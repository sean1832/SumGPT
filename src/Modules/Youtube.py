import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import streamlit as st
from typing import Any, Dict, List, Tuple, Union


manifest = st.session_state["MANIFEST"]
def _error_report_msg(youtube_url):
    return f"Please create an issue on [GitHub]({manifest['bugs']['url']}). " \
           f"Please include the YouTube URL ({youtube_url}), version number ({manifest['version']}) " \
           f"and all necessary information to replicate the error. " \
           f"**Before creating a new issue, please check if the problem has already been reported.**"

def _extract_video_id_from_url(url):
    video_id_pattern = r'(?:v=|/v/|youtu\.be/|/embed/|/e/)([^?&"\'>]+)'
    match = re.search(video_id_pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def get_video_title(youtube_url):
    video_id = _extract_video_id_from_url(youtube_url)
    url = f'https://www.youtube.com/watch?v={video_id}'
    response = requests.get(url)
    title_pattern = r'<title>(.+?) - YouTube<\/title>'
    match = re.search(title_pattern, response.text)
    if match:
        title = match.group(1)
        return title
    else:
        return None

def get_available_subtitle_languages(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = [transcript.language_code for transcript in transcript_list]
        return languages
    except Exception as e:
        print(f"Error fetching available subtitle languages: {e}")
        return []

def get_video_captions(youtube_url, languages):
    video_id = _extract_video_id_from_url(youtube_url)
    simplified_url = f'https://www.youtube.com/watch?v={video_id}'

    available_language = get_available_subtitle_languages(video_id)

    if not any(lang in languages for lang in available_language) and available_language != []:
        print(f"Failed to retrieve transcript: Language {available_language} is/are not yet supported for {simplified_url}.")
        st.error(f'❌ Language {available_language} is/are not yet supported for {simplified_url}.\n\n' + _error_report_msg(simplified_url))
        st.stop()

    for language in languages:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            captions = ""
            for item in transcript:
                captions += item['text'] + "\n"
            return captions

        except NoTranscriptFound as e:
            if language == languages[-1]:
                print(f"Language {available_language} exist in language list but failed to retrieve in YouTubeTranscriptApi.get_transcript: {e}")
                st.error(f'❌ Language {available_language} exist in language list but failed to retrieve in `YouTubeTranscriptApi.get_transcript`:\n\n'
                         f'languages = {available_language}\n\n'
                         f'language list = {languages}\n\n'
                         + _error_report_msg(simplified_url))
                st.stop()
            else:
                continue

        except TranscriptsDisabled:
            print(f"Failed to retrieve transcript: transcripts disabled for {simplified_url}")
            st.error(f'❌ Subtitles not available for {simplified_url}! \n\n---'
                     f'\n**Instruction:**\n\n'
                     f'1. Verify if the [video]({simplified_url}) has subtitles available.\n\n'
                     f"2. If you are confident that subtitles are available in the video but could not be retrieved, "
                     + _error_report_msg(simplified_url))
            st.stop()
            raise TranscriptsDisabled

        except Exception as e:
            print(e)
            st.error(f'❌ Failed to fetch data from YouTube for {simplified_url}. \n\n'
                     f'{_error_report_msg(simplified_url)}'
                     f'\n\nError: \n\n---\n\n{e}')
            st.stop()
            break

@st.cache_data(show_spinner=False)
def extract_youtube_transcript(url: str, lang_code: str | List[str] = 'a.en') -> Tuple[str, str]:
    """Extracts the transcript from a YouTube video."""
    transcript = get_video_captions(url, lang_code)
    title = get_video_title(url)
    return transcript, title
