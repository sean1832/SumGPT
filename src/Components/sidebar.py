import streamlit as st
import GPT
from streamlit_toggle import st_toggle_switch
import Components


def set_openai_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key


def set_openai_persona(persona_rec: str, persona_sum: str):
    st.session_state["OPENAI_PERSONA_REC"] = persona_rec
    st.session_state["OPENAI_PERSONA_SUM"] = persona_sum


def set_param(params: GPT.param):
    st.session_state["OPENAI_PARAMS"] = params


def set_chunk_size(size: int):
    st.session_state['CHUNK_SIZE'] = size


def set_delay(time: int):
    st.session_state['DELAY'] = time


def set_final_summary_mode(mode: bool):
    st.session_state['FINAL_SUMMARY_MODE'] = mode


def sidebar():
    with st.sidebar:
        st.markdown("## How to use\n"
                    "1. 🔑 Enter your [OpenAI API key](https://beta.openai.com/account/api-keys)\n"
                    "2. 📁 upload your files (multiple files accepted)\n"
                    "3. 🏃 Run\n"
                    "---")

        api_input = st.text_input(label="🔑 OpenAI API Key",
                                  placeholder="Enter your OpenAI API key (sk-...)",
                                  type="password",
                                  help="You can get your API key from https://beta.openai.com/account/api-keys")

        enable_final_summary = st_toggle_switch(label="Enable Final Summary", default_value=False)
        if enable_final_summary:
            set_final_summary_mode(True)
        if st.session_state['FINAL_SUMMARY_MODE'] != enable_final_summary:
            set_final_summary_mode(enable_final_summary)

        with st.expander('🤖 Bot Persona'):
            persona_rec = st.text_area('Bot Persona Recursive',
                                       value='Summarize following content in a detail '
                                             'and comprehensive way in perfect english with no grammar issue while '
                                             'making sure all the key points are included.',
                                       help='System message is a pre-defined message used to instruct the assistant at the '
                                            'beginning of a conversation. iterating and '
                                            'experimenting with potential improvements can help to generate better outputs.'
                                            'Make sure to use casual language.',
                                       height=140)
            if enable_final_summary:
                persona_sum = st.text_area('Bot Persona Total Sum',
                                           value='Provide detail explanation and summary of the '
                                                 'following large chunk of text into comprehensive and cohesive '
                                                 'paragraphs of article with perfect english while making sure all the key points '
                                                 'are included. Make sure that the text can read fluently and make sense.',
                                           help='This is a pre-defined message for total summarization that is used to'
                                                'instruct the assistant at the beginning of a conversation. ',
                                           height=140)
            else:
                persona_sum = ""

        with st.expander('🔥 Advanced Options'):
            chunk_size = st.slider('Chunk Size (word count)', min_value=0, max_value=2500, value=800, step=20)
            max_tokens_single = st.slider('Max Tokens Summary', min_value=0, max_value=4090, value=650, step=20)
            max_tokens_rec = st.slider('Max Tokens Chunks', min_value=0, max_value=4090, value=250, step=20)
            temperature = st.slider('Temperature', min_value=0.0, max_value=1.0, step=0.05, value=0.7)
            top_p = st.slider('Top P', min_value=0.0, max_value=1.0, step=0.05, value=1.0)
            frequency_penalty = st.slider('Frequency Penalty', min_value=0.0, max_value=2.0, step=0.1)
            presence_penalty = st.slider('Presence Penalty', min_value=0.0, max_value=2.0, step=0.1)
            model = st.selectbox("Model", options=['gpt-3.5-turbo', 'gpt-3.5-turbo-0301'])
            if st_toggle_switch(label="Delay (free openAI API user)", default_value=False):
                delay = st.slider('Delay (seconds)', min_value=0, max_value=5, value=1, step=1)
            else:
                delay = 0
            param = GPT.param.gpt_param(
                model=model,
                max_tokens_single=max_tokens_single,
                max_tokens_rec=max_tokens_rec,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

        Components.Info.info()

        if api_input:
            set_openai_api_key(api_input)

        if persona_rec:
            set_openai_persona(persona_rec, persona_sum)

        set_chunk_size(chunk_size)
        set_param(param)
        set_delay(delay)
