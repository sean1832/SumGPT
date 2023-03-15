
class gpt_param:
    def __init__(self, model: str, max_tokens_final: int, max_tokens_rec: int, temperature: float, top_p: float,
                 frequency_penalty: float, presence_penalty: float):
        self.model = model
        self.max_tokens_rec = max_tokens_rec
        self.max_tokens_final = max_tokens_final
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
