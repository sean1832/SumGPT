import streamlit as st
import GPT


def set_openai_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key


def set_openai_persona(persona: str):
    st.session_state["OPENAI_PERSONA"] = persona


def set_param(params: GPT.param):
    st.session_state["OPENAI_PARAMS"] = params


def set_chunk_size(size: int):
    st.session_state['CHUNK_SIZE'] = size


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

        persona = st.text_area('🤖 Bot Persona',
                               value='You are a comprehensive summarizer that summarise large chunk of text '
                                     'into detailed paragraphs with perfect english while making sure all '
                                     'the key points are included.',
                               help='System message is a pre-defined message used to instruct the assistant at the '
                                    'beginning of a conversation. iterating and '
                                    'experimenting with potential improvements can help to generate better outputs.',
                               height=120)

        with st.expander('🔥 Advanced Options'):
            chunk_size = st.slider('Chunk Size (word count)', min_value=0, max_value=2500, value=800, step=20)
            max_tokens_single = st.slider('Max Tokens Summary', min_value=0, max_value=4090, value=650, step=20)
            max_tokens_rec = st.slider('Max Tokens Chunks', min_value=0, max_value=4090, value=250, step=20)
            temperature = st.slider('Temperature', min_value=0.0, max_value=1.0, step=0.05, value=0.7)
            top_p = st.slider('Top P', min_value=0.0, max_value=1.0, step=0.05, value=1.0)
            frequency_penalty = st.slider('Frequency Penalty', min_value=0.0, max_value=2.0, step=0.1)
            presence_penalty = st.slider('Presence Penalty', min_value=0.0, max_value=2.0, step=0.1)
            model = st.selectbox("Model", options=['gpt-3.5-turbo', 'gpt-3.5-turbo-0301'])
            param = GPT.param.gpt_param(
                model=model,
                max_tokens_single=max_tokens_single,
                max_tokens_rec=max_tokens_rec,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

        if api_input:
            set_openai_api_key(api_input)

        if persona:
            set_openai_persona(persona)

        set_chunk_size(chunk_size)
        set_param(param)
