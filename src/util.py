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


def _is_auto_lang(lang_code: str) -> bool:
    """Checks if the language code is an auto language."""
    return lang_code.startswith('a.')


def _extract_xml_caption(xml: str, is_auto_lang: bool) -> str:
    """Extracts the text content from the <s> elements of an XML string."""
    root = ET.fromstring(xml)
    text_content = ''
    if is_auto_lang:
        for child in root.iter('s'):
            text_content += child.text
    else:
        text = ''
        for p in root.findall('.//p'):
            text += p.text + ' '
        text_content = text
    return text_content.strip()


def _get_caption(url: str, lang_code: str | List[str] = 'a.en') -> str:
    """Extracts the transcript from a YouTube video."""
    yt = YouTube(url)
    caption = None
    selected_lang = None
    if not isinstance(lang_code, list):
        lang_code = [lang_code]
    for lang in lang_code:
        try:
            caption = yt.captions[lang]
            selected_lang = lang
        except KeyError:
            continue  # try next language

    if caption is None:
        yt_captions = yt.captions
        if yt_captions is not None:
            st.error(f'❌ Caption language currently not supported.\n\n'
                     f'{yt_captions}')
        else:
            st.error(f'❌ No captions found in this video. Please try another one.')
        st.stop()

    else:
        xml_caption = caption.xml_captions
        caption_string = _extract_xml_caption(xml_caption, _is_auto_lang(selected_lang))

        # check if caption parsing failed
        if xml_caption is not None and caption_string == '':
            st.error(f'❌ Caption parsing failed. [ url: {url}, lang: {selected_lang} ]\n\n'
                     f'Please [report this issue on Here](https://github.com/sean1832/SumGPT/issues). '
                     f'Make sure to copy this error message and include it in your issue.')
            st.stop()

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


@st.cache_data(show_spinner=False)
def extract_youtube_transcript(url: str, lang_code: str | List[str] = 'a.en') -> Tuple[str, str]:
    """Extracts the transcript from a YouTube video."""

    youtube = YouTube(url)
    time.sleep(0.3)
    title = youtube.title
    transcript = _get_caption(url, lang_code)
    return transcript, title


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
def recursive_summarize(chunks: List[Dict[str, Union[str, float]]], max_tokens) -> Tuple[List[str], str]:
    """Returns a recursive summary of the given content."""
    recursiveSumTexts = []
    finish_reason = ''
    chunks_length = len(chunks)
    count = 0
    progress_bar = st.progress(0)
    for chunk in chunks:
        content = chunk['content']
        text, finish_reason = GPT.generate.get_answer(content,
                                                      max_tokens=max_tokens,
                                                      persona=st.session_state['OPENAI_PERSONA_REC'])
        recursiveSumTexts.append(text)
        progress_bar.progress((count + 1) / chunks_length)
        count += 1
        time.sleep(st.session_state['DELAY'])

    return recursiveSumTexts, finish_reason


@st.cache_data(show_spinner=False)
def summarize(message: List[str] | str) -> Tuple[str, str]:
    """Returns a summary of the given content."""
    if isinstance(message, list):
        join_msg = ' '.join(message)
    else:
        join_msg = message

    params = st.session_state['OPENAI_PARAMS']
    max_asw_tokens_final = params.max_tokens_final

    answer, finish_reason = GPT.generate.get_answer(join_msg, max_tokens=max_asw_tokens_final,
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
                           file_name=f"summary_{now.strftime('%Y-%m-%d_%H-%M')}.md")
    else:
        st.download_button("📥 Download Summary",
                           joint_rec_response,
                           file_name=f"summary_{now.strftime('%Y-%m-%d_%H-%M')}.md")


def exceeded_token_handler(param, chunks) -> bool:
    """Handles the case where the user has exceeded the number of tokens."""
    if param.model == 'gpt-4':
        max_token = 8100
    else:
        max_token = 4096
    info = GPT.misc.is_tokens_exceeded(param, chunks, max_token)
    if info['exceeded']:
        st.error(f"❌ {info['message']}")
        return True
    else:
        return False
