class Chunk:
    def __init__(self, id: int, content: str, tokens: int, input_id: int):
        self.id = id
        self.content = content
        self.tokens = tokens
        self.input_id = input_id
        self.filename = None

    def __str__(self) -> str:
        return f"Chunk(content={self.content}, tokens={self.tokens}, input_id={self.input_id})"

    def set_filename_from_list(self, filenames: list[str]) -> str:
        self.filename = filenames[self.input_id]
        return self.filename

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "tokens": self.tokens,
            "input_id": self.input_id,
        }
