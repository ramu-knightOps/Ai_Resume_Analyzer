"""Visual system and reusable HTML fragments for the Streamlit interface."""


LIGHT_THEME = {
    "canvas": "#f2e9dc",
    "surface": "#fffaf2",
    "surface_alt": "#f7ead3",
    "ink": "#191510",
    "muted": "#6f6255",
    "line": "#d7c7b5",
    "amber": "#f4ad24",
    "amber_soft": "#ffd991",
    "orange": "#e9571c",
    "input": "#fffdf8",
    "sidebar": "#1b1713",
    "sidebar_text": "#fff8ed",
    "sidebar_muted": "#cdbca8",
    "sidebar_line": "#3c3229",
}

DARK_THEME = {
    "canvas": "#110e0b",
    "surface": "#1b1713",
    "surface_alt": "#282018",
    "ink": "#fff8ed",
    "muted": "#cdbca8",
    "line": "#43372c",
    "amber": "#f7b733",
    "amber_soft": "#5a3c12",
    "orange": "#ff6b2c",
    "input": "#211b16",
    "sidebar": "#090806",
    "sidebar_text": "#fff8ed",
    "sidebar_muted": "#b8a894",
    "sidebar_line": "#332a22",
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

    .main .block-container {{
        max-width: 1240px;
        padding: 1.25rem 2rem 4rem;
    }}

    h1, h2, h3, h4, h5, p, li, label, span, div {{ color: var(--ink); }}
    h1, h2, h3, h4 {{
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: -0.035em;
    }}

    .taskoora-hero {{
        position: relative;
        overflow: hidden;
        min-height: 490px;
        margin: 0 0 1.4rem;
        padding: clamp(2rem, 5vw, 4.6rem);
        border: 7px solid var(--ink);
        border-radius: 38px;
        background: var(--surface);
        box-shadow: var(--shadow);
    }}

    .taskoora-hero::after {{
        content: "";
        position: absolute;
        inset: 20% 12% auto 12%;
        height: 48%;
        border-radius: 50%;
        background: color-mix(in srgb, var(--amber-soft) 48%, transparent);
        filter: blur(72px);
        pointer-events: none;
    }}

    .hero-topline, .hero-copy, .hero-features {{ position: relative; z-index: 1; }}
    .hero-topline {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: clamp(3rem, 7vw, 6rem);
    }}

    .taskoora-logo {{
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: -0.055em;
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
        color: var(--orange) !important;
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .hero-title {{
        margin: 0.9rem auto 1.1rem;
        font-size: clamp(3.1rem, 7.5vw, 7.5rem);
        line-height: 0.92;
        font-weight: 750;
        letter-spacing: -0.075em;
    }}

    .hero-title .accent {{ color: var(--orange) !important; }}
    .hero-subtitle {{
        max-width: 690px;
        margin: 0 auto;
        color: var(--muted) !important;
        font-size: clamp(1rem, 1.8vw, 1.18rem);
        line-height: 1.6;
    }}

    .hero-features {{
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.65rem;
        margin-top: 2rem;
    }}

    .hero-feature {{
        padding: 0.7rem 1rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--surface);
        font-size: 0.84rem;
        font-weight: 750;
    }}

    .hero-feature:first-child {{ background: var(--amber); border-color: var(--amber); color: #191510 !important; }}

    [data-testid="stSidebar"] {{
        background: var(--sidebar);
        border-right: 1px solid var(--sidebar-line);
    }}
    [data-testid="stSidebar"] > div {{ background: var(--sidebar); }}
    [data-testid="stSidebar"] * {{ color: var(--sidebar-text) !important; }}

    .nav-stage {{
        padding: 1rem 0.4rem 1.2rem;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid var(--sidebar-line);
    }}
    .nav-kicker {{
        color: var(--amber) !important;
        font-size: 0.72rem;
        font-weight: 850;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }}
    .nav-title {{
        margin: 0.4rem 0 0.55rem;
        font-size: 1.85rem;
        font-weight: 850;
        letter-spacing: -0.05em;
    }}
    .nav-copy {{ color: var(--sidebar-muted) !important; font-size: 0.9rem; line-height: 1.55; }}

    [data-testid="stSidebar"] .stButton > button {{
        justify-content: flex-start !important;
        width: 100%;
        padding: 0.78rem 0.85rem !important;
        border: 1px solid transparent !important;
        border-radius: 13px !important;
        background: transparent !important;
        color: var(--sidebar-muted) !important;
        box-shadow: none !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        text-align: left !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: var(--sidebar-line) !important;
        background: #282019 !important;
        color: var(--sidebar-text) !important;
    }}

    .theme-inline-label {{
        margin: 2.7rem 0 0.55rem;
        color: var(--muted) !important;
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }}
    .theme-switcher-module__q-SprW__root {{ height: 0; }}
    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] div[role="radiogroup"] {{
        display: inline-flex;
        gap: 0.2rem;
        padding: 0.22rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--surface-alt);
    }}
    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: auto;
        height: 30px;
        min-width: 54px;
        margin: 0;
        padding: 0 0.7rem;
        border-radius: 999px;
        cursor: pointer;
    }}
    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label:has(input:checked) {{
        border-radius: 999px;
        background: var(--ink);
        color: var(--surface) !important;
    }}
    .theme-switcher-module__q-SprW__root + div[data-testid="stRadio"] label p {{ color: inherit !important; }}

    .section-card {{
        margin: 0.6rem 0 1rem;
        padding: 1.25rem 1.35rem;
        border: 1px solid var(--line);
        border-left: 6px solid var(--orange);
        border-radius: var(--radius-md);
        background: var(--surface);
    }}
    .section-card-title {{ font-size: 1.25rem; font-weight: 850; letter-spacing: -0.025em; }}
    .section-card-copy {{ margin-top: 0.35rem; color: var(--muted) !important; font-size: 0.94rem; line-height: 1.5; }}

    .info-card {{
        min-height: 142px;
        padding: 1.05rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        background: var(--surface);
    }}
    .info-card[data-tone="warm"] {{ background: var(--amber); border-color: var(--amber); }}
    .info-card[data-tone="teal"] {{ background: var(--orange); border-color: var(--orange); }}
    .info-card[data-tone="teal"] * {{ color: #fffaf2 !important; }}
    .info-card-label {{ font-size: 0.72rem; font-weight: 850; letter-spacing: 0.1em; text-transform: uppercase; }}
    .info-card-value {{ margin-top: 0.35rem; font-size: 1.75rem; font-weight: 900; letter-spacing: -0.05em; }}
    .info-card-copy {{ margin-top: 0.45rem; color: var(--muted) !important; font-size: 0.87rem; line-height: 1.4; }}
    .info-card[data-tone="warm"] .info-card-copy {{ color: #5f4210 !important; }}

    [data-testid="stForm"] {{
        padding: clamp(1.1rem, 3vw, 2rem);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        background: var(--surface);
    }}
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox [data-baseweb="select"] > div {{
        border: 1px solid var(--line) !important;
        border-radius: 13px !important;
        background: var(--input) !important;
        color: var(--ink) !important;
        box-shadow: none !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{ border-color: var(--orange) !important; }}
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {{ color: var(--muted) !important; opacity: 0.8; }}
    .stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {{ font-weight: 750 !important; }}

    .main .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
        min-height: 48px;
        border: 2px solid var(--ink) !important;
        border-radius: 999px !important;
        background: var(--ink) !important;
        color: var(--surface) !important;
        box-shadow: none !important;
        font-weight: 850 !important;
    }}
    .main .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
        border-color: var(--orange) !important;
        background: var(--orange) !important;
        color: #fff !important;
    }}

    .stFileUploader [data-testid="stFileUploaderDropzone"] {{
        padding: 1rem !important;
        border: 2px dashed var(--amber) !important;
        border-radius: var(--radius-md) !important;
        background: var(--surface-alt) !important;
    }}
    .stFileUploader [data-testid="stFileUploaderDropzone"] * {{ color: var(--ink) !important; }}
    .stFileUploader button {{
        border: 1px solid var(--ink) !important;
        border-radius: 999px !important;
        background: var(--ink) !important;
        color: var(--surface) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem;
        padding: 0.35rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--surface);
    }}
    .stTabs [data-baseweb="tab"] {{ padding: 0.65rem 0.9rem; border-radius: 13px; font-weight: 750; }}
    .stTabs [aria-selected="true"] {{ background: var(--amber-soft); color: var(--ink) !important; }}
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
    .skill-chip-emerald {{ background: var(--amber-soft); color: var(--ink) !important; }}
    .skill-chip-amber {{ background: var(--amber); color: #191510 !important; }}
    .skill-chip-slate {{ background: var(--ink); color: var(--surface) !important; border-color: var(--ink); }}
    .skill-chip-muted {{ color: var(--muted) !important; }}

    .course-panel {{ margin: 1rem 0; }}
    .course-grid {{ display: grid; gap: 0.7rem; margin: 0.8rem 0 1.2rem; }}
    .course-card {{ display: flex; align-items: center; gap: 0.8rem; padding: 0.9rem 1rem; text-decoration: none !important; }}
    .course-card:hover {{ border-color: var(--orange); }}
    .course-card-index {{ display: grid; place-items: center; width: 2.2rem; height: 2.2rem; border-radius: 50%; background: var(--amber); color: #191510 !important; font-size: 0.78rem; font-weight: 850; }}
    .course-card-body {{ display: flex; flex-direction: column; flex: 1; }}
    .course-card-title {{ font-weight: 750; }}
    .course-card-meta {{ color: var(--muted) !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.07em; }}

    .stProgress > div > div > div > div {{ background: var(--orange); }}
    .stSlider [role="slider"] {{ background: var(--orange) !important; border-color: var(--orange) !important; }}
    .stExpander, [data-testid="stDataFrame"] {{ border: 1px solid var(--line) !important; border-radius: var(--radius-md) !important; overflow: hidden; }}

    header[data-testid="stHeader"] {{ background: color-mix(in srgb, var(--canvas) 92%, transparent) !important; }}
    div[data-testid="stToolbar"] {{ visibility: hidden; }}
    footer {{ display: none !important; }}
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {{ position: fixed !important; top: 0.75rem !important; left: 0.75rem !important; z-index: 10000 !important; }}

    @media (max-width: 760px) {{
        .main .block-container {{ padding: 1rem 0.8rem 3rem; }}
        .taskoora-hero {{ min-height: 440px; padding: 1.5rem; border-width: 5px; border-radius: 28px; }}
        .hero-topline {{ margin-bottom: 4rem; }}
        .hero-tag {{ display: none; }}
        .hero-title {{ font-size: clamp(3.25rem, 16vw, 5rem); }}
    }}
</style>
"""


def hero_section():
    return """
    <section class="taskoora-hero">
        <div class="hero-topline">
            <div class="taskoora-logo">Taskoora</div>
            <div class="hero-tag">Resume × Job Description</div>
        </div>
        <div class="hero-copy">
            <div class="hero-kicker">Know what your resume proves</div>
            <h1 class="hero-title">Match your resume to the <span class="accent">work you want.</span></h1>
            <p class="hero-subtitle">Compare your resume with a real job description, see the evidence behind the score, and leave with specific improvements.</p>
        </div>
        <div class="hero-features">
            <span class="hero-feature">ATS structure</span>
            <span class="hero-feature">Requirement evidence</span>
            <span class="hero-feature">PDF report</span>
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
