from datamodel.llm_params import LLMParams
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic.types import SecretStr


class LLM:
    def __init__(self, api_key: str, gpt_params: LLMParams):
        self.api_key: str = api_key
        self.llm_params: LLMParams = gpt_params
        self.model: ChatOpenAI = self._set_llm()

    def _set_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=SecretStr(self.api_key),
            model=self.llm_params.model.name,
            max_tokens=self.llm_params.max_tokens,
            temperature=self.llm_params.temperature,
        )

    def generate(_self, prompt: str, system: str = "") -> BaseMessage:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]
        return _self.model.invoke(messages)

    async def agenerate(_self, prompt: str, system: str = "") -> BaseMessage:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]
        return await _self.model.ainvoke(messages)

    def Calc_price(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        scale_factor: int = 1000000,
    ) -> float:
        pricing = self.llm_params.model.pricing
        if cached_tokens != 0 and pricing.cached is not None:
            input_tokens -= cached_tokens
            return (
                input_tokens * pricing.input
                + output_tokens * pricing.output
                + cached_tokens * pricing.cached
            ) / scale_factor

        return (input_tokens * pricing.input + output_tokens * pricing.output) / scale_factor
