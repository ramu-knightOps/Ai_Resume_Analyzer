"""Admin analytics page."""

import streamlit as st

from ..components.admin_dashboard import render_admin_console
from ..components.styles import section_card
from ..services.storage import parse_admin_credentials


def render_admin_page(database, theme_mode: str):
    credentials = parse_admin_credentials()
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    st.markdown(
        section_card("Admin Console v2", "A polished analytics workspace for role flow, score quality, and feedback intelligence."),
        unsafe_allow_html=True,
    )

    if not st.session_state.admin_authenticated:
        login_col1, login_col2 = st.columns([1.1, 0.9])
        with login_col1:
            st.markdown(section_card("Secure access", "Enter admin credentials to open the analytics workspace."), unsafe_allow_html=True)
            username = st.text_input("Username", key="admin_username")
            password = st.text_input("Password", type="password", key="admin_password")
            if not credentials:
                st.warning("Admin credentials are not configured. Add them in `.env` before using the console.")
            if st.button("Open Admin Console", width="stretch"):
                if credentials.get(username) == password:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_username = username
                    st.rerun()
                else:
                    st.error("Wrong ID and password provided.")
        with login_col2:
            st.markdown(
                """
                <section class="skill-panel">
                    <div class="skill-panel-title">Control room access</div>
                    <div class="skill-panel-subtitle">This workspace includes candidate records, regional signals, score distribution, and feedback monitoring.</div>
                    <div class="skill-chip-row">
                        <span class="skill-chip skill-chip-emerald">Role Trends</span>
                        <span class="skill-chip skill-chip-amber">Score Analytics</span>
                        <span class="skill-chip skill-chip-slate">Geo Footprint</span>
                        <span class="skill-chip skill-chip-emerald">Feedback Pulse</span>
                    </div>
                </section>
                """,
                unsafe_allow_html=True,
            )
        return

    admin_action_col1, admin_action_col2 = st.columns([1, 5])
    with admin_action_col1:
        if st.button("Logout", width="stretch"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_username = None
            st.rerun()
    with admin_action_col2:
        active_admin = st.session_state.get("admin_username", "Admin")
        st.success(f"Welcome {active_admin}. The analytics workspace is ready.")

    plot_data, users_df, feedback_df = database.load_admin_frames()
    render_admin_console(plot_data, users_df, feedback_df, theme_mode)
