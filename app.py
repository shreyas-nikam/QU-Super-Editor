from frontend.components.sidebar import sidebar
import streamlit as st
from frontend.pages.editor import Editor
from frontend.pages.home import render as home


if "initial_run" not in st.session_state:
    st.session_state.editor = Editor()
    st.session_state.initial_run = True

st.set_page_config(page_title="Super Editor", layout="wide")

page = sidebar()

if page == "Home":
    home()
elif page == "Editor":
    st.session_state.editor.render()

