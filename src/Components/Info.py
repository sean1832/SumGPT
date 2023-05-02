import streamlit as st
import Modules.file_io as file_io


def info():
    info_panel = st.container()
    
    manifest = 'src/manifest.json'
    st.session_state['MANIFEST'] = manifest_data = file_io.read_json(manifest)

    with info_panel:
        st.markdown('---')
        st.markdown(f"# {manifest_data['name']}")
        st.markdown(f"Version: `{manifest_data['version']}`")
        st.markdown(f"Author: {manifest_data['author']}")
        st.markdown(f"[Report a bug]({manifest_data['bugs']['url']})")
        st.markdown(f"[GitHub repo]({manifest_data['homepage']})")
        st.markdown(f"License: [{manifest_data['license']['type']}]({manifest_data['license']['url']})")