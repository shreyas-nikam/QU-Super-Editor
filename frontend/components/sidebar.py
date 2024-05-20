import streamlit as st


def sidebar():
    st.sidebar.image("frontend/assets/images/logo.jpg")
    page = st.sidebar.radio("Go to", ["Home", "Editor"])
    return page