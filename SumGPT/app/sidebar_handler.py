import json
from typing import Any, Dict, List, Tuple

import streamlit as st
import utils.helpers as helpers
from core.crypto import Crypto
from datamodel.llm_params import LLMModel, LLMParams
from streamlit_cookies_controller import CookieController


class SidebarHandler:
    def __init__(self):
        self.cookie_controller = CookieController()
        self.crypto: Crypto = st.session_state["crypto"]
        self.config = {}
        if self.config == {}:
            self._set_config_from_cookie()

        self.chunk_size = None

    def _set_config_from_cookie(self):
        config_binary = self.cookie_controller.get("config")
        if config_binary:
            try:
                self.config = json.loads(self.crypto.decrypt_b64(config_binary))
            except TypeError:
                self.config = {}
                self.cookie_controller.remove("config")  # Remove invalid cookie

    def header(self):
        st.title("SumGPT")
        st.markdown("Select the model and parameters for summarization.")

    def api_key_entry(self) -> str | None:
        st.markdown("### API Key")
        api_key = st.text_input(
            "Enter your OpenAI API key", type="password", value=self.config.get("api_key", "")
        )
        self.config["api_key"] = api_key
        return api_key

    def role_settings_panel(self, height=300) -> str:
        language = st.selectbox(
            "Role language",
            ["English", "Chinese", "Japanese", "Spanish", "French", "German", "Italian"],
        )
        role = st.text_area(
            "Role settings",
            self.config.get(
                "role",
                f"Write a detailed summary in perfect {language} that is concise, clear and coherent while capturing the main ideas the text. "
                "The summary should be well-structured and free of grammatical errors.\n\n"
                "The summary is to be written in markdown format, with a heading (###) that encapsulate the core concept of the content. It should be concise and specific. avoid generic headings like 'Summary' or 'Introduction'.",
            ),
            height=height,
        )
        if role is None:
            st.stop()
            st.warning("Role settings are not set.")

        self.config["role"] = role
        return role

    def config_control_panel(self, models_data: List[Dict[str, str]]) -> Tuple[LLMParams, int]:
        model_names = helpers.extract_values(models_data, "model")
        model_name = st.selectbox("Model", model_names, self.config.get("model_index", 0))
        model = LLMModel.construct_from_dict(self._get_model_dict(models_data, model_name))
        self.config["model"] = model_name

        _param = self._construct_param(models_data, model_name)

        chunk_size = st.number_input(
            "Chunk size (tokens)",
            32,
            _param["context_window"],
            self.config.get("chunk_size", 2048),
            step=1024,
        )
        self.config["chunk_size"] = chunk_size

        max_tokens: int = st.number_input(
            "Max output (tokens)",
            32,
            _param["max_output_tokens"],
            self.config.get("max_tokens", 512),
        )
        self.config["max_tokens"] = max_tokens

        temperature: float = st.slider("Temperature", 0.0, 1.0, self.config.get("temperature", 0.7))
        self.config["temperature"] = temperature

        return (
            LLMParams(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            ),
            chunk_size,
        )

    def _get_model_dict(self, models_data, selected_model) -> Dict[str, Any]:
        model_index = helpers.extract_dict_index(models_data, "model", selected_model)
        return models_data[model_index]

    def _construct_param(self, models_data, selected_model):
        model_dict = self._get_model_dict(models_data, selected_model)
        param = {
            "max_output_tokens": model_dict["max_output_tokens"],
            "context_window": model_dict["context_window"],
        }
        return param

    def import_config(self):
        st.markdown("### Import Configuration")
        config_file = st.file_uploader("Upload configuration file", type=["json"])
        if config_file:
            config = json.load(config_file)
            self.config = config
            self.cookie_controller.set("config", self.crypto.encrypt_b64(json.dumps(config)))

    def export_config(self):
        st.markdown("### Export Configuration")
        st.download_button(
            "Export configuration",
            data=json.dumps(self.config, indent=2),
            file_name="sumgpt_config.json",
        )

    def footer(self, data: Dict[str, Any]):
        st.markdown("---")
        st.markdown("### SumGPT")
        st.markdown(f"Version: `{data.get('version')}`")
        st.markdown(f"Author: {data.get('author')}")
        st.markdown(f"[Report a bug]({data['bugs']['url']})")
        st.markdown(f"[GitHub repo]({data['repository']['url']})")
        st.markdown(f"License: [{data['license']['type']}]({data['license']['url']})")
