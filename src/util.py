import numpy as np
from typing import Any, Dict, List, Tuple, Union
from GPT.embeddings import openAIEmbeddings
import streamlit as st
import re
import GPT
import textwrap
from langdetect import detect
import time
from pytube import YouTube
import xml.etree.ElementTree as ET
from datetime import datetime


def _extract_xml_caption(xml: str) -> str:
    """Extracts the text content from the <s> elements of an XML string."""
    root = ET.fromstring(xml)
    text_content = ''
    for child in root.iter('s'):
        text_content += child.text
    return text_content.strip()


def _get_caption(url: str, lang_code: str = 'a.en') -> str:
    """Extracts the transcript from a YouTube video."""
    yt = YouTube(url)
    try:
        caption = yt.captions[lang_code]
        xml_caption = caption.xml_captions
        caption_string = _extract_xml_caption(xml_caption)
    except KeyError:
        st.error('❌ No captions found for this video.')
        caption_string = ''

    return caption_string


def _similarity(v1, v2) -> np.ndarray:
    """Returns the cosine similarity between two vectors."""
    return np.dot(v1, v2)


def _chunk_spliter(content: str, chunk_size: int = 1000, lang_base: str = 'latin') -> List[str]:
    """Splits a string into chunks of a given size."""

    sentences = re.split(r'(?<=[.?!,。，、！？·])\s+', content)
    if lang_base == 'latin':
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
        # add the last chunk
        if chunk:
            chunks.append(chunk.strip())

        new_chunks = []
        for c in chunks:
            if c == '':
                continue
            if len(c.split()) > chunk_size + 25:
                words = c.split()
                small_chunks = []
                for i in range(0, len(words), chunk_size):
                    small_chunks.append(' '.join(words[i:i + chunk_size]))
                new_chunks.extend(small_chunks)
            else:
                new_chunks.append(c)
        return new_chunks

    else:
        chunks = textwrap.wrap(content, width=chunk_size)
        return chunks


def language_base(string: str) -> str:
    try:
        lang_code = detect(string)
        latin_based = ['en', 'fr-ca', 'es']
        east_asian_based = ['zh', 'ja', 'ko']
        for lang in latin_based:
            if lang_code.startswith(lang):
                return 'latin'
        for lang in east_asian_based:
            if lang_code.startswith(lang):
                return 'east_asian'
        return 'other'
    except KeyError:
        return 'other'


def extract_youtube_transcript(url: str, lang_code: str = 'a.en') -> Tuple[str, str]:
    """Extracts the transcript from a YouTube video."""

    youtube = YouTube(url)
    title = youtube.title
    transcript = _get_caption(url, lang_code)
    return transcript, title


def convert_to_chunks(content: str, chunk_size: int = 1000, enable_embedding: bool = False) -> List[Dict[str, float]]:
    """Converts a string into chunks of a given size."""
    chunks_text = _chunk_spliter(content, chunk_size, language_base(content))
    chunks = []
    for i, chunk in enumerate(chunks_text):
        if enable_embedding:
            embedding = openAIEmbeddings(st.session_state["OPENAI_API_KEY"])
            chunks.append({'content': chunk, 'vector': embedding.embedding(chunk)})
        else:
            chunks.append({'content': chunk, 'language_based': language_base(chunk)})
    return chunks


def search_chunks(query: str, chunks: List[Dict[str, float]], count: int = 1) -> List[Dict[str, np.ndarray]]:
    """Returns the top `count` chunks that are most similar to the query."""
    embedding = openAIEmbeddings(st.session_state["OPENAI_API_KEY"])
    vectors = embedding.embedding(query)
    points = []

    for chunk in chunks:
        point = _similarity(vectors, chunk['vector'])
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
        text, finish_reason = GPT.generate.get_answer(content, recursive=True,
                                                      persona=st.session_state['OPENAI_PERSONA_REC'])
        recursiveSumTexts.append(text)
        progress_bar.progress((count + 1) / chunks_length)
        count += 1
        time.sleep(st.session_state['DELAY'])

    return recursiveSumTexts, finish_reason


def summarize(recursive_sum: List[str]) -> Tuple[str, str]:
    """Returns a summary of the given content."""
    join_sum = ' '.join(recursive_sum)
    answer, finish_reason = GPT.generate.get_answer(join_sum, recursive=False,
                                                    persona=st.session_state['OPENAI_PERSONA_SUM'])
    return answer, finish_reason


def download_results(rec_responses, final_response):
    """Downloads the results as a txt file."""
    joint_rec_response = f"=====recursive responses=====\n\n" + '\n\n'.join(rec_responses)
    joint_final_response = f"{joint_rec_response}\n\n======final response=====\n\n{final_response}"
    now = datetime.now()
    if final_response is not None:
        st.download_button("📥 Download Summary",
                           joint_final_response,
                           file_name=f"summary_{now.strftime('%Y-%m-%d_%H-%M')}.txt")
    else:
        st.download_button("📥 Download Summary",
                           joint_rec_response,
                           file_name=f"summary_{now.strftime('%Y-%m-%d_%H-%M')}.txt")
