import re
import PyPDF4
import docx
from typing import Any, Dict, List, Tuple, Union
from pydub import AudioSegment
import math
import json
import streamlit as st



@st.cache_data()
def read_json(file, key: str = None) -> Any:
    """Reads a json file and returns the value of a key."""
    with open(file, "r") as f:
        data = json.load(f)
        if key and isinstance(data, dict):
            return data[key]
        elif key and isinstance(data, list):
            return [d[key] for d in data]
        else:
            return data


@st.cache_data()
def read_json_upload(file, key: str) -> Any:
    """Reads a json file and returns the value of a key."""
    if not isinstance(file, str):
        f = file.getvalue().decode("utf-8")
        data = json.loads(f)
        return data[key]


@st.cache_data()
def read_txt(file, encoding: str = "utf-8") -> str:
    """Reads a text file."""
    return file.read().decode(encoding)


@st.cache_data()
def read_pdf(file) -> List[str]:
    """Reads a pdf file."""
    pdfReader = PyPDF4.PdfFileReader(file, strict=False)
    texts = []
    for page in range(pdfReader.numPages):
        text = pdfReader.getPage(page).extractText()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        texts.append(text)
    return texts


@st.cache_data()
def read_docx(file) -> str:
    """Reads a docx file."""
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        # Remove multiple newlines
        t = re.sub(r"\n\s*\n", "\n\n", para.text)
        text += t + "\n"
    return text


@st.cache_data()
def _split_audio(audio, chunk_size=2) -> List[AudioSegment]:
    """Split audio into chunks of 10 minutes."""
    # load audio
    audio = AudioSegment.from_file(audio, format="mp3")
    # Define the chunk size (10 minutes default)
    chunk_size = chunk_size * 60 * 1000
    # calculate the number of chunks
    num_chunks = math.ceil(len(audio) / chunk_size)
    chunks = []
    # split audio into chunks
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = audio[start:end]
        chunks.append(chunk)
    return chunks


@st.cache_data()
def read(file) -> str | List[str]:
    """Reads a file and returns the content."""
    if file.name.endswith(".txt") or file.name.endswith(".md"):
        return read_txt(file)
    elif file.name.endswith(".pdf"):
        return read_pdf(file)
    elif file.name.endswith(".docx"):
        return read_docx(file)
    else:
        raise ValueError("File type not supported")
