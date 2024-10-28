import streamlit as st
from app.page import Page
from utils import io


def init():
    st.set_page_config("SumGPT", "📝", "wide")

    if "summaries" not in st.session_state:
        st.session_state["summaries"] = []


def main():
    manifest = io.read_json_file("SumGPT/manifest.json")
    models = io.read_json_file("SumGPT/models.json")

    pg = Page()
    pg.draw_header(manifest["version"])
    pg.draw_sidebar(manifest, models)
    pg.draw_body()


if __name__ == "__main__":
    init()
    main()
