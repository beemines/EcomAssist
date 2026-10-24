"""Validation-only calibration and fixed17-column multilabel measurement."""
from typing import Literal
import json
import numpy as np
from pydantic import Field,model_validator
from sklearn.metrics import multilabel_confusion_matrix,f1_score,accuracy_score,hamming_loss
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import StrictRecord
from app.topics.manifest import DECODER_VERSION

GRID=tuple(round(.1+.05*i,2) for i in range(17))


class ClassMetrics(StrictRecord):
    label:str
    support:int
    negative_support:int
    precision:float
    recall:float
    f1:float
    confusion:tuple[tuple[int,int],tuple[int,int]]
    undefined_denominators:tuple[str,...]


class EvaluationReport(StrictRecord):
    sample_count:int
    taxonomy_hash:str
    per_class:tuple[ClassMetrics,...]
    macro_f1:float
    micro_f1:float
    exact_match:float
    hamming_loss:float
    needs_review_rate:float


class ThresholdClass(StrictRecord):
    label:str
    threshold:float=Field(ge=.1,le=.9)
    positive_support:int
    negative_support:int
    validation_f1:float=Field(ge=0,le=1)
    calibrated:bool
    reason:str|None


class ThresholdSet(StrictRecord):
    split:Literal['validation']
    taxonomy_hash:str
    validation_arrays_hash:str
    per_class:tuple[ThresholdClass,...]
    threshold_hash:str

    @property
    def thresholds(self):return tuple(row.threshold for row in self.per_class)

    @model_validator(mode='after')
    def identity(self):
        fields=self.model_dump(mode='json');fields.pop('threshold_hash')
        if (self.taxonomy_hash!=default_taxonomy().digest or len(self.per_class)!=17
                or tuple(row.label for row in self.per_class)!=default_taxonomy().ordered_names
                or self.threshold_hash!=digest(fields)):
            raise ValueError('Threshold identity or taxonomy changed')
        return self


def _matrix(value,*,binary=False):
    result=np.asarray(value)
    if (result.ndim!=2 or result.shape[1]!=17 or len(result)==0 or result.dtype.kind not in 'biuf'
            or not np.isfinite(result).all() or binary and not np.isin(result,[0,1]).all()):
        raise ValueError('Expected nonempty finite17-column numeric matrix'+(' with binary values' if binary else ''))
    return result.astype(np.int64 if binary else np.float64)


def decode_logits(logits,thresholds):
    values=_matrix(logits)
    limits=np.asarray(thresholds)
    if limits.shape!=(17,) or limits.dtype.kind not in 'iuf' or not np.isfinite(limits).all() or not ((limits>0)&(limits<1)).all():
        raise ValueError('Expected17 finite thresholds strictly between zero and one')
    # Algebraically sigmoid(logit)>=threshold, avoiding overflow and boundary rounding.
    prediction=values>=np.log(limits/(1-limits))
    prediction[:,-1]&=~prediction[:,:-1].any(axis=1)
    return prediction


def select_thresholds(logits,y_true,*,split:str) -> ThresholdSet:
    if split!='validation':raise ValueError('Only the frozen validation split may select thresholds')
    values=_matrix(logits);truth=_matrix(y_true,binary=True)
    if values.shape!=truth.shape:raise ValueError('Logit and truth shapes differ')
    names=default_taxonomy().ordered_names;rows=[]
    for index,label in enumerate(names):
        positive=int(truth[:,index].sum());negative=len(truth)-positive
        calibrated=min(positive,negative)>=10
        candidates=GRID if calibrated else (.5,)
        scores={threshold:float(f1_score(truth[:,index],values[:,index]>=np.log(threshold/(1-threshold)),zero_division=0))
            for threshold in candidates}
        threshold=min(candidates,key=lambda threshold:(-scores[threshold],round(abs(threshold-.5),10),-threshold))
        rows.append(ThresholdClass(label=label,threshold=threshold,positive_support=positive,negative_support=negative,
            validation_f1=scores[threshold],calibrated=calibrated,reason=None if calibrated else '正例或负例少于10条'))
    fields=dict(split=split,taxonomy_hash=default_taxonomy().digest,
        validation_arrays_hash=digest(dict(logits=values.tolist(),truth=truth.tolist())),
        per_class=[row.model_dump(mode='json') for row in rows])
    return ThresholdSet.model_validate_json(json.dumps(fields|dict(threshold_hash=digest(fields))))


def evaluate_multilabel(y_true,predictions,*,taxonomy) -> EvaluationReport:
    if taxonomy.digest!=default_taxonomy().digest:raise ValueError('The sole authoritative17-label taxonomy is required')
    truth=_matrix(y_true,binary=True);predicted=_matrix(predictions,binary=True)
    if truth.shape!=predicted.shape:raise ValueError('Prediction and truth shapes differ')
    matrices=multilabel_confusion_matrix(truth,predicted,labels=list(range(17)))
    rows=[]
    for label,matrix in zip(taxonomy.ordered_names,matrices,strict=True):
        tn,fp,fn,tp=(int(x) for x in matrix.ravel());undefined=[]
        if tp+fp==0:undefined.append('没有预测正例，精确率分母为0')
        if tp+fn==0:undefined.append('没有真实正例，召回率分母为0')
        if 2*tp+fp+fn==0:undefined.append('没有真实或预测正例，F1分母为0')
        rows.append(ClassMetrics(label=label,support=tp+fn,negative_support=tn+fp,
            precision=tp/(tp+fp) if tp+fp else 0.,recall=tp/(tp+fn) if tp+fn else 0.,
            f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.,confusion=((tn,fp),(fn,tp)),
            undefined_denominators=tuple(undefined)))
    return EvaluationReport(sample_count=len(truth),taxonomy_hash=taxonomy.digest,per_class=tuple(rows),
        macro_f1=float(f1_score(truth,predicted,average='macro',zero_division=0)),
        micro_f1=float(f1_score(truth,predicted,average='micro',zero_division=0)),
        exact_match=float(accuracy_score(truth,predicted)),hamming_loss=float(hamming_loss(truth,predicted)),
        needs_review_rate=float((~predicted.any(axis=1)).mean()))
