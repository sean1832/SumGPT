import asyncio
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import utils.io as io
from core.llm import LLM
from core.tokenizer import Tokenizer
from datamodel.chunk import Chunk
from datamodel.llm_params import LLMParams


class BodyHandler:
    def file_uploader(self, type: List[str] = ["txt"]) -> List[Dict[str, str]]:
        uploaded_files = st.file_uploader("Upload a file", type=type, accept_multiple_files=True)
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

    def generate(
        self,
        chunks: List[Chunk],
        gpt_params: LLMParams,
        role: str,
        api_key: Optional[str],
    ) -> None:
        generate_button = st.button("Generate summary")
        if generate_button:
            if not api_key:
                st.error("❌ Please enter your OpenAI API key in the sidebar.")
                return
            if not role:
                st.error("❌ Please enter a role description in the sidebar.")
                return

            st.session_state["summaries"] = []  # Initialize or reset summaries

            progress_text = st.empty()
            progress_bar = st.progress(0)
            total_chunks = len(chunks)

            # Group chunks by filename
            filename_chunks = {}
            for chunk in chunks:
                if chunk.filename not in filename_chunks:
                    filename_chunks[chunk.filename] = []
                filename_chunks[chunk.filename].append(chunk)

            llm = LLM(api_key, gpt_params)
            processed_chunks = 0

            # Process chunks by filename
            for filename, file_chunks in filename_chunks.items():
                expander = st.expander(f"{filename}")
                for chunk in file_chunks:
                    processed_chunks += 1
                    progress_text.write(f"Generating summaries {processed_chunks}/{total_chunks}")
                    progress_bar.progress(processed_chunks / total_chunks)

                    summary = llm.generate(chunk.content, role)
                    with expander:
                        with st.chat_message("🤖"):
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
                    # Store the summary in session state
                    st.session_state["summaries"].append(
                        {
                            "filename": filename,
                            "content": summary.content,
                            "tokens": completion_tokens + prompt_tokens,
                            "price": price,
                        }
                    )

            progress_text.write("✅ All chunks processed!")
            progress_bar.progress(1.0)
        else:
            # Check if summaries exist in session state and display them
            if "summaries" in st.session_state:
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
                            with st.chat_message("🤖"):
                                st.write(summary_data["content"])
                                st.write(
                                    f"Tokens: `{summary_data['tokens']}`, price: `${summary_data['price']}`"
                                )

    def agenerate(
        self,
        chunks: List[Chunk],
        gpt_params: LLMParams,
        role: str,
        api_key: Optional[str],
    ) -> None:
        generate_button = st.button("Generate summary")
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
                total_chunks = len(chunks)
                progress_text = st.empty()
                progress_text.write(f"Generating summaries 0/{total_chunks}")
                total_price_text = st.empty()
                total_price = 0

                progress_bar = st.progress(0)
                completed_chunks = 0

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
                st.write(f"Total price: `${round(total_price, 6)}`")
