import GPT.bot
import streamlit as st
import GPT.param
from typing import Any, Dict, List, Tuple, Union


def get_answer_stream(content: str):
    """Returns a stream of responses from the OpenAI API."""
    params = st.session_state["OPENAI_PARAMS"]
    previous_char = ''
    bot = GPT.bot.OpenAIChatBot(st.session_state["OPENAI_API_KEY"],
                                st.session_state["OPENAI_PERSONA"],
                                params.model,
                                params.max_tokens_rec,
                                params.temperature,
                                params.top_p,
                                params.frequency_penalty,
                                params.presence_penalty)
    responses = bot.chat_stream(content)
    response_panel = st.empty()
    for response_json in responses:
        choice = response_json['choices'][0]
        if choice['finish_reason'] == 'stop':
            break

        # error handling
        if choice['finish_reason'] == 'length':
            st.warning('⚠️Result cut off due to length. Consider increasing the max tokens parameter.')
            break

        delta = choice['delta']
        if 'role' in delta or delta == {}:
            char = ''
        else:
            char = delta['content']
        answer = previous_char + char
        response_panel.info(answer)


def get_answer(content: str, max_tokens, persona: str) -> Tuple[str, str]:
    """Returns a response from the OpenAI API."""
    params = st.session_state["OPENAI_PARAMS"]
    bot = GPT.bot.OpenAIChatBot(st.session_state["OPENAI_API_KEY"],
                                persona,
                                params.model,
                                max_tokens,
                                params.temperature,
                                params.top_p,
                                params.frequency_penalty,
                                params.presence_penalty)
    response, finish_reason = bot.chat(content)
    return response, finish_reason
