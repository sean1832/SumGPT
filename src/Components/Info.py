import streamlit as st
import Modules.file_io as file_io


def info():
    info_panel = st.container()
    
    manifest = 'src/manifest.json'

    with info_panel:
        st.markdown('---')
        st.markdown(f"# {file_io.read_json(manifest, 'name')}")
        st.markdown(f"Version: `{file_io.read_json(manifest, 'version')}`")
        st.markdown(f"Author: {file_io.read_json(manifest, 'author')}")
        st.markdown(f"[Report a bug]({file_io.read_json(manifest, 'bugs')})")
        st.markdown(f"[GitHub repo]({file_io.read_json(manifest, 'homepage')})")
        st.markdown(f"License: [{file_io.read_json(manifest, 'license')}](https://github.com/sean1832/SumGPT/blob/master/LICENSE)")