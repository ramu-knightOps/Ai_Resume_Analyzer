"""Navigation and shell controls for the Streamlit frontend."""

import streamlit as st


NAV_OPTIONS = ["Home", "Analyze", "Results", "Feedback", "About", "Admin"]
NAV_LABELS = {
    "Home": "Home",
    "Analyze": "Analyze resume",
    "Results": "Results",
    "Feedback": "Feedback",
    "About": "About",
    "Admin": "Admin",
}
NAV_ICONS = {
    "Home": "⌂",
    "Analyze": "+",
    "Results": "▤",
    "Feedback": "◇",
    "About": "ⓘ",
    "Admin": "⚙",
}

def render_theme_picker():
    theme_label_map = {
        "System": "Theme · Auto",
        "Light": "Theme · Light",
        "Dark": "Theme · Dark",
    }

    def _on_theme_change():
        st.session_state.theme_mode = {
            "Auto": "System",
            "Light": "Light",
            "Dark": "Dark",
        }[st.session_state.theme_selector]

    st.sidebar.markdown(
        f"<div class='theme-inline-label'>{theme_label_map[st.session_state.theme_mode]}</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<div class='theme-switcher-module__q-SprW__root' data-small=''></div>", unsafe_allow_html=True)
    st.sidebar.radio(
        "Theme mode",
        ["Auto", "Light", "Dark"],
        key="theme_selector",
        horizontal=True,
        label_visibility="collapsed",
        on_change=_on_theme_change,
    )


def render_navigation() -> str:
    def _set_nav(target):
        st.session_state.nav_choice = target

    def _format_nav(key):
        active_marker = "  •" if st.session_state.get("nav_choice") == key else ""
        return f"{NAV_ICONS[key]}  {NAV_LABELS[key]}{active_marker}"

    st.sidebar.markdown(
        """
        <div class='nav-stage'>
            <div class='nav-mark'>T</div>
            <div class='nav-title'>Taskoora</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for nav_key in NAV_OPTIONS:
        st.sidebar.button(
            _format_nav(nav_key),
            key=f"nav_{nav_key.lower()}",
            width="stretch",
            on_click=_set_nav,
            args=(nav_key,),
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='padding: 12px 4px 2px 4px;'>
            <div style='font-size: 0.82rem; line-height: 1.5; color: var(--sidebar-muted) !important;'>Resume evidence, organized by task.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.session_state.get("nav_choice", "Home")
