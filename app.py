from frontend.components.sidebar import sidebar
import streamlit as st
from frontend.pages.editor import render as editor
from frontend.pages.home import render as home


st.set_page_config(page_title="Super Editor", layout="wide")

page = sidebar()

if page == "Home":
    home()
elif page == "Editor":
    editor()

