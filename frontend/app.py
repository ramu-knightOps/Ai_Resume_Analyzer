"""Streamlit user interface entry point."""

import streamlit as st

from .api_client import ResumeAnalyzerClient
from .components.navigation import ensure_sidebar_open, render_navigation, render_theme_picker
from .components.styles import hero_section, render_app_styles
from .pages.about import render_about_page
from .pages.admin import render_admin_page
from .pages.candidate import render_candidate_page
from .pages.feedback import render_feedback_page
from .services.storage import get_database


st.set_page_config(
    page_title="TASKOORA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _initialize_session():
    st.session_state.setdefault("theme_mode", "System")
    st.session_state.setdefault("theme_selector", "◫")
    st.session_state.setdefault("nav_choice", "User")


def run():
    _initialize_session()
    st.markdown(render_app_styles(st.session_state.theme_mode), unsafe_allow_html=True)
    ensure_sidebar_open()
    render_theme_picker()
    choice = render_navigation()
    st.markdown(hero_section(), unsafe_allow_html=True)

    database = get_database()
    if database.status_message:
        st.info(database.status_message)

    client = ResumeAnalyzerClient()
    if choice == "User":
        render_candidate_page(database, client)
    elif choice == "Feedback":
        render_feedback_page(database)
    elif choice == "About":
        render_about_page()
    else:
        render_admin_page(database, st.session_state.theme_mode)


if __name__ == "__main__":
    run()
