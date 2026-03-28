LIGHT_THEME = {
    "bg_start": "#fbf6ef",
    "bg_end": "#f3ece1",
    "glow_1": "rgba(217, 119, 6, 0.18)",
    "glow_2": "rgba(15, 118, 110, 0.14)",
    "surface": "rgba(255, 250, 244, 0.88)",
    "surface_strong": "rgba(255, 255, 255, 0.92)",
    "card_bg": "rgba(255, 250, 244, 0.84)",
    "ink": "#1f2933",
    "muted": "#52606d",
    "line": "rgba(31, 41, 51, 0.09)",
    "accent": "#d97706",
    "accent_2": "#0f766e",
    "accent_3": "#b45309",
    "input_bg": "rgba(255, 255, 255, 0.96)",
    "input_text": "#111827",
    "input_placeholder": "#6b7280",
    "sidebar_start": "#f8f4ed",
    "sidebar_end": "#f0e9dd",
    "sidebar_text": "#1f2933",
    "sidebar_surface": "rgba(0, 0, 0, 0.03)",
    "sidebar_line": "rgba(31, 41, 51, 0.10)",
    "sidebar_muted": "#52606d",
    "sidebar_glow_1": "rgba(217, 119, 6, 0.12)",
    "sidebar_glow_2": "rgba(15, 118, 110, 0.10)",
    "shadow": "0 12px 34px rgba(84, 63, 38, 0.09)",
}

DARK_THEME = {
    "bg_start": "#09111a",
    "bg_end": "#0f1722",
    "glow_1": "rgba(245, 158, 11, 0.14)",
    "glow_2": "rgba(20, 184, 166, 0.12)",
    "surface": "rgba(15, 23, 34, 0.86)",
    "surface_strong": "rgba(17, 24, 39, 0.90)",
    "card_bg": "rgba(15, 23, 34, 0.82)",
    "ink": "#e5eef8",
    "muted": "#b2c0d0",
    "line": "rgba(203, 213, 225, 0.12)",
    "accent": "#f59e0b",
    "accent_2": "#14b8a6",
    "accent_3": "#d97706",
    "input_bg": "rgba(17, 24, 39, 0.96)",
    "input_text": "#f8fafc",
    "input_placeholder": "#94a3b8",
    "sidebar_start": "rgba(8, 15, 25, 0.98)",
    "sidebar_end": "rgba(12, 19, 31, 0.98)",
    "sidebar_text": "#f8fafc",
    "sidebar_surface": "rgba(255, 255, 255, 0.03)",
    "sidebar_line": "rgba(255, 255, 255, 0.08)",
    "sidebar_muted": "#b2c0d0",
    "sidebar_glow_1": "rgba(245, 158, 11, 0.10)",
    "sidebar_glow_2": "rgba(20, 184, 166, 0.10)",
    "shadow": "0 12px 34px rgba(0, 0, 0, 0.22)",
}


def _theme_vars_css(values):
    return "\n".join([
        f"        --bg-start: {values['bg_start']};",
        f"        --bg-end: {values['bg_end']};",
        f"        --glow-1: {values['glow_1']};",
        f"        --glow-2: {values['glow_2']};",
        f"        --surface: {values['surface']};",
        f"        --surface-strong: {values['surface_strong']};",
        f"        --card-bg: {values['card_bg']};",
        f"        --ink: {values['ink']};",
        f"        --muted: {values['muted']};",
        f"        --line: {values['line']};",
        f"        --accent: {values['accent']};",
        f"        --accent-2: {values['accent_2']};",
        f"        --accent-3: {values['accent_3']};",
        f"        --input-bg: {values['input_bg']};",
        f"        --input-text: {values['input_text']};",
        f"        --input-placeholder: {values['input_placeholder']};",
        f"        --sidebar-start: {values['sidebar_start']};",
        f"        --sidebar-end: {values['sidebar_end']};",
        f"        --sidebar-text: {values['sidebar_text']};",
        f"        --sidebar-surface: {values['sidebar_surface']};",
        f"        --sidebar-line: {values['sidebar_line']};",
        f"        --sidebar-muted: {values['sidebar_muted']};",
        f"        --sidebar-glow-1: {values['sidebar_glow_1']};",
        f"        --sidebar-glow-2: {values['sidebar_glow_2']};",
        f"        --shadow: {values['shadow']};",
    ])


def render_app_styles(theme_mode):
    light_vars = _theme_vars_css(LIGHT_THEME)
    dark_vars = _theme_vars_css(DARK_THEME)

    if theme_mode == "Dark":
        root_css = dark_vars
        extra_css = ""
    elif theme_mode == "Light":
        root_css = light_vars
        extra_css = ""
    else:
        root_css = light_vars
        extra_css = f"""
    @media (prefers-color-scheme: dark) {{
        :root {{
{dark_vars}
            --radius-xl: 28px;
            --radius-lg: 20px;
        }}
    }}
"""

    return f"""
<style>
    :root {{
{root_css}
        --radius-xl: 28px;
        --radius-lg: 20px;
    }}
{extra_css}

    .stApp {{
        background:
            radial-gradient(circle at top left, var(--glow-1), transparent 28%),
            radial-gradient(circle at top right, var(--glow-2), transparent 26%),
            linear-gradient(180deg, var(--bg-start) 0%, var(--bg-end) 100%);
        color: var(--ink);
    }}

    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1220px;
    }}

    h1, h2, h3, h4, h5, p, li, label, span, div {{
        color: var(--ink);
    }}

    h1, h2, h3, h4 {{
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.02em;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--sidebar-start) 0%, var(--sidebar-end) 100%);
        border-right: 1px solid var(--sidebar-line);
    }}

    [data-testid="stSidebar"] > div {{
        background:
            radial-gradient(circle at 18% 12%, var(--sidebar-glow-1), transparent 24%),
            radial-gradient(circle at 84% 22%, var(--sidebar-glow-2), transparent 20%),
            linear-gradient(180deg, var(--sidebar-start) 0%, var(--sidebar-end) 100%);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--sidebar-text) !important;
    }}

    /* Professional Navigation Buttons */
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        color: var(--sidebar-muted) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        transition: all 200ms ease;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background: color-mix(in srgb, var(--sidebar-text) 8%, transparent) !important;
        color: var(--sidebar-text) !important;
        transform: translateX(4px);
    }}

    [data-testid="stSidebar"] .stButton > button:active {{
        background: color-mix(in srgb, var(--sidebar-text) 12%, transparent) !important;
        transform: translateX(2px);
    }}

    .nav-stage {{
        position: relative;
        overflow: hidden;
        padding: 1rem 1rem 1.1rem 1rem;
        border-radius: 24px;
        background: var(--sidebar-surface);
        border: 1px solid var(--sidebar-line);
        box-shadow: inset 0 1px 0 color-mix(in srgb, var(--sidebar-text) 6%, transparent);
        margin-bottom: 0.8rem;
    }}

    .nav-kicker {{
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--sidebar-muted) !important;
        opacity: 0.72;
        margin-bottom: 0.7rem;
    }}

    .nav-title {{
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--sidebar-text) !important;
        line-height: 1;
        margin-bottom: 0.55rem;
        font-family: Georgia, "Times New Roman", serif;
    }}

    .nav-copy {{
        font-size: 0.93rem;
        line-height: 1.55;
        color: var(--sidebar-muted) !important;
        max-width: 15rem;
    }}

    .nav-orbit {{
        position: absolute;
        right: -24px;
        top: -18px;
        width: 110px;
        height: 110px;
        border-radius: 999px;
        background:
            radial-gradient(circle at center, var(--sidebar-glow-1) 0%, color-mix(in srgb, var(--sidebar-glow-1) 40%, transparent) 36%, transparent 68%);
        filter: blur(1px);
        pointer-events: none;
    }}

    .main .stButton > button,
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 82%, transparent) 0%, color-mix(in srgb, var(--accent-3) 82%, transparent) 100%);
        color: #fff !important;
        border: none;
        border-radius: 999px;
        padding: 0.75rem 1.25rem;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(180, 83, 9, 0.14);
    }}

    .main .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        transform: translateY(-1px);
        filter: brightness(1.03);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.55rem;
        padding: 0.35rem;
        border-radius: 22px;
        background: color-mix(in srgb, var(--surface) 92%, rgba(16, 16, 16, 0.04));
        border: 1px solid var(--line);
        margin: 0.6rem 0 1rem 0;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: auto;
        padding: 0.7rem 1rem;
        border-radius: 16px;
        background: transparent;
        color: var(--muted);
        font-weight: 700;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 14%, transparent) 0%, color-mix(in srgb, var(--accent-2) 16%, transparent) 100%);
        color: var(--ink) !important;
        border: 1px solid color-mix(in srgb, var(--accent-2) 18%, var(--line));
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        background: transparent !important;
    }}

    .nav-stage-inline {{
        margin-top: 1.25rem;
        margin-bottom: 0.9rem;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] input {{
        border-radius: 18px !important;
        border: 1px solid var(--line) !important;
        background: var(--input-bg) !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        caret-color: var(--input-text) !important;
        box-shadow: none !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: var(--input-placeholder) !important;
        -webkit-text-fill-color: var(--input-placeholder) !important;
        opacity: 1 !important;
    }}

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {{
        color: var(--ink) !important;
        font-weight: 700 !important;
    }}

    /* ── Skill panel ── */

    .skill-panel {{
        margin: 0.65rem 0 1.1rem 0;
        padding: 1.2rem 1.25rem;
        border-radius: 22px;
        background: var(--card-bg);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }}

    .skill-panel-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--ink) !important;
        margin-bottom: 0.35rem;
        font-family: Georgia, "Times New Roman", serif;
    }}

    .skill-panel-subtitle {{
        font-size: 0.94rem;
        line-height: 1.5;
        color: var(--muted) !important;
        margin-bottom: 0.9rem;
    }}

    .skill-chip-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }}

    .skill-chip {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.42rem 0.85rem;
        font-size: 0.88rem;
        font-weight: 600;
        line-height: 1;
        letter-spacing: 0.01em;
        border: 1px solid transparent;
        transition: transform 160ms ease, box-shadow 160ms ease;
        cursor: default;
    }}

    .skill-chip:hover {{
        transform: translateY(-1px);
    }}

    .skill-chip-emerald {{
        background: color-mix(in srgb, var(--accent-2) 14%, var(--surface-strong));
        color: var(--accent-2) !important;
        border-color: color-mix(in srgb, var(--accent-2) 22%, transparent);
    }}
    .skill-chip-emerald:hover {{
        box-shadow: 0 4px 12px color-mix(in srgb, var(--accent-2) 18%, transparent);
    }}

    .skill-chip-amber {{
        background: color-mix(in srgb, var(--accent) 14%, var(--surface-strong));
        color: var(--accent) !important;
        border-color: color-mix(in srgb, var(--accent) 22%, transparent);
    }}
    .skill-chip-amber:hover {{
        box-shadow: 0 4px 12px color-mix(in srgb, var(--accent) 18%, transparent);
    }}

    .skill-chip-slate {{
        background: color-mix(in srgb, var(--ink) 8%, var(--surface-strong));
        color: var(--muted) !important;
        border-color: color-mix(in srgb, var(--ink) 12%, transparent);
    }}
    .skill-chip-slate:hover {{
        box-shadow: 0 4px 12px color-mix(in srgb, var(--ink) 10%, transparent);
    }}

    .skill-chip-muted {{
        background: color-mix(in srgb, var(--muted) 10%, var(--surface-strong));
        color: var(--muted) !important;
        border-color: color-mix(in srgb, var(--muted) 16%, transparent);
    }}

    /* ── Course panel ── */

    .course-panel {{
        margin: 0.8rem 0 0.7rem 0;
    }}

    .course-panel-title {{
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
        color: var(--ink) !important;
        font-family: Georgia, "Times New Roman", serif;
        margin-bottom: 0.35rem;
    }}

    .course-panel-subtitle {{
        font-size: 0.98rem;
        line-height: 1.6;
        color: var(--muted) !important;
        max-width: 48rem;
    }}

    .course-grid {{
        display: grid;
        gap: 0.85rem;
        margin: 1rem 0 1.2rem 0;
    }}

    .course-card {{
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 0.95rem;
        align-items: center;
        text-decoration: none !important;
        padding: 0.95rem 1rem;
        border-radius: 20px;
        background: var(--card-bg);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    }}

    .course-card:hover {{
        transform: translateY(-1px);
        border-color: color-mix(in srgb, var(--accent) 28%, var(--line));
        background: color-mix(in srgb, var(--surface-strong) 86%, rgba(245, 158, 11, 0.06));
    }}

    .course-card-index {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.35rem;
        height: 2.35rem;
        border-radius: 999px;
        background: color-mix(in srgb, var(--accent-2) 12%, var(--surface-strong));
        color: var(--accent-2) !important;
        font-weight: 800;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
    }}

    .course-card-body {{
        display: flex;
        flex-direction: column;
        gap: 0.18rem;
        min-width: 0;
    }}

    .course-card-title {{
        color: var(--ink) !important;
        font-size: 1.03rem;
        font-weight: 700;
        line-height: 1.35;
    }}

    .course-card-meta {{
        color: var(--muted) !important;
        font-size: 0.84rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .course-card-arrow {{
        color: color-mix(in srgb, var(--ink) 55%, transparent) !important;
        font-size: 1.05rem;
        font-weight: 700;
    }}

    .stSlider label {{
        color: var(--ink) !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.01em;
    }}

    .stSlider [data-baseweb="slider"] {{
        padding-top: 0.45rem;
    }}

    /* Slider track (filled portion) */
    .stSlider [role="slider"] {{
        background: var(--accent-2) !important;
        border-color: var(--accent-2) !important;
        box-shadow: 0 0 8px color-mix(in srgb, var(--accent-2) 35%, transparent) !important;
        width: 18px !important;
        height: 18px !important;
    }}

    .stSlider [data-testid="stThumbValue"] {{
        color: var(--ink) !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
    }}

    /* Active track bar */
    .stSlider div[role="slider"] ~ div > div:first-child {{
        background: var(--accent-2) !important;
    }}

    /* Streamlit slider track override */
    .stSlider [data-baseweb="slider"] div[style*="background-color"] {{
        background-color: var(--accent-2) !important;
    }}

    .stSlider [data-baseweb="slider"] div[style*="background-color: rgb"] {{
        background-color: color-mix(in srgb, var(--ink) 12%, var(--surface-strong)) !important;
    }}

    /* ── File uploader ── */

    .stFileUploader > div > div {{
        border: 1px solid var(--line) !important;
        border-radius: 22px !important;
        background: var(--surface-strong) !important;
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] {{
        background: var(--input-bg) !important;
        border-radius: 18px !important;
        border: 2px dashed color-mix(in srgb, var(--accent-2) 40%, var(--line)) !important;
        padding: 1rem !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] * {{
        color: var(--ink) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] svg {{
        fill: var(--accent-2) !important;
        color: var(--accent-2) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] small {{
        color: var(--muted) !important;
    }}

    .stFileUploader label,
    .stFileUploader small,
    .stFileUploader span,
    .stFileUploader p {{
        color: var(--ink) !important;
    }}

    .stFileUploader button {{
        background: var(--surface-strong) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        font-weight: 600 !important;
        transition: background 160ms ease, border-color 160ms ease;
    }}

    .stFileUploader button:hover {{
        background: color-mix(in srgb, var(--accent-2) 12%, var(--surface-strong)) !important;
        border-color: color-mix(in srgb, var(--accent-2) 30%, var(--line)) !important;
        color: var(--ink) !important;
    }}

    /* Uploaded file item row */
    .stFileUploader [data-testid="stFileUploaderFile"] {{
        background: var(--surface-strong) !important;
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
        padding: 0.65rem 0.9rem !important;
        margin-top: 0.5rem;
    }}

    .stFileUploader [data-testid="stFileUploaderFile"] * {{
        color: var(--ink) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderFile"] svg {{
        color: var(--accent-2) !important;
        fill: var(--accent-2) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderFile"] small {{
        color: var(--muted) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDeleteBtn"] {{
        background: color-mix(in srgb, var(--ink) 8%, var(--surface-strong)) !important;
        border-radius: 999px !important;
        color: var(--muted) !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDeleteBtn"]:hover {{
        background: color-mix(in srgb, var(--ink) 14%, var(--surface-strong)) !important;
        color: var(--ink) !important;
    }}

    .stExpander {{
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--surface) !important;
        box-shadow: var(--shadow);
    }}

    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    }}

    [data-testid="stDataFrame"] {{
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid var(--line);
    }}

    /* Keep Streamlit toolbar minimal but don't hide it entirely */
    div[data-testid="stToolbar"] {{
        visibility: hidden;
    }}

    footer {{
        display: none !important;
    }}

    /* Do NOT hide #MainMenu — it can block nav in newer Streamlit */

    header[data-testid="stHeader"] {{
        background: color-mix(in srgb, var(--bg-start) 85%, transparent) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }}

    /* Ensure all .stButton buttons inside main area are always visible */
    .main .stButton > button {{
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }}

    /* Ensure sidebar buttons are always visible */
    [data-testid="stSidebar"] .stButton > button {{
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }}

    /* Ensure Streamlit header action buttons are visible */
    header[data-testid="stHeader"] button {{
        opacity: 1 !important;
        visibility: visible !important;
    }}

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {{
        position: fixed !important;
        top: 0.8rem !important;
        left: 0.85rem !important;
        z-index: 10000 !important;
    }}

    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    button[kind="header"][aria-label*="sidebar" i] {{
        width: 2.7rem !important;
        height: 2.7rem !important;
        border-radius: 999px !important;
        border: 1px solid var(--line) !important;
        background: color-mix(in srgb, var(--surface-strong) 94%, rgba(17, 17, 17, 0.08)) !important;
        color: var(--ink) !important;
        box-shadow: var(--shadow) !important;
    }}

    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    button[kind="header"][aria-label*="sidebar" i]:hover {{
        border-color: color-mix(in srgb, var(--accent-2) 24%, var(--line)) !important;
        background: color-mix(in srgb, var(--surface-strong) 88%, rgba(15, 118, 110, 0.08)) !important;
    }}

    .theme-switcher-module__q-SprW__root {{
        height: 0.2rem;
        margin: 0;
        padding: 0;
    }}

    .theme-inline-label {{
        font-size: 0.96rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1;
        margin: 2.8rem 0 0.7rem 0;
    }}

    .theme-switcher-module__q-SprW__root[data-small=""] + div[data-testid="stRadio"] {{
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1.5rem;
    }}

    .theme-switcher-module__q-SprW__root[data-small=""] + div[data-testid="stRadio"] > div {{
        background: transparent;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] div[role="radiogroup"] {{
        gap: 0.25rem;
        background: color-mix(in srgb, var(--surface) 92%, rgba(16, 16, 16, 0.06));
        border: 1px solid var(--line);
        border-radius: 9999px;
        padding: 0.2rem;
        display: flex;
        align-items: center;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label {{
        cursor: pointer;
        width: 28px;
        height: 28px;
        color: color-mix(in srgb, var(--ink) 72%, transparent) !important;
        background: transparent;
        border-radius: 9999px;
        justify-content: center;
        align-items: center;
        margin: 0;
        display: flex;
        position: relative;
        border: 0;
        padding: 0;
        min-width: 28px;
        transition: transform 180ms ease, color 180ms ease;
    }}


    .theme-switcher-module__q-SprW__root[data-small=""] + div[data-testid="stRadio"] label {{
        width: 24px;
        height: 24px;
        min-width: 24px;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label p {{
        font-size: 0.9rem !important;
        line-height: 1 !important;
        color: inherit !important;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] input:not(:disabled):checked + div {{
        box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 18%, transparent), 0px 1px 2px 0px rgba(0, 0, 0, 0.12);
        color: var(--ink);
        background: color-mix(in srgb, var(--input-bg) 90%, transparent);
        border-radius: 9999px;
        transition: background 180ms ease, box-shadow 180ms ease, color 180ms ease;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label > div {{
        transition: background 180ms ease, box-shadow 180ms ease, color 180ms ease, transform 180ms ease;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] input:not(:disabled):checked + div p {{
        color: var(--ink) !important;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] input {{
        display: none !important;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 9999px;
    }}

    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label > div {{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 9999px;
    }}
</style>
"""


def hero_section():
    return """
    <section style="padding: 2rem 2.2rem; border-radius: 30px; background: var(--surface-strong);
        border: 1px solid var(--line); box-shadow: var(--shadow);
        margin-bottom: 1.25rem; position: relative; overflow: hidden;">
        <div style="position:absolute; right:-40px; top:-40px; width:220px; height:220px;
            background: radial-gradient(circle, var(--glow-1), transparent 66%);"></div>
        <div style="position:absolute; left:-30px; bottom:-40px; width:180px; height:180px;
            background: radial-gradient(circle, var(--glow-2), transparent 66%);"></div>
        <div style="position:relative;">
            <div style="display:inline-block; padding:0.35rem 0.8rem; border-radius:999px;
                background: rgba(15,118,110,0.12); color:var(--accent-2); font-size:0.82rem; font-weight:700;
                letter-spacing:0.06em; text-transform:uppercase;">Career Studio</div>
            <h1 style="margin:0.8rem 0 0.5rem 0; font-size:3rem; line-height:1.05;">
                Resume analysis with job-fit scoring and clearer guidance.
            </h1>
            <p style="font-size:1.05rem; max-width:820px; color:var(--muted); margin:0;">
                Upload a resume, paste a job description, and get a richer view of role fit, missing skills,
                semantic matches, and personalized learning paths.
            </p>
        </div>
    </section>
    """


