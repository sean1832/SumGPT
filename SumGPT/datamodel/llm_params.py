from datamodel.llm_model import LLMModel, LLMModelPricing  # noqa: F401


class LLMParams:
    def __init__(
        self,
        model: LLMModel,
        max_tokens=2048,
        temperature=0.7,
    ):
        self.model: LLMModel = model
        self.max_tokens: int = max_tokens
        self.temperature: float = temperature
