"""Visual system and reusable HTML fragments for the Streamlit interface."""


LIGHT_THEME = {
    "canvas": "#f7f8fa",
    "surface": "#ffffff",
    "surface_alt": "#eef3f8",
    "ink": "#17202a",
    "muted": "#627080",
    "line": "#dce2e8",
    "primary": "#1769aa",
    "primary_soft": "#e6f0f8",
    "input": "#ffffff",
    "sidebar": "#ffffff",
    "sidebar_text": "#17202a",
    "sidebar_muted": "#627080",
    "sidebar_line": "#e5e9ee",
}

DARK_THEME = {
    "canvas": "#101419",
    "surface": "#181e25",
    "surface_alt": "#202832",
    "ink": "#f3f6f8",
    "muted": "#aab5c0",
    "line": "#303b46",
    "primary": "#5ba4d9",
    "primary_soft": "#19364d",
    "input": "#151b21",
    "sidebar": "#101419",
    "sidebar_text": "#f3f6f8",
    "sidebar_muted": "#aab5c0",
    "sidebar_line": "#2a333d",
}


def _theme_vars_css(values):
    return "\n".join(f"        --{name.replace('_', '-')}: {value};" for name, value in values.items())


def render_app_styles(theme_mode):
    light_vars = _theme_vars_css(LIGHT_THEME)
    dark_vars = _theme_vars_css(DARK_THEME)
    root_css = dark_vars if theme_mode == "Dark" else light_vars
    system_css = ""
    if theme_mode == "System":
        system_css = f"""
    @media (prefers-color-scheme: dark) {{
        :root {{
{dark_vars}
        }}
    }}
"""

    return f"""
<style>
    :root {{
{root_css}
        --radius-lg: 24px;
        --radius-md: 16px;
        --shadow: 0 18px 50px rgba(55, 38, 20, 0.10);
    }}
{system_css}

    .stApp {{
        background: var(--canvas);
        color: var(--ink);
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        max-width: 960px;
        padding: 3.2rem 1.2rem 1.6rem;
    }}

    h1, h2, h3, h4, h5, p, li, label, span, div {{ color: var(--ink); }}
    h1, h2, h3, h4 {{
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: -0.035em;
    }}

    .analyzer-hero {{
        position: relative;
        overflow: hidden;
        min-height: 300px;
        margin: 0 0 1rem;
        padding: clamp(1.4rem, 3vw, 2.3rem);
        border: 3px solid var(--ink);
        border-radius: 24px;
        background: var(--surface);
        box-shadow: none;
    }}

    .analyzer-hero::after {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 8px;
        height: 100%;
        background: var(--primary);
        pointer-events: none;
    }}

    .hero-topline, .hero-copy, .hero-features {{ position: relative; z-index: 1; }}
    .hero-topline {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: clamp(1.6rem, 3vw, 2.4rem);
    }}

    .analyzer-logo {{
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.055em;
        text-transform: uppercase;
    }}

    .hero-tag {{
        padding: 0.55rem 0.9rem;
        border-radius: 999px;
        background: var(--ink);
        color: var(--surface) !important;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .hero-copy {{ max-width: 950px; margin: 0 auto; text-align: center; }}
    .hero-kicker {{
        color: var(--primary) !important;
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .hero-title {{
        margin: 0.9rem auto 1.1rem;
        font-size: clamp(2.3rem, 4vw, 3.9rem);
        line-height: 1;
        font-weight: 750;
        letter-spacing: -0.075em;
    }}

    .hero-title .accent {{ color: var(--primary) !important; }}
    .hero-subtitle {{
        max-width: 640px;
        margin: 0 auto;
        color: var(--muted) !important;
        font-size: clamp(0.92rem, 1.4vw, 1.05rem);
        line-height: 1.5;
    }}

    .connection-status {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0 0 0.8rem;
        padding: 0.48rem 0.72rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--surface);
        color: var(--muted) !important;
        font-size: 0.78rem;
        font-weight: 750;
    }}
    .connection-status span {{ width: 0.55rem; height: 0.55rem; border-radius: 50%; background: #b65f56; }}
    .connection-status.connected span {{ background: #2f9e62; }}

    [data-testid="stSidebar"] {{
        width: 228px !important;
        min-width: 228px !important;
        max-width: 228px !important;
        background: var(--sidebar);
        border-right: 1px solid var(--sidebar-line);
    }}
    [data-testid="stSidebar"] > div {{ width: 228px !important; background: var(--sidebar); }}
    [data-testid="stSidebar"] * {{ color: var(--sidebar-text) !important; }}

    .nav-stage {{ display: flex; align-items: center; gap: 0.65rem; padding: 0.4rem 0.3rem 0.75rem; margin-bottom: 0.25rem; }}
    .nav-mark {{ display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; background: var(--primary); color: #ffffff !important; font-size: 0.85rem; font-weight: 900; }}
    .nav-title {{
        margin: 0;
        font-size: 0.94rem;
        font-weight: 720;
        letter-spacing: -0.018em;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        justify-content: flex-start !important;
        width: 100%;
        min-height: 2.35rem !important;
        padding: 0.55rem 0.65rem !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        background: transparent !important;
        color: var(--sidebar-text) !important;
        box-shadow: none !important;
        font-size: 0.9rem !important;
        font-weight: 650 !important;
        text-align: left !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: var(--sidebar-line) !important;
        background: var(--surface-alt) !important;
        color: var(--sidebar-text) !important;
    }}

    [data-testid="stSidebar"] .stSelectbox {{ margin-top: 0.8rem; }}
    [data-testid="stSidebar"] .stSelectbox label p {{ color: var(--sidebar-muted) !important; font-size: 0.76rem !important; font-weight: 750 !important; }}
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {{ min-height: 2.25rem !important; border-radius: 10px !important; }}

    .section-card {{
        margin: 0.25rem 0 0.65rem;
        padding: 0.85rem 1rem;
        border: 1px solid var(--line);
        border-left: 3px solid var(--primary);
        border-radius: 13px;
        background: var(--surface);
        box-shadow: 0 6px 20px rgba(15, 35, 55, 0.05);
    }}
    .section-card-title {{ font-size: 1rem; font-weight: 800; letter-spacing: -0.02em; }}
    .section-card-copy {{ margin-top: 0.2rem; color: var(--muted) !important; font-size: 0.84rem; line-height: 1.4; }}

    .info-card {{
        min-height: 142px;
        padding: 1.05rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        background: var(--surface);
    }}
    .info-card[data-tone="warm"] {{ background: var(--primary-soft); border-color: var(--line); }}
    .info-card[data-tone="teal"] {{ background: var(--primary); border-color: var(--primary); }}
    .info-card[data-tone="teal"] * {{ color: #ffffff !important; }}
    .info-card-label {{ font-size: 0.72rem; font-weight: 850; letter-spacing: 0.1em; text-transform: uppercase; }}
    .info-card-value {{ margin-top: 0.35rem; font-size: 1.75rem; font-weight: 900; letter-spacing: -0.05em; }}
    .info-card-copy {{ margin-top: 0.45rem; color: var(--muted) !important; font-size: 0.87rem; line-height: 1.4; }}
    .info-card[data-tone="warm"] .info-card-copy {{ color: var(--muted) !important; }}

    [data-testid="stForm"] {{
        padding: clamp(0.9rem, 2vw, 1.35rem);
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 10px 28px rgba(15, 35, 55, 0.06);
    }}
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox [data-baseweb="select"] > div {{
        border: 1px solid color-mix(in srgb, var(--line) 82%, var(--muted)) !important;
        border-radius: 10px !important;
        background: var(--input) !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        caret-color: var(--primary) !important;
        box-shadow: none !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px var(--primary-soft) !important;
    }}
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        opacity: 0.82;
    }}
    .stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {{ font-weight: 750 !important; }}

    .main .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
        min-height: 42px;
        border: 1px solid var(--primary) !important;
        border-radius: 999px !important;
        background: var(--primary) !important;
        color: #ffffff !important;
        box-shadow: none !important;
        font-weight: 850 !important;
    }}
    .main .stButton > button *, .stFormSubmitButton > button *, .stDownloadButton > button * {{
        color: inherit !important;
    }}
    .main .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
        border-color: var(--primary) !important;
        background: var(--primary) !important;
        color: #fff !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] {{
        padding: 0.65rem 0.8rem !important;
        border: 1px dashed var(--primary) !important;
        border-radius: 12px !important;
        background: var(--surface-alt) !important;
    }}
    .stFileUploader [data-testid="stFileUploaderDropzone"] * {{ color: var(--ink) !important; }}
    .stFileUploader [data-testid="stFileUploaderDropzone"] button {{
        border: 1px solid #191510 !important;
        border-radius: 999px !important;
        background: #fffaf2 !important;
        color: #191510 !important;
        -webkit-text-fill-color: #191510 !important;
    }}
    .stFileUploader [data-testid="stFileUploaderDropzone"] button *,
    .stFileUploader [data-testid="stFileUploaderDropzone"] button p {{
        color: #191510 !important;
        -webkit-text-fill-color: #191510 !important;
    }}
    .stFileUploader button:focus-visible,
    .main .stButton > button:focus-visible,
    .stFormSubmitButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {{
        outline: 3px solid var(--primary) !important;
        outline-offset: 3px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem;
        padding: 0.35rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--surface);
    }}
    .stTabs [data-baseweb="tab"] {{ padding: 0.65rem 0.9rem; border-radius: 13px; font-weight: 750; }}
    .stTabs [aria-selected="true"] {{ background: var(--primary-soft); color: var(--ink) !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background: transparent !important; }}

    .skill-panel, .course-card {{
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        background: var(--surface);
    }}
    .skill-panel {{ margin: 0.7rem 0 1rem; padding: 1.2rem; }}
    .skill-panel-title, .course-panel-title {{ font-size: 1.3rem; font-weight: 850; letter-spacing: -0.03em; }}
    .skill-panel-subtitle, .course-panel-subtitle {{ margin: 0.3rem 0 0.8rem; color: var(--muted) !important; line-height: 1.5; }}
    .skill-chip-row {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
    .skill-chip {{ padding: 0.42rem 0.78rem; border: 1px solid var(--line); border-radius: 999px; font-size: 0.84rem; font-weight: 700; }}
    .skill-chip-emerald, .skill-chip-blue {{ background: var(--primary-soft); color: var(--ink) !important; }}
    .skill-chip-slate {{ background: var(--ink); color: var(--surface) !important; border-color: var(--ink); }}
    .skill-chip-muted {{ color: var(--muted) !important; }}

    .course-panel {{ margin: 1rem 0; }}
    .course-grid {{ display: grid; gap: 0.7rem; margin: 0.8rem 0 1.2rem; }}
    .course-card {{ display: flex; align-items: center; gap: 0.8rem; padding: 0.9rem 1rem; text-decoration: none !important; }}
    .course-card:hover {{ border-color: var(--primary); }}
    .course-card-index {{ display: grid; place-items: center; width: 2.2rem; height: 2.2rem; border-radius: 50%; background: var(--primary-soft); color: var(--ink) !important; font-size: 0.78rem; font-weight: 850; }}
    .course-card-body {{ display: flex; flex-direction: column; flex: 1; }}
    .course-card-title {{ font-weight: 750; }}
    .course-card-meta {{ color: var(--muted) !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.07em; }}

    .stProgress > div > div > div > div {{ background: var(--primary); }}
    .stSlider [role="slider"] {{ background: var(--primary) !important; border-color: var(--primary) !important; }}
    .stExpander, [data-testid="stDataFrame"] {{ border: 1px solid var(--line) !important; border-radius: var(--radius-md) !important; overflow: hidden; }}

    header[data-testid="stHeader"] {{ background: color-mix(in srgb, var(--canvas) 92%, transparent) !important; }}
    footer {{ display: none !important; }}
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 0.7rem !important;
        left: 0.7rem !important;
        z-index: 10000 !important;
    }}
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stExpandSidebarButton"],
    button[kind="header"][aria-label*="sidebar" i] {{
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 2.6rem !important;
        height: 2.6rem !important;
        border: 1px solid var(--line) !important;
        border-radius: 50% !important;
        background: var(--primary) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18) !important;
    }}
    [data-testid="collapsedControl"] button svg,
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stExpandSidebarButton"] svg,
    button[kind="header"][aria-label*="sidebar" i] svg {{
        color: #ffffff !important;
        fill: #ffffff !important;
    }}
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{ color: #ffffff !important; }}

    @media (max-width: 760px) {{
        .main .block-container, [data-testid="stMainBlockContainer"] {{ padding: 3rem 0.65rem 1.2rem; }}
        .analyzer-hero {{ min-height: 310px; padding: 1.25rem; border-width: 2px; border-radius: 20px; }}
        .hero-topline {{ margin-bottom: 2rem; }}
        .hero-tag {{ display: none; }}
        .hero-title {{ font-size: clamp(2.25rem, 11vw, 3rem); letter-spacing: -0.055em; }}
    }}
</style>
"""


def hero_section():
    return """
    <section class="analyzer-hero">
        <div class="hero-topline">
            <div class="analyzer-logo">AI Resume Analyzer</div>
            <div class="hero-tag">Resume × Job Description</div>
        </div>
        <div class="hero-copy">
            <div class="hero-kicker">Know what your resume proves</div>
            <h1 class="hero-title">Match your resume to the <span class="accent">work you want.</span></h1>
            <p class="hero-subtitle">Compare your resume with a real job description, see the evidence behind the score, and leave with specific improvements.</p>
        </div>
    </section>
    """


def info_card(title, value, subtitle, tone="warm"):
    return f"""
    <div class="info-card" data-tone="{tone}">
        <div class="info-card-label">{title}</div>
        <div class="info-card-value">{value}</div>
        <div class="info-card-copy">{subtitle}</div>
    </div>
    """


def section_card(title, subtitle):
    return f"""
    <div class="section-card">
        <div class="section-card-title">{title}</div>
        <div class="section-card-copy">{subtitle}</div>
    </div>
    """
