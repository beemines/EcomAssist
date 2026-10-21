"""Borrow Ch04's physical ownership/cleanup protocol with the one Ch09 call cap."""
from app.rag_evaluation.resources import OwnedResources
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.retrieval.rerank import SiliconFlowReranker


class CalibrationResources(OwnedResources):
    def __init__(self, *args, cap=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap = cap

    def _provider_http(self, stage):
        counter = self.requests.fixed_hook(stage)
        async def hook(request):
            if self.cap is not None:
                self.cap.reserve(stage)
            await counter(request)
        return self._http(hook)

    def _models(self):
        # Calibration has no generator, classifier, self-check, judge or planner.
        self.embedder = SiliconFlowEmbedder(self.settings, http_client=self._provider_http('embedding'))
        self.reranker = SiliconFlowReranker(self.settings, http_client=self._provider_http('rerank'))