def info_card(title, value, subtitle, tone="warm"):
    accents = {
        "warm": ("rgba(217, 119, 6, 0.10)", "var(--accent)"),
        "teal": ("rgba(15, 118, 110, 0.12)", "var(--accent-2)"),
        "ink": ("var(--surface-strong)", "var(--ink)"),
    }
    bg, accent = accents.get(tone, accents["warm"])
    return f"""
    <div style="padding:1rem 1.1rem; border-radius:22px; background:{bg};
        border:1px solid var(--line); min-height:132px;">
        <div style="font-size:0.82rem; text-transform:uppercase; letter-spacing:0.08em; color:{accent}; font-weight:700;">{title}</div>
        <div style="font-size:2rem; font-weight:800; margin-top:0.35rem; color:var(--ink);">{value}</div>
        <div style="font-size:0.92rem; color:var(--muted); margin-top:0.45rem;">{subtitle}</div>
    </div>
    """


def section_card(title, subtitle):
    return f"""
    <div style="padding:1.2rem 1.3rem; border-radius:24px; background:var(--card-bg);
        border:1px solid var(--line); box-shadow:var(--shadow); margin:0.5rem 0 1rem 0;">
        <div style="font-size:1.25rem; font-weight:800; color:var(--ink);">{title}</div>
        <div style="font-size:0.95rem; color:var(--muted); margin-top:0.35rem;">{subtitle}</div>
    </div>
    """
