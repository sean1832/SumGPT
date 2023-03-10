import openai


class openAIEmbeddings:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def embedding(self, content: str, engine: str = 'text-embedding-ada-002') -> float:
        """Returns the embedding vector of a string."""
        response = openai.Embedding.create(input=content, engine=engine)
        vector = response['data'][0]['embedding']
        return vector
