"""One approved, train-only short-input sampling control; never an inference rule."""
import random

import torch
from transformers import Trainer

from app.topics.reviews import digest
from ml.topic_classifier.data import SEED

PROFILE='short30-v1'


class ShortQuotaSampler(torch.utils.data.Sampler):
    """Keep epoch length fixed and balance repeats within each length stratum."""
    def __init__(self,rows,*,seed=SEED):
        if type(seed) is not int or seed!=SEED:
            raise ValueError('The approved sampling seed is fixed')
        rows=tuple(rows)
        self.short=tuple(i for i,row in enumerate(rows) if 4<=len(row.text)<=16)
        short_set=set(self.short)
        self.long=tuple(i for i in range(len(rows)) if i not in short_set)
        self.size=len(rows);self.seed=seed;self.epoch=0
        self.short_quota=(3*self.size+5)//10
        if not self.short or not self.long or not 0<self.short_quota<self.size:
            raise ValueError('Both nonempty length strata are required for the local control')

    def __len__(self):return self.size

    def set_epoch(self,epoch):
        if type(epoch) is not int or epoch<0:
            raise ValueError('Sampling epoch must be a nonnegative integer')
        self.epoch=epoch

    def __iter__(self):
        rng=random.Random(self.seed+self.epoch)
        def draw(pool,count):
            selected=[]
            while len(selected)<count:
                order=list(pool);rng.shuffle(order)
                selected.extend(order[:count-len(selected)])
            return selected
        result=draw(self.short,self.short_quota)+draw(self.long,self.size-self.short_quota)
        rng.shuffle(result)
        return iter(result)


def sampling_record(rows):
    """Bind the exact eight reproducible epoch streams, without accessing labels."""
    rows=tuple(rows);sampler=ShortQuotaSampler(rows);streams=[]
    for epoch in range(8):
        sampler.set_epoch(epoch)
        streams.append(digest(list(sampler)))
    fields=dict(profile=PROFILE,seed=SEED,short_min=4,short_max=16,target_fraction=.3,
        total_samples=len(rows),short_pool=len(sampler.short),long_pool=len(sampler.long),
        short_per_epoch=sampler.short_quota,long_per_epoch=len(rows)-sampler.short_quota,
        source_order_hash=digest([(row.id,row.text) for row in rows]),epoch_index_hashes=streams)
    return fields|dict(sampling_hash=digest(fields))


class ShortSamplingTrainer(Trainer):
    def _get_train_sampler(self,train_dataset=None):
        from ml.topic_classifier.train import EncodedSamples
        dataset=self.train_dataset if train_dataset is None else train_dataset
        if not isinstance(dataset,EncodedSamples):
            raise ValueError('The control only accepts frozen encoded training samples')
        if self.args.world_size!=1 or self.args.seed!=SEED or self.args.data_seed!=SEED:
            raise ValueError('The approved local control uses one process and the fixed seed')
        return ShortQuotaSampler(dataset.rows)
