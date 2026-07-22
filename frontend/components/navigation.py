"""Navigation and shell controls for the Streamlit frontend."""

import streamlit as st
import streamlit.components.v1 as components


NAV_OPTIONS = ["User", "Feedback", "About", "Admin"]
NAV_LABELS = {
    "User": "Candidate Studio",
    "Feedback": "Signal & Feedback",
    "About": "About The Engine",
    "Admin": "Admin Atlas",
}


def ensure_sidebar_open():
    components.html(
        """
        <script>
        const openSidebarIfNeeded = () => {
          const doc = window.parent.document;
          const sidebar = doc.querySelector('[data-testid="stSidebar"]');
          const opener = doc.querySelector('[data-testid="collapsedControl"] button, [data-testid="stSidebarCollapsedControl"] button, button[kind="header"][aria-label*="sidebar" i]');

          if (!sidebar && opener) {
            opener.click();
            return;
          }

          if (sidebar) {
            const width = sidebar.getBoundingClientRect().width;
            if (width < 40 && opener) {
              opener.click();
            }
          }
        };

        setTimeout(openSidebarIfNeeded, 50);
        setTimeout(openSidebarIfNeeded, 250);
        setTimeout(openSidebarIfNeeded, 700);
        </script>
        """,
        height=0,
    )


def render_theme_picker():
    theme_label_map = {
        "System": "Theme · Auto",
        "Light": "Theme · Light",
        "Dark": "Theme · Dark",
    }

    def _on_theme_change():
        st.session_state.theme_mode = {
            "◫": "System",
            "☀": "Light",
            "☾": "Dark",
        }[st.session_state.theme_selector]

    st.markdown(
        f"<div class='theme-inline-label'>{theme_label_map[st.session_state.theme_mode]}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='theme-switcher-module__q-SprW__root' data-small=''></div>", unsafe_allow_html=True)
    st.radio(
        "Theme mode",
        ["◫", "☀", "☾"],
        key="theme_selector",
        horizontal=True,
        label_visibility="collapsed",
        on_change=_on_theme_change,
    )


def render_navigation() -> str:
    def _set_nav(target):
        st.session_state.nav_choice = target

    def _format_nav(key):
        idx = NAV_OPTIONS.index(key) + 1
        prefix = "◆" if st.session_state.get("nav_choice") == key else f"{idx:02d}"
        return f"{prefix}  {NAV_LABELS[key]}"

    st.sidebar.markdown(
        """
        <div class='nav-stage'>
            <div class='nav-kicker'>Control Deck</div>
            <div class='nav-title'>Navigation</div>
            <div class='nav-copy'>Move through the analyzer like chapters in a compact studio console.</div>
            <div class='nav-orbit'></div>
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
            <div style='font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.7;'>Studio Notes</div>
            <div style='margin-top: 10px; font-size: 1rem; font-weight: 700;'>Career intelligence</div>
            <div style='font-size: 0.95rem; opacity: 0.86; margin-top: 8px;'>Compare resumes to target roles with role-fit analysis and focused skill advice.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.session_state.get("nav_choice", "User")
