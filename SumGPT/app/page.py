from typing import Dict, List, Optional

import streamlit as st
from datamodel.llm_params import LLMParams

from app.body_handler import BodyHandler
from app.sidebar_handler import SidebarHandler


class Page:
    def __init__(self):
        self.chunk_size: Optional[int] = None
        self.role: Optional[str] = None
        self.api_key: Optional[str] = None
        self.llm_params: Optional[LLMParams] = None

    def draw_header(self, version):
        st.title(f"📝 SumGPT {version}")
        st.markdown("##### Summarize your text with OpenAI's API")
        st.markdown("##### [GitHub repo](https://github.com/sean1832/SumGPT)")
        st.warning(
            "Please [report any bugs](https://github.com/sean1832/SumGPT/issues) to the GitHub repo."
        )

    def draw_sidebar(self, manifest: Dict[str, str], models_data: List[Dict[str, str]]) -> None:
        with st.sidebar:
            sb = SidebarHandler()
            sb.header()
            sb.import_config()
            self.api_key = sb.api_key_entry()
            with st.expander("Role settings"):
                self.role = sb.role_settings_panel()
            with st.expander("Configuration"):
                self.llm_params, self.chunk_size = sb.config_control_panel(models_data)
            sb.export_config()
            sb.footer(manifest)

    def draw_body(self) -> None:
        if not self.chunk_size:
            st.error("❌ Please set the chunk size in the sidebar.")
            return
        if not self.llm_params:
            st.error("❌ Please set the model in the sidebar.")
            return
        if not self.role:
            st.error("❌ Please set the role in the sidebar.")
            return

        body = BodyHandler()
        texts = body.file_uploader(["txt", "md"])

        total_chunks = []
        filenames = []

        for idx, text in enumerate(texts):
            filename = text["filename"]
            filenames.append(filename)
            chunks, total_token_size = body.segment_text(
                text["text"], self.chunk_size, self.llm_params.model.name, idx
            )
            with st.expander(f"`{filename}` **(chunks: {len(chunks)})**"):
                for chunk in chunks:
                    chunk.set_filename_from_list(filenames)
                st.write([chunk.to_dict() for chunk in chunks])
                st.write(f"Tokens: `{total_token_size}`")

                total_chunks.extend(chunks)

        body.agenerate(total_chunks, self.llm_params, self.role, self.api_key)
