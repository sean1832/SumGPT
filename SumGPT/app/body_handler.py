import asyncio
import datetime
import json
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import utils.io as io
from core.crypto import Crypto
from core.llm import LLM
from core.tokenizer import Tokenizer
from datamodel.chunk import Chunk
from datamodel.llm_params import LLMParams
from streamlit_cookies_controller import CookieController


class BodyHandler:
    def file_uploader(self, type: List[str] = ["txt"]) -> List[Dict[str, str]]:
        uploaded_files = st.file_uploader(
            "📁 Upload your files", type=type, accept_multiple_files=True
        )
        files = []
        if uploaded_files is None:
            st.stop()
            st.warning("File is not uploaded.")
        for file in uploaded_files:
            text = io.read_to_string(file)
            filename = file.name
            files.append({"filename": filename, "text": text})
        return files

    def segment_text(
        self, text: str, chunk_size: int, model: str, input_id: int
    ) -> Tuple[List[Chunk], int]:
        chunks: List[Chunk] = []
        tokenizer = Tokenizer(model)
        total_tokens = tokenizer.tokenize(text)
        count = 0
        for i in range(0, len(total_tokens), chunk_size):
            chunk_tokens = total_tokens[i : i + chunk_size]
            content = tokenizer.detokenize(chunk_tokens)
            chunks.append(Chunk(count, content, len(chunk_tokens), input_id))
            count += 1
        return chunks, len(total_tokens)

    def _get_tokens(self, response_meta: Dict[str, Any]) -> Tuple[int, int, int]:
        completion_tokens = response_meta.get("token_usage", {}).get("completion_tokens", 0)
        prompt_tokens = response_meta.get("token_usage", {}).get("prompt_tokens", 0)
        cached_tokens = (
            response_meta.get("token_usage", {})
            .get("prompt_tokens_details", {})
            .get("cached_tokens", 0)
        )
        return completion_tokens, prompt_tokens, cached_tokens

    def agenerate(
        self,
        chunks: List[Chunk],
        gpt_params: LLMParams,
        role: str,
        api_key: Optional[str],
        chunk_size: int,
    ) -> None:
        generate_button = st.button(
            "🚀 Run",
        )
        total_chunks = len(chunks)
        progress_text = st.empty()

        total_price_text = st.empty()

        if generate_button:
            if not api_key:
                st.error("❌ Please enter your OpenAI API key in the sidebar.")
                return
            if not role:
                st.error("❌ Please enter a role description in the sidebar.")
                return

            st.session_state["summaries"] = []  # Initialize or reset summaries

            async def process_chunks():
                llm = LLM(api_key, gpt_params)
                total_price = 0
                progress_bar = st.progress(0)
                completed_chunks = 0
                progress_text.write(f"Generating summaries 0/{total_chunks}")

                # Sort chunks by chunk.id
                sorted_chunks = sorted(chunks, key=lambda c: c.id)

                # Group chunks by filename
                filename_chunks = {}
                for chunk in sorted_chunks:
                    if chunk.filename not in filename_chunks:
                        filename_chunks[chunk.filename] = []
                    filename_chunks[chunk.filename].append(chunk)

                # Create expanders for each file
                expanders = {
                    filename: st.expander(f"{filename}") for filename in filename_chunks.keys()
                }

                # Create tasks for all chunks (sorted by chunk.id)
                tasks = [llm.agenerate(chunk.content, role) for chunk in sorted_chunks]

                # Run all tasks and get the results in the same order
                summaries = await asyncio.gather(*tasks)

                # Process the results in order
                for summary, current_chunk in zip(summaries, sorted_chunks):
                    completed_chunks += 1
                    progress_text.write(f"Generating summaries {completed_chunks}/{total_chunks}")
                    progress_bar.progress(completed_chunks / total_chunks)

                    with expanders[current_chunk.filename]:
                        with st.chat_message("ai"):
                            st.write(summary.content)
                            completion_tokens, prompt_tokens, cached_tokens = self._get_tokens(
                                summary.response_metadata
                            )
                            price = round(
                                llm.Calc_price(prompt_tokens, completion_tokens, cached_tokens), 6
                            )
                            st.write(
                                f"Tokens: `{completion_tokens + prompt_tokens}`, price: `${price}`"
                            )
                            total_price += price

                    # Store the summary in session state
                    st.session_state["summaries"].append(
                        {
                            "filename": current_chunk.filename,
                            "content": summary.content,
                            "tokens": completion_tokens + prompt_tokens,
                            "price": price,
                        }
                    )

                progress_text.write("✅ All chunks processed!")
                progress_bar.progress(1.0)
                total_price_text.write(f"Total price: `${round(total_price, 6)}`")

            # Run the async processing
            asyncio.run(process_chunks())
            config = self._serialize_config(
                api_key,
                role,
                gpt_params.model.name,
                chunk_size,
                gpt_params.max_tokens,
                gpt_params.temperature,
            )
            crypto: Crypto = st.session_state["crypto"]
            config = crypto.encrypt_b64(json.dumps(config))
            controler = CookieController()
            controler.set(
                "config",
                config,
                expires=datetime.datetime.now() + datetime.timedelta(days=30),
            )
        else:
            # Check if summaries exist in session state and display them
            if "summaries" in st.session_state:
                total_price = 0
                # Group summaries by filename
                filename_summaries = {}
                for summary_data in st.session_state["summaries"]:
                    filename = summary_data["filename"]
                    if filename not in filename_summaries:
                        filename_summaries[filename] = []
                    filename_summaries[filename].append(summary_data)

                # Display summaries grouped by filename
                for filename, summaries in filename_summaries.items():
                    with st.expander(f"{filename}"):
                        for summary_data in summaries:
                            with st.chat_message("ai"):
                                st.write(summary_data["content"])
                                st.write(
                                    f"Tokens: `{summary_data['tokens']}`, price: `${summary_data['price']}`"
                                )
                                total_price += summary_data["price"]
                total_price_text.write(f"Total price: `${round(total_price, 6)}`")

    def download_summaries(self):
        if "summaries" in st.session_state:
            summaries = st.session_state["summaries"]
            if not summaries:
                return
            st.download_button(
                "📥 Download summaries",
                self._serialize_summaries(summaries),
                "summaries.md",
                mime="application/markdown",
            )

    def _serialize_summaries(self, summaries):
        markdown = ""

        markdown_by_filename = {}
        for summary in summaries:
            filename = summary["filename"]
            if filename not in markdown_by_filename:
                markdown_by_filename[filename] = []
            markdown_by_filename[filename].append(summary["content"])

        for filename, content in markdown_by_filename.items():
            markdown += f"# {filename}\n"
            markdown += "\n\n".join(content)
            markdown += "\n\n"

        return markdown

    def _serialize_config(self, api_key, role, model, chunk_size, max_tokens, temperature):
        return {
            "api_key": api_key,
            "role": role,
            "model": model,
            "chunk_size": chunk_size,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
