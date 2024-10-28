from typing import Any, Dict, List, Tuple

import streamlit as st
import utils.helpers as helpers
from datamodel.llm_params import LLMModel, LLMParams


class SidebarHandler:
    def __init__(self):
        self.config = {}
        self.chunk_size = None

    def header(self):
        st.title("SumGPT")
        st.markdown("Select the model and parameters for summarization.")

    def api_key_entry(self) -> str:
        st.markdown("### API Key")
        return st.text_input("Enter your OpenAI API key", type="password")

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
        return role

    def config_control_panel(self, models_data: List[Dict[str, str]]) -> Tuple[LLMParams, int]:
        model_names = helpers.extract_values(models_data, "model")
        model_name = st.selectbox("Model", model_names, self.config.get("model_index", 0))
        model = LLMModel.construct_from_dict(self._get_model_dict(models_data, model_name))

        _param = self._construct_param(models_data, model_name)

        chunk_size = st.number_input(
            "Chunk size (tokens)",
            32,
            _param["context_window"],
            self.config.get("chunk_size", 2048),
            step=1024,
        )
        max_tokens: int = st.number_input(
            "Max output (tokens)",
            32,
            _param["max_output_tokens"],
            self.config.get("max_tokens", 512),
        )
        temperature: float = st.slider("Temperature", 0.0, 1.0, self.config.get("temperature", 0.7))
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
        if st.button("Import configuration"):
            raise NotImplementedError  # TODO: implement

    def export_config(self):
        st.markdown("### Export Configuration")
        if st.button("Export configuration"):
            raise NotImplementedError  # TODO: implement

    def footer(self, data: Dict[str, Any]):
        st.markdown("---")
        st.markdown("### SumGPT")
        st.markdown(f"Version: `{data.get('version')}`")
        st.markdown(f"Author: {data.get('author')}")
        st.markdown(f"[Report a bug]({data['bugs']['url']})")
        st.markdown(f"[GitHub repo]({data['repository']['url']})")
        st.markdown(f"License: [{data['license']['type']}]({data['license']['url']})")
