import asyncio
import streamlit as st

import Components.StreamlitSetup as StreamlitSetup
StreamlitSetup.setup()

import Modules.Youtube
from Components.sidebar import sidebar
import Modules.file_io as file_io
import GPT
import util
import time

app_header = st.container()

file_handler = st.container()
content_handler = st.container()
result_handler = st.container()

with app_header:
    st.title("📝 SumGPT")
    st.markdown("##### Summarize your text with OpenAI's GPT-3.5 / GPT-4 API")
    st.markdown("##### [GitHub repo](https://github.com/sean1832/SumGPT)")
    st.warning("🚧️ This app is still in beta. Please [report any bugs](https://github.com/sean1832/SumGPT/issues) to the GitHub repo.")

sidebar()

with file_handler:
    if st.button("🔃 Refresh"):
        st.cache_data.clear()
    youtube_link_empty = st.empty()
    upload_file_emtpy = st.empty()

    youtube_link = youtube_link_empty.text_input(label="🔗 YouTube Link",
                                                 placeholder="Enter your YouTube link",
                                                 help="Enter your YouTube link to download the video and extract the audio")
    upload_file = upload_file_emtpy.file_uploader("📁 Upload your file", type=['txt', 'pdf', 'docx', 'md'])
    if youtube_link:
        upload_file_emtpy.empty()
        with st.spinner("🔍 Extracting transcript..."):
            transcript, title = Modules.Youtube.extract_youtube_transcript(youtube_link, st.session_state['CAPTION_LANGUAGES'])
            file_content = {'name': f"{title}.txt", 'content': transcript}
    elif upload_file:
        youtube_link_empty.empty()
        with st.spinner("🔍 Reading file... (mp3 file might take a while)"):
            file_content = {'name': upload_file.name, 'content': file_io.read(upload_file)}
    elif youtube_link and upload_file:
        st.warning("Please only upload one file at a time")
    else:
        file_content = None

with content_handler:
    if file_content:
        with st.expander("File Preview"):
            if file_content['name'].endswith(".pdf"):
                content = "\n\n".join(file_content['content'])
                st.text_area(file_content['name'], content, height=200)
            else:
                content = file_content['content']
                st.text_area(file_content['name'], content, height=200)

with result_handler:
    if file_content:
        chunks = []
        content = file_content['content']
        if file_content['name'].endswith(".pdf"):
            content = "\n\n".join(file_content['content'])
        chunks.extend(util.convert_to_chunks(content, chunk_size=st.session_state['CHUNK_SIZE']))

        with st.expander(f"Chunks ({len(chunks)})"):
            for chunk in chunks:
                st.write(chunk)

        token_usage = GPT.misc.predict_token(st.session_state['OPENAI_PARAMS'], chunks)
        param = st.session_state["OPENAI_PARAMS"]
        prompt_token = token_usage['prompt']
        completion_token = token_usage['completion']
        if param.model == 'gpt-4':
            price = round(prompt_token * 0.00003 + completion_token * 0.00006, 5)
            st.markdown('**Note:** To access GPT-4, please [join the waitlist](https://openai.com/waitlist/gpt-4-api)'
                        " if you haven't already received an invitation from OpenAI.")
            st.info("ℹ️️ Please keep in mind that GPT-4 is significantly **[more expensive](https://openai.com/pricing#language-models)** than GPT-3.5. ")
        elif param.model == 'gpt-3.5-turbo-16k':
            price = round(prompt_token * 0.000003 + completion_token *0.000004, 5)
        else:
            price = round(prompt_token * 0.0000015 + completion_token * 0.000002 , 5)
        st.markdown(
            f"Price Prediction: `${price}` || Total Prompt: `{prompt_token}`, Total Completion: `{completion_token}`")
        # max tokens exceeded warning
        exceeded = util.exceeded_token_handler(param=st.session_state['OPENAI_PARAMS'], chunks=chunks)

        # load cached results
        if st.session_state['PREVIOUS_RESULTS'] is not None:
            rec_responses = st.session_state['PREVIOUS_RESULTS']['rec_responses']
            rec_id = st.session_state['PREVIOUS_RESULTS']['rec_ids']
            final_response = st.session_state['PREVIOUS_RESULTS']['final_response']
            finish_reason_rec = st.session_state['PREVIOUS_RESULTS']['finish_reason_rec']
            finish_reason_final = st.session_state['PREVIOUS_RESULTS']['finish_reason_final']
        else:
            rec_responses = None
            rec_id = None
            final_response = None
            finish_reason_rec = None
            finish_reason_final = None

        # finish_reason_rec = None
        if st.button("🚀 Run", disabled=exceeded):
            start_time = time.time()
            st.cache_data.clear()
            API_KEY = st.session_state['OPENAI_API_KEY']
            if not API_KEY and not GPT.misc.validate_api_key(API_KEY):
                st.error("❌ Please enter a valid [OpenAI API key](https://beta.openai.com/account/api-keys).")
            else:
                with st.spinner("Summarizing... (this might take a while)"):
                    if st.session_state['LEGACY']:
                        rec_max_token = st.session_state['OPENAI_PARAMS'].max_tokens_rec
                        rec_responses, finish_reason_rec = util.recursive_summarize(chunks, rec_max_token)
                        if st.session_state['FINAL_SUMMARY_MODE']:
                            final_response, finish_reason_final = util.summarize(rec_responses)
                        else:
                            final_response = None
                    else:
                        completions, final_response = asyncio.run(util.summarize_experimental_concurrently(content, st.session_state['CHUNK_SIZE']))
                        rec_responses = [d["content"] for d in completions]
                        rec_ids = [d["chunk_id"] for d in completions]
                        # save previous completions
                        resp = {'rec_responses': rec_responses,
                                'rec_ids': rec_ids,
                                'final_response': final_response,
                                'finish_reason_rec': finish_reason_rec,
                                'finish_reason_final': finish_reason_final}
                        if resp != st.session_state['PREVIOUS_RESULTS']:
                            st.session_state['PREVIOUS_RESULTS'] = resp

            end_time = time.time()
            st.markdown(f"⏱️ Time taken: `{round(end_time - start_time, 2)}s`")

        if rec_responses is not None:
            with st.expander("Recursive Summaries", expanded=not st.session_state['FINAL_SUMMARY_MODE']):
                for i, response in enumerate(rec_responses):
                    st.info(f'{response}')
            if finish_reason_rec == 'length':
                st.warning('⚠️Result cut off due to length. Consider increasing the [Max Tokens Chunks] parameter.')

        if final_response is not None:
            st.header("📝Summary")
            st.info(final_response)
            if finish_reason_final == 'length':
                st.warning(
                    '⚠️Result cut off due to length. Consider increasing the [Max Tokens Summary] parameter.')
        if final_response is not None or rec_responses is not None:
            util.download_results(rec_responses, final_response)
