from typing import Optional


class LLMModelPricing:
    def __init__(self, input: int, output: int, cached: Optional[int] = None):
        self.input = input
        self.output = output
        self.cached = cached


class LLMModel:
    def __init__(
        self, name: str, context_window: int, max_output_tokens: int, pricing: LLMModelPricing
    ):
        self.name = name
        self.context_window = context_window
        self.max_output_tokens = max_output_tokens
        self.pricing = pricing

    @staticmethod
    def construct_from_dict(data: dict) -> "LLMModel":
        pricing = LLMModelPricing(data["pricing"]["input"], data["pricing"]["output"])
        if "cached" in data["pricing"]:
            pricing.cached = data["pricing"]["cached"]

        return LLMModel(
            name=data["model"],
            context_window=data["context_window"],
            max_output_tokens=data["max_output_tokens"],
            pricing=pricing,
        )
