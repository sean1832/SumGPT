import streamlit as st
from Components.sidebar import sidebar
import Modules.file_io as file_io
import GPT
import util

st.set_page_config(page_title="SumGPT", page_icon="📝", layout="wide")

if not st.session_state.get('OPENAI_API_KEY'):
    st.session_state['OPENAI_API_KEY'] = None

if not st.session_state.get('OPENAI_PERSONA'):
    st.session_state['OPENAI_PERSONA'] = None

if not st.session_state.get('CHUNK_SIZE'):
    st.session_state['CHUNK_SIZE'] = None

if not st.session_state.get('OPENAI_PARAMS'):
    st.session_state['OPENAI_PARAMS'] = None

file_handler = st.container()
content_handler = st.container()
result_handler = st.container()

sidebar()

with file_handler:
    uploaded_files = st.file_uploader("Upload your files", type=['txt', 'pdf', 'docx', 'md'],
                                      accept_multiple_files=True)
    file_contents = []
    with st.spinner("🔍 Reading files... (mp3 files might take a while)"):
        for file in uploaded_files:
            file_contents.append({'name': file.name, 'content': file_io.read(file)})

with content_handler:
    if file_contents:
        with st.expander("File Preview"):
            for file in file_contents:
                if file['name'].endswith(".pdf"):
                    file_content = "\n\n".join(file['content'])
                    st.text_area(file['name'], file_content, height=200)
                else:
                    file_content = file['content']
                    st.text_area(file['name'], file_content, height=200)

with result_handler:
    run_button = st.button("🚀 Run")

    chunks = []
    for file in file_contents:
        content = file['content']
        if file['name'].endswith(".pdf"):
            content = "\n\n".join(file['content'])
        chunks.extend(util.convert_to_chunks(content, chunk_size=500))

    token_usage = GPT.misc.predict_token(st.session_state['OPENAI_PARAMS'], chunks)
    st.markdown(f"Price Prediction: `${token_usage * 0.000002}` || Token Usage: `{token_usage}`")

    with st.expander("Chunks"):
        for chunk in chunks:
            st.write(chunk)

    if run_button:
        API_KEY = st.session_state['OPENAI_API_KEY']
        if API_KEY and GPT.misc.validate_api_key(API_KEY):
            if file_contents:
                st.success("👍API key is valid")


                with st.spinner("Summarizing... (this might take a while)"):
                    responses, finish_reason_rec = util.recursive_summarize(chunks)
                    response, finish_reason_single = util.summarize(responses)

                with st.expander("Recursive Summaries"):
                    st.write(responses)
                if finish_reason_rec == 'length':
                    st.warning('⚠️Result cut off due to length. Consider increasing the [Max Tokens Chunks] parameter.')

                st.header("📝Summary")
                st.info(response)
                if finish_reason_single == 'length':
                    st.warning(
                        '⚠️Result cut off due to length. Consider increasing the [Max Tokens Summary] parameter.')
            else:
                st.error("❌Please upload a file.")
        else:
            st.error("❌Please enter a valid [OpenAI API key](https://beta.openai.com/account/api-keys).")
