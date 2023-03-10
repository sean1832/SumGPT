import numpy as np
from typing import Any, Dict, List, Tuple, Union
from GPT.embeddings import openAIEmbeddings
import streamlit as st
import re
import GPT


def similarity(v1, v2) -> np.ndarray:
    """Returns the cosine similarity between two vectors."""
    return np.dot(v1, v2)


def _chunk_spliter(content: str, chunk_size: int = 1000) -> List[str]:
    """Splits a string into chunks of a given size."""

    sentences = re.split(r'(?<=[.?!])\s+', content)
    chunks = []
    chunk = ''
    word_count = 0
    for sentence in sentences:
        sentence += ' '  # add space at end to compensate for split
        words = sentence.split()
        sentence_word_count = len(words)
        if word_count + sentence_word_count <= chunk_size:
            chunk += sentence
            word_count += sentence_word_count
        else:
            chunks.append(chunk.strip())
            chunk = sentence
            word_count = sentence_word_count
    if chunk:
        chunks.append(chunk.strip())
    return chunks


def convert_to_chunks(content: str, chunk_size: int = 1000, enable_embedding: bool = False) -> List[Dict[str, float]]:
    """Converts a string into chunks of a given size."""
    chunks_text = _chunk_spliter(content, chunk_size)
    chunks = []
    for i, chunk in enumerate(chunks_text):
        if enable_embedding:
            embedding = openAIEmbeddings(st.session_state["OPENAI_API_KEY"])
            chunks.append({'content': chunk, 'vector': embedding.embedding(chunk)})
        else:
            chunks.append({'content': chunk, 'vector': None})
    return chunks


def search_chunks(query: str, chunks: List[Dict[str, float]], count: int = 1) -> List[Dict[str, np.ndarray]]:
    """Returns the top `count` chunks that are most similar to the query."""
    embedding = openAIEmbeddings(st.session_state["OPENAI_API_KEY"])
    vectors = embedding.embedding(query)
    points = []

    for chunk in chunks:
        point = similarity(vectors, chunk['vector'])
        points.append({'content': chunk['content'], 'point': point})

    # sort the points in descending order
    ordered = sorted(points, key=lambda x: x['point'], reverse=True)
    return ordered[0:count]


def recursive_summarize(chunks: List[Dict[str, float]]) -> Tuple[List[str], str]:
    """Returns a recursive summary of the given content."""
    recursiveSumTexts = []
    finish_reason = ''
    chunks_length = len(chunks)
    count = 0
    progress_bar = st.progress(0)
    for chunk in chunks:
        content = chunk['content']
        text, finish_reason = GPT.generate.get_answer(content, recursive=True)
        recursiveSumTexts.append(text)
        progress_bar.progress((count + 1) / chunks_length)
        count += 1
    return recursiveSumTexts, finish_reason


def summarize(recursive_sum: List[str]) -> Tuple[str, str]:
    """Returns a summary of the given content."""
    join_sum = ' '.join(recursive_sum)
    answer, finish_reason = GPT.generate.get_answer(join_sum, recursive=False)
    return answer, finish_reason

