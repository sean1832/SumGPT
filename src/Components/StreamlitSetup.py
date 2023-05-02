import streamlit as st
import Data.caption_languages as data
import Modules.file_io as file_io

def setup():
    st.set_page_config(page_title="SumGPT", page_icon="📝", layout="wide")

    if not st.session_state.get('OPENAI_API_KEY'):
        st.session_state['OPENAI_API_KEY'] = None

    if not st.session_state.get('OPENAI_PERSONA_REC'):
        st.session_state['OPENAI_PERSONA_REC'] = None

    if not st.session_state.get('OPENAI_PERSONA_SUM'):
        st.session_state['OPENAI_PERSONA_SUM'] = None

    if not st.session_state.get('CHUNK_SIZE'):
        st.session_state['CHUNK_SIZE'] = None

    if not st.session_state.get('OPENAI_PARAMS'):
        st.session_state['OPENAI_PARAMS'] = None

    if not st.session_state.get('DELAY'):
        st.session_state['DELAY'] = 0

    if not st.session_state.get('FINAL_SUMMARY_MODE'):
        st.session_state['FINAL_SUMMARY_MODE'] = False

    if not st.session_state.get('CAPTION_LANGUAGES'):
        st.session_state['CAPTION_LANGUAGES'] = data.languages + data.auto_languages

    if not st.session_state.get('PREVIOUS_RESULTS'):
        st.session_state['PREVIOUS_RESULTS'] = None

    if not st.session_state.get('MANIFEST'):
        st.session_state["MANIFEST"] = file_io.read_json("src/manifest.json")