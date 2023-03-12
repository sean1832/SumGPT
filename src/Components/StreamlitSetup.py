import streamlit as st


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
