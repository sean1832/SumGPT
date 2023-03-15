import openai
from langchain.llms import OpenAI
import os
import streamlit as st


def validate_api_key(api_key: str) -> bool:
    """Validates the OpenAI API key by trying to create a completion."""
    openai.api_key = api_key
    try:
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=1,
            messages=[
                {"role": "user", "content": "Hello!"}
            ]
        )
        return True
    except openai.error.AuthenticationError:
        return False


def predict_token(param, chunks) -> int:
    """predict how many tokens to generate."""
    if st.session_state["OPENAI_API_KEY"] is not None:
        os.environ['OPENAI_API_KEY'] = st.session_state["OPENAI_API_KEY"]
        llm = OpenAI()
        total_token = 0
        for chunk in chunks:
            chunk_token = llm.get_num_tokens(chunk['content'])
            chunk_token += param.max_tokens_rec
            total_token += chunk_token
        if st.session_state['FINAL_SUMMARY_MODE']:
            total_token += param.max_tokens_final

        return total_token
    else:
        return 0
