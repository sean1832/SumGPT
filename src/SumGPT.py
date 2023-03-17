import Components
import streamlit as st
from Components.sidebar import sidebar
import Modules.file_io as file_io
import GPT
import util

Components.StreamlitSetup.setup()

app_header = st.container()

file_handler = st.container()
content_handler = st.container()
result_handler = st.container()

with app_header:
    st.title("📝 SumGPT")
    st.markdown("##### Summarize your text with OpenAI's GPT-3.5 API")
    st.markdown("##### [GitHub repo](https://github.com/sean1832/SumGPT)")

sidebar()

with file_handler:
    youtube_link_empty = st.empty()
    upload_file_emtpy = st.empty()
    youtube_link = youtube_link_empty.text_input(label="🔗 YouTube Link",
                                                 placeholder="Enter your YouTube link",
                                                 help="Enter your YouTube link to download the video and extract the audio")
    upload_file = upload_file_emtpy.file_uploader("📁 Upload your file", type=['txt', 'pdf', 'docx', 'md'])
    if youtube_link:
        upload_file_emtpy.empty()
        with st.spinner("🔍 Extracting transcript..."):
            transcript, title = util.extract_youtube_transcript(youtube_link)
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
        st.markdown(f"Price Prediction: `${round(token_usage * 0.000002, 5)}` || Token Usage: `{token_usage}`")

        # max tokens exceeded warning
        exceeded = util.exceeded_token_handler(param=st.session_state['OPENAI_PARAMS'], chunks=chunks)

        if st.button("🚀 Run", disabled=exceeded):
            API_KEY = st.session_state['OPENAI_API_KEY']
            if not API_KEY and GPT.misc.validate_api_key(API_KEY):
                st.error("❌ Please enter a valid [OpenAI API key](https://beta.openai.com/account/api-keys).")
            else:
                with st.spinner("Summarizing... (this might take a while)"):
                    rec_max_token = st.session_state['OPENAI_PARAMS'].max_tokens_rec
                    rec_responses, finish_reason_rec = util.recursive_summarize(chunks, rec_max_token)
                    if st.session_state['FINAL_SUMMARY_MODE']:
                        final_response, finish_reason_final = util.summarize(rec_responses)
                    else:
                        final_response = None

                with st.expander("Recursive Summaries", expanded=not st.session_state['FINAL_SUMMARY_MODE']):
                    for response in rec_responses:
                        st.info(response)
                if finish_reason_rec == 'length':
                    st.warning('⚠️Result cut off due to length. Consider increasing the [Max Tokens Chunks] parameter.')

                if st.session_state['FINAL_SUMMARY_MODE']:
                    st.header("📝Summary")
                    st.info(final_response)
                    if finish_reason_final == 'length':
                        st.warning(
                            '⚠️Result cut off due to length. Consider increasing the [Max Tokens Summary] parameter.')
                util.download_results(rec_responses, final_response)
