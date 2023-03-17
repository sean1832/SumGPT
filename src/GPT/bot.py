import openai
from typing import Any, Dict, List, Tuple, Union


class OpenAIChatBot:
    """A class to interact with the OpenAI API."""

    def __init__(self, api_key: str, persona: str, model: str, max_tokens: int, temperature: float, top_p: float,
                 frequency_penalty: float, presence_penalty: float):
        openai.api_key = api_key
        self.persona = persona
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def chat_stream(self, prompt: str) -> openai.api_resources.chat_completion.ChatCompletion:
        """Returns the streamed response from the OpenAI API."""
        completions = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stream=True,
            messages=[
                {"role": "system", "content": self.persona},
                {"role": "user", "content": prompt}
            ])
        return completions

    def chat(self, prompt: str) -> Tuple[str, str]:
        """Returns the response from the OpenAI API."""
        completions = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            messages=[
                {"role": "system", "content": self.persona},
                {"role": "user", "content": f"{self.persona} '{prompt}'"}
            ])
        return completions['choices'][0]['message']['content'], completions['choices'][0]['finish_reason']
