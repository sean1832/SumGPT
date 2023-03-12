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
    uploaded_files = st.file_uploader("📁 Upload your files", type=['txt', 'pdf', 'docx', 'md'],
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
        chunks.extend(util.convert_to_chunks(content, chunk_size=st.session_state['CHUNK_SIZE']))

    token_usage = GPT.misc.predict_token(st.session_state['OPENAI_PARAMS'], chunks)
    st.markdown(f"Price Prediction: `${round(token_usage * 0.000002, 5)}` || Token Usage: `{token_usage}`")

    with st.expander(f"Chunks ({len(chunks)})"):
        for chunk in chunks:
            st.write(chunk)

    if run_button:
        API_KEY = st.session_state['OPENAI_API_KEY']
        if API_KEY and GPT.misc.validate_api_key(API_KEY):
            if file_contents:
                st.success("👍API key is valid")
                print(f'delay: {st.session_state["DELAY"]}')
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
                st.error("❌ Please upload a file to continue.")
        else:
            st.error("❌ Please enter a valid [OpenAI API key](https://beta.openai.com/account/api-keys).")
