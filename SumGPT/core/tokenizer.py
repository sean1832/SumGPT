from typing import List

import tiktoken


class Tokenizer:
    def __init__(self, model: str):
        self.tokenizer = tiktoken.encoding_for_model(model)

    def tokenize(self, text: str) -> List[int]:
        return self.tokenizer.encode(text)

    def detokenize(self, tokens: List[int]) -> str:
        return self.tokenizer.decode(tokens)

    def detokenize_single(self, tokens: List[int]) -> List[str]:
        results = []
        for token in tokens:
            results.append(self.tokenizer.decode_single_token_bytes(token).decode("utf-8"))
        return results
