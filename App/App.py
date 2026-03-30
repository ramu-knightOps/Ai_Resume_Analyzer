


###### Packages Used ######
import streamlit as st # core package used in this project
import streamlit.components.v1 as components
import pandas as pd
import base64, random
import time,datetime
import psycopg2
import html
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
# libraries used to parse the pdf files
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
from parser_utils import parse_resume_document
from resume_analysis_core import build_full_analysis, build_pdf_report_bytes
from ui_styles import hero_section, info_card, render_app_styles, section_card
import nltk
nltk.download('stopwords')


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="500" type="application/pdf" style="border-radius: 10px; border: 2px solid #1ed760;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.markdown('<section class="course-panel"><div class="course-panel-title">Recommended Courses &amp; Certifications</div><div class="course-panel-subtitle">A curated learning stack to strengthen the signal for your target direction.</div></section>', unsafe_allow_html=True)
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    course_cards = []
    for c_name, c_link in course_list:
        c += 1
        rec_course.append(c_name)
        escaped_link = html.escape(c_link, quote=True)
        escaped_name = html.escape(c_name)
        course_cards.append(
            f'<a class="course-card" href="{escaped_link}" target="_blank" rel="noopener noreferrer">'
            f'<span class="course-card-index">{c:02d}</span>'
            f'<span class="course-card-body">'
            f'<span class="course-card-title">{escaped_name}</span>'
            f'<span class="course-card-meta">Open course ↗</span>'
            f'</span></a>'
        )
        if c == no_of_reco:
            break
    cards_html = "".join(course_cards)
    st.markdown(f"<div class='course-grid'>{cards_html}</div>", unsafe_allow_html=True)
    return rec_course


COURSE_LIBRARY = {
    'data_science': ds_course,
    'web': web_course,
    'android': android_course,
    'ios': ios_course,
    'uiux': uiux_course,
}

# Styled bullet point helpers
def success_bullet(text):
    """Display a success (green) styled bullet point"""
    st.markdown(f'''
    <div style="padding: 12px 15px; margin: 8px 0; background: linear-gradient(135deg, rgba(34, 197, 94, 0.16) 0%, rgba(34, 197, 94, 0.07) 100%); 
    border-left: 4px solid #22c55e; border-radius: 14px;">
        <span style="color: #22c55e; font-weight: 600;">✓</span>
        <span style="color: var(--ink); margin-left: 10px; font-weight: 600;">{text}</span>
    </div>
    ''', unsafe_allow_html=True)

def warning_bullet(text):
    """Display a warning (orange) styled bullet point"""
    st.markdown(f'''
    <div style="padding: 12px 15px; margin: 8px 0; background: linear-gradient(135deg, rgba(251, 146, 60, 0.14) 0%, rgba(251, 146, 60, 0.05) 100%); 
    border-left: 4px solid #fb923c; border-radius: 14px;">
        <span style="color: #fb923c; font-weight: 600;">○</span>
        <span style="color: var(--ink); margin-left: 10px; font-weight: 600;">{text}</span>
    </div>
    ''', unsafe_allow_html=True)


def render_skill_panel(title, subtitle, items, tone="emerald"):
    chip_html = "".join(
        f"<span class='skill-chip skill-chip-{tone}'>{html.escape(str(item))}</span>"
        for item in items
    )
    st.markdown(
        f"""
        <section class="skill-panel">
            <div class="skill-panel-title">{html.escape(title)}</div>
            <div class="skill-panel-subtitle">{html.escape(subtitle)}</div>
            <div class="skill-chip-row">{chip_html or "<span class='skill-chip skill-chip-muted'>No items</span>"}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_scorecards(section_scores):
    for section in section_scores:
        st.markdown(
            section_card(
                section["category"],
                f"{section['matched_checks']} of {section['total_checks']} checks matched · {section['score']}/{section['max_score']} points",
            ),
            unsafe_allow_html=True,
        )
        st.progress(min(max(section["percent"] / 100, 0.0), 1.0))
        st.caption(f"Coverage score: {section['percent']}%")
        matched_labels = [item["label"] for item in section["checks"] if item["matched"]]
        missing_labels = [item["label"] for item in section["checks"] if not item["matched"]]
        if matched_labels:
            render_skill_panel("Already covered", "Strong signals already present in your resume.", matched_labels, tone="emerald")
        if missing_labels:
            render_skill_panel("Still missing", "Sections to strengthen in the next revision.", missing_labels, tone="amber")


def render_bullet_quality_panel(bullet_quality):
    st.markdown(section_card("Bullet quality checker", bullet_quality["summary"]), unsafe_allow_html=True)
    if not bullet_quality["flagged_bullets"]:
        st.success("No weak bullet patterns were detected in the parsed resume text.")
        return

    for finding in bullet_quality["flagged_bullets"]:
        issues = ", ".join(finding["issues"])
        st.markdown(
            f"""
            <div style="padding:1rem 1.1rem; border-radius:20px; background:var(--card-bg);
                border:1px solid var(--line); box-shadow:var(--shadow); margin:0 0 1rem 0;">
                <div style="font-size:0.82rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--accent-3); font-weight:700;">Flagged Bullet</div>
                <div style="margin-top:0.55rem; font-size:1rem; font-weight:700; color:var(--ink);">{html.escape(finding['original'])}</div>
                <div style="margin-top:0.55rem; font-size:0.92rem; color:var(--muted);">Issues: {html.escape(issues)}</div>
                <div style="margin-top:0.75rem; font-size:0.9rem; color:var(--accent-2); font-weight:700;">Suggested rewrite</div>
                <div style="margin-top:0.3rem; font-size:0.95rem; color:var(--ink);">{html.escape(finding['suggestion'])}</div>
                <div style="margin-top:0.55rem; font-size:0.9rem; color:var(--muted);">{html.escape(finding['coaching_tip'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_gap_explainer_panel(gap_explainer):
    st.markdown(section_card("Resume-to-JD gap explainer", gap_explainer["summary"]), unsafe_allow_html=True)
    categorized = gap_explainer["categorized_missing_keywords"]
    if not categorized:
        st.success("No major gap categories were detected from the JD.")
        return

    gap_cols = st.columns(2)
    gap_items = list(categorized.items())
    for index, (category, items) in enumerate(gap_items):
        with gap_cols[index % 2]:
            render_skill_panel(
                category,
                "Keywords from the JD that are not yet clearly proven in the resume.",
                items,
                tone="slate" if category in {"Domain", "Evidence"} else "emerald",
            )


def render_interview_prep_panel(interview_prep):
    st.markdown(section_card("Interview prep from JD", "Pattern-based questions generated from the JD and your current skills."), unsafe_allow_html=True)
    tech_col, project_col, behavior_col = st.columns(3)
    groups = [
        ("Technical", interview_prep.get("technical_questions", []), tech_col),
        ("Project", interview_prep.get("project_questions", []), project_col),
        ("Behavioral", interview_prep.get("behavioral_questions", []), behavior_col),
    ]
    for title, questions, column in groups:
        with column:
            st.markdown(f"#### {title}")
            if questions:
                for question in questions:
                    warning_bullet(question)
            else:
                st.info("Add a target JD to unlock this section.")


def render_semantic_evidence_panel(semantic_results):
    st.markdown(section_card("Semantic evidence", "Recovered resume signals and top JD-aligned capabilities used by the matcher."), unsafe_allow_html=True)

    evidence_col1, evidence_col2 = st.columns(2)
    with evidence_col1:
        strengths = [item["skill"] for item in semantic_results.get("resume_skill_evidence", [])[:12]]
        render_skill_panel(
            "Recovered Resume Strengths",
            "Signals detected from parser output and full resume text.",
            strengths,
            tone="emerald",
        )

    with evidence_col2:
        jd_matches = [
            f'{item["skill"]} · {item["score"]}%'
            for item in semantic_results.get("jd_skill_matches", [])[:12]
            if item.get("present_in_resume")
        ]
        if jd_matches:
            render_skill_panel(
                "JD Signals Already Covered",
                "Capabilities the semantic matcher found in both the JD and your resume.",
                jd_matches,
                tone="slate",
            )
        else:
            st.info("No strong shared JD signals were recovered yet.")


def build_admin_metric_card(title, value, subtitle, tone="warm"):
    return info_card(title, value, subtitle, tone)


def get_chart_theme_settings(theme_mode):
    is_dark = theme_mode == "Dark"
    return {
        "template": "plotly_dark" if is_dark else "plotly_white",
        "font_color": "#e5eef8" if is_dark else "#1f2933",
        "muted_color": "#b2c0d0" if is_dark else "#52606d",
        "grid_color": "rgba(203, 213, 225, 0.16)" if is_dark else "rgba(31, 41, 51, 0.12)",
        "paper_bg": "rgba(9,17,26,0)" if is_dark else "rgba(255,255,255,0)",
        "plot_bg": "rgba(9,17,26,0)" if is_dark else "rgba(255,255,255,0)",
        "bar_line": "rgba(255,255,255,0.12)" if is_dark else "rgba(31,41,51,0.18)",
    }


def apply_chart_theme(figure, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    figure.update_layout(
        template=chart_theme["template"],
        paper_bgcolor=chart_theme["paper_bg"],
        plot_bgcolor=chart_theme["plot_bg"],
        font=dict(color=chart_theme["font_color"]),
        title_font=dict(color=chart_theme["font_color"], size=18),
        legend=dict(font=dict(color=chart_theme["font_color"])),
    )
    figure.update_xaxes(
        showgrid=True,
        gridcolor=chart_theme["grid_color"],
        zeroline=False,
        color=chart_theme["font_color"],
        title_font=dict(color=chart_theme["font_color"]),
        tickfont=dict(color=chart_theme["font_color"]),
    )
    figure.update_yaxes(
        showgrid=False,
        zeroline=False,
        color=chart_theme["font_color"],
        title_font=dict(color=chart_theme["font_color"]),
        tickfont=dict(color=chart_theme["font_color"]),
    )
    return figure


def build_ranked_bar_chart(dataframe, column_name, title, color_scale, theme_mode, limit=6):
    chart_theme = get_chart_theme_settings(theme_mode)
    series = (
        dataframe[column_name]
        .fillna("Unknown")
        .astype(str)
        .replace("", "Unknown")
        .value_counts()
        .head(limit)
        .sort_values(ascending=True)
    )
    figure = go.Figure(
        go.Bar(
            x=series.values,
            y=series.index,
            orientation="h",
            marker=dict(
                color=series.values,
                colorscale=color_scale,
                line=dict(color=chart_theme["bar_line"], width=1),
            ),
            text=series.values,
            textposition="outside",
            textfont=dict(color=chart_theme["font_color"]),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    figure.update_layout(
        title=title,
        height=320,
        margin=dict(l=10, r=20, t=56, b=10),
        xaxis_title="Count",
        yaxis_title="",
    )
    return apply_chart_theme(figure, theme_mode)


def build_score_distribution_chart(dataframe, theme_mode):
    scores = pd.to_numeric(dataframe["resume_score"], errors="coerce").dropna()
    if scores.empty:
        scores = pd.Series([0], dtype=float)
    figure = go.Figure(
        go.Histogram(
            x=scores,
            nbinsx=10,
            marker=dict(
                color="rgba(15, 118, 110, 0.78)",
                line=dict(color="rgba(15, 118, 110, 1)", width=1),
            ),
            hovertemplate="Score %{x}<br>Count %{y}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Resume Score Distribution",
        height=320,
        margin=dict(l=10, r=20, t=56, b=10),
        xaxis_title="Resume score",
        yaxis_title="Profiles",
        bargap=0.08,
    )
    return apply_chart_theme(figure, theme_mode)


def build_feedback_mix_chart(feedback_df, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    ratings = pd.to_numeric(feedback_df["Feedback Score"], errors="coerce").dropna()
    if ratings.empty:
        ratings = pd.Series([0], dtype=float)
    counts = ratings.astype(int).value_counts().sort_index()
    figure = go.Figure(
        go.Scatterpolar(
            r=counts.values.tolist(),
            theta=[f"{index} Star" for index in counts.index.tolist()],
            fill="toself",
            line=dict(color="rgba(217, 119, 6, 0.9)", width=3),
            marker=dict(size=8, color="rgba(217, 119, 6, 0.9)"),
            hovertemplate="%{theta}: %{r}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Feedback Rating Mix",
        height=320,
        margin=dict(l=20, r=20, t=56, b=20),
        polar=dict(
            bgcolor=chart_theme["plot_bg"],
            radialaxis=dict(
                visible=True,
                showline=False,
                gridcolor=chart_theme["grid_color"],
                color=chart_theme["font_color"],
                tickfont=dict(color=chart_theme["font_color"]),
            ),
            angularaxis=dict(
                color=chart_theme["font_color"],
                tickfont=dict(color=chart_theme["font_color"]),
            ),
        ),
    )
    return apply_chart_theme(figure, theme_mode)


def build_level_mix_chart(dataframe, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    series = (
        dataframe["User_Level"]
        .fillna("Unknown")
        .astype(str)
        .replace("", "Unknown")
        .value_counts()
    )
    figure = go.Figure(
        go.Pie(
            labels=series.index,
            values=series.values,
            hole=0.62,
            marker=dict(colors=["#0f766e", "#d97706", "#1f2933", "#94a3b8"]),
            textinfo="label+percent",
            textfont=dict(color=chart_theme["font_color"]),
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Candidate Seniority Mix",
        height=320,
        margin=dict(l=20, r=20, t=56, b=20),
        showlegend=False,
    )
    return apply_chart_theme(figure, theme_mode)


def build_admin_console(plot_data, users_df, feedback_df, theme_mode):
    plot_data = plot_data.copy()
    plot_data["resume_score_num"] = pd.to_numeric(plot_data["resume_score"], errors="coerce")
    total_profiles = int(len(plot_data))
    average_score = float(plot_data["resume_score_num"].dropna().mean()) if total_profiles else 0.0
    top_track = (
        plot_data["Predicted_Field"].fillna("Unknown").astype(str).value_counts().idxmax()
        if total_profiles else "No data"
    )
    total_feedback = int(len(feedback_df))
    average_rating = float(pd.to_numeric(feedback_df["Feedback Score"], errors="coerce").dropna().mean()) if total_feedback else 0.0

    st.markdown(section_card("Admin Console v2", "Professional analytics for candidate flow, score quality, geography, and feedback."), unsafe_allow_html=True)
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.markdown(build_admin_metric_card("Profiles Reviewed", f"{total_profiles}", "Total resumes processed in the system.", "teal"), unsafe_allow_html=True)
    with metric_col2:
        st.markdown(build_admin_metric_card("Average Score", f"{average_score:.1f}", "Mean resume quality score across all uploads.", "warm"), unsafe_allow_html=True)
    with metric_col3:
        st.markdown(build_admin_metric_card("Top Talent Track", top_track, "Most frequently predicted role family.", "ink"), unsafe_allow_html=True)
    with metric_col4:
        st.markdown(build_admin_metric_card("Feedback Pulse", f"{average_rating:.1f}/5", "Average feedback rating from submitted reviews.", "teal"), unsafe_allow_html=True)

    dashboard_tabs = st.tabs(["Overview", "Talent Signals", "Geo & Feedback", "Data Tables"])

    with dashboard_tabs[0]:
        overview_col1, overview_col2 = st.columns(2)
        with overview_col1:
            st.plotly_chart(
                build_ranked_bar_chart(plot_data, "Predicted_Field", "Top Predicted Role Tracks", "Tealgrn", theme_mode),
                use_container_width=True,
            )
        with overview_col2:
            st.plotly_chart(build_score_distribution_chart(plot_data, theme_mode), use_container_width=True)

    with dashboard_tabs[1]:
        talent_col1, talent_col2 = st.columns(2)
        with talent_col1:
            st.plotly_chart(build_level_mix_chart(plot_data, theme_mode), use_container_width=True)
        with talent_col2:
            st.plotly_chart(
                build_ranked_bar_chart(plot_data, "City", "Top Candidate Cities", "Sunsetdark", theme_mode),
                use_container_width=True,
            )

        st.plotly_chart(
            build_ranked_bar_chart(plot_data, "State", "Regional Distribution by State", "Burgyl", theme_mode),
            use_container_width=True,
        )

    with dashboard_tabs[2]:
        feedback_col1, feedback_col2 = st.columns(2)
        with feedback_col1:
            st.plotly_chart(build_feedback_mix_chart(feedback_df, theme_mode), use_container_width=True)
        with feedback_col2:
            st.plotly_chart(
                build_ranked_bar_chart(plot_data, "Country", "Country Footprint", "Mint", theme_mode),
                use_container_width=True,
            )

        st.markdown(section_card("Feedback stream", "Latest comments collected from users."), unsafe_allow_html=True)
        if feedback_df.empty:
            st.info("No feedback has been recorded yet.")
        else:
            recent_feedback = feedback_df.sort_values("Timestamp", ascending=False).head(8)
            st.dataframe(recent_feedback[["Name", "Feedback Score", "Comments", "Timestamp"]], use_container_width=True)

    with dashboard_tabs[3]:
        data_tab1, data_tab2 = st.tabs(["Candidate Records", "Feedback Records"])
        with data_tab1:
            st.markdown(section_card("Candidate records", "Detailed candidate and system metadata with CSV export."), unsafe_allow_html=True)
            st.dataframe(users_df, use_container_width=True, height=380)
            st.markdown(get_csv_download_link(users_df, 'User_Data.csv', 'Download Candidate Report'), unsafe_allow_html=True)
        with data_tab2:
            st.markdown(section_card("Feedback records", "All submitted ratings and comments in one table."), unsafe_allow_html=True)
            st.dataframe(feedback_df, use_container_width=True, height=320)


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


###### Database Stuffs ######

load_dotenv()


def get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value


def get_env_or_default(name, default_value):
    value = os.getenv(name)
    return value if value else default_value


def parse_admin_credentials():
    raw_credentials = os.getenv('ADMIN_CREDENTIALS', '').strip()
    if raw_credentials:
        credentials = {}
        for pair in raw_credentials.split(','):
            if ':' not in pair:
                continue
            username, password = pair.split(':', 1)
            username = username.strip()
            password = password.strip()
            if username and password:
                credentials[username] = password
        if credentials:
            return credentials

    primary_username = os.getenv('ADMIN_USERNAME', '').strip()
    primary_password = os.getenv('ADMIN_PASSWORD', '').strip()
    if primary_username and primary_password:
        return {primary_username: primary_password}
    return {}


# PostgreSQL connector
connection = psycopg2.connect(
    host=get_required_env('DB_HOST'),
    port=get_required_env('DB_PORT'),
    database=get_required_env('DB_NAME'),
    user=get_required_env('DB_USER'),
    password=get_required_env('DB_PASSWORD')
)
cursor = connection.cursor()
ADMIN_CREDENTIALS = parse_admin_credentials()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """ 
    (sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country, act_name, act_mail, act_mob, name, email_id, resume_score, timestamp, page_no, predicted_field, user_level, actual_skills, recommended_skills, recommended_courses, pdf_name)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    (feed_name, feed_email, feed_score, comments, timestamp)
    values (%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="Resume Analyzer",
   page_icon="📄",
   layout="wide",
   initial_sidebar_state="expanded",
)

###### Main function run() ######


def run():
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = "System"
    if 'theme_selector' not in st.session_state:
        st.session_state.theme_selector = "◫"

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

    st.markdown(render_app_styles(st.session_state.theme_mode), unsafe_allow_html=True)
    ensure_sidebar_open()

    if 'nav_choice' not in st.session_state:
        st.session_state.nav_choice = "User"

    with st.container():
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

    nav_options = ["User", "Feedback", "About", "Admin"]
    nav_labels = {
        "User": "Candidate Studio",
        "Feedback": "Signal & Feedback",
        "About": "About The Engine",
        "Admin": "Admin Atlas",
    }

    def _set_nav(target):
        st.session_state.nav_choice = target

    def _format_nav(key):
        idx = nav_options.index(key) + 1
        prefix = "◆" if st.session_state.get("nav_choice") == key else f"{idx:02d}"
        return f"{prefix}  {nav_labels[key]}"

    st.sidebar.markdown(f"""
    <div class='nav-stage'>
        <div class='nav-kicker'>Control Deck</div>
        <div class='nav-title'>Navigation</div>
        <div class='nav-copy'>Move through the analyzer like chapters in a compact studio console.</div>
        <div class='nav-orbit'></div>
    </div>
    """, unsafe_allow_html=True)

    for nav_key in nav_options:
        st.sidebar.button(
            _format_nav(nav_key),
            key=f"nav_{nav_key.lower()}",
            use_container_width=True,
            on_click=_set_nav,
            args=(nav_key,),
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='padding: 12px 4px 2px 4px;'>
        <div style='font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.7;'>Studio Notes</div>
        <div style='margin-top: 10px; font-size: 1rem; font-weight: 700;'>Career intelligence</div>
        <div style='font-size: 0.95rem; opacity: 0.86; margin-top: 8px;'>Compare resumes to target roles with role-fit analysis and focused skill advice.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(hero_section(), unsafe_allow_html=True)

    choice = st.session_state.get("nav_choice", "User")

    user_table_sql = """
        CREATE TABLE IF NOT EXISTS user_data (
            ID SERIAL PRIMARY KEY,
            sec_token VARCHAR(20) NOT NULL,
            ip_add VARCHAR(50) NULL,
            host_name VARCHAR(50) NULL,
            dev_user VARCHAR(50) NULL,
            os_name_ver VARCHAR(50) NULL,
            latlong VARCHAR(50) NULL,
            city VARCHAR(50) NULL,
            state VARCHAR(50) NULL,
            country VARCHAR(50) NULL,
            act_name VARCHAR(50) NOT NULL,
            act_mail VARCHAR(50) NOT NULL,
            act_mob VARCHAR(20) NOT NULL,
            Name VARCHAR(500) NOT NULL,
            Email_ID VARCHAR(500) NOT NULL,
            resume_score VARCHAR(8) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            Page_no VARCHAR(5) NOT NULL,
            Predicted_Field TEXT NOT NULL,
            User_level TEXT NOT NULL,
            Actual_skills TEXT NOT NULL,
            Recommended_skills TEXT NOT NULL,
            Recommended_courses TEXT NOT NULL,
            pdf_name VARCHAR(50) NOT NULL
        );
    """
    feedback_table_sql = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            ID SERIAL PRIMARY KEY,
            feed_name VARCHAR(50) NOT NULL,
            feed_email VARCHAR(50) NOT NULL,
            feed_score VARCHAR(5) NOT NULL,
            comments VARCHAR(100) NULL,
            Timestamp VARCHAR(50) NOT NULL
        );
    """
    cursor.execute(user_table_sql)
    cursor.execute(feedback_table_sql)
    connection.commit()

    if choice == 'User':
        st.markdown(section_card("Candidate workspace", "Upload a resume, add a job description, and get a more realistic fit review."), unsafe_allow_html=True)
        form_col1, form_col2, form_col3 = st.columns(3)
        with form_col1:
            act_name = st.text_input('Name*')
        with form_col2:
            act_mail = st.text_input('Mail*')
        with form_col3:
            act_mob = st.text_input('Mobile Number*')

        job_description = st.text_area(
            'Target Job Description',
            height=180,
            placeholder='Paste a job description here to unlock semantic role search, fit scoring, and skill-gap analysis.'
        )

        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        city = ''
        state = ''
        country = ''
        latlong = []
        try:
            g = geocoder.ip('me')
            latlong = g.latlng
            if latlong:
                geolocator = Nominatim(user_agent="http")
                location = geolocator.reverse(latlong, language='en')
                address = location.raw['address']
                city = address.get('city', '')
                state = address.get('state', '')
                country = address.get('country', '')
        except Exception:
            pass

        st.markdown(
            """<h5 style='text-align: left; color: #0f766e; font-weight: 700;'>
            Upload your resume and unlock targeted recommendations
            </h5>""",
            unsafe_allow_html=True
        )
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Analyzing resume, matching role intent, and preparing recommendations...'):
                time.sleep(2)

            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as file_handle:
                file_handle.write(pdf_file.getbuffer())

            resume_text = pdf_reader(save_image_path)
            resume_data = parse_resume_document(save_image_path, resume_text)
            if resume_data:
                analysis = build_full_analysis(resume_data, resume_text, job_description)
                resume_skills = analysis["candidate"]["skills"]
                summary = analysis["summary"]
                semantic_results = analysis["semantic_results"]
                semantic_error = analysis["semantic_error"]
                recommended_skills = summary["recommended_skills"]
                reco_field = summary["career_track"]
                candidate_level = analysis["candidate"]["candidate_level"]
                resume_score = summary["resume_score"]

                st.header("Resume report")
                st.success("Hello " + (analysis["candidate"]["name"] or act_name or 'there'))

                summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                with summary_col1:
                    st.markdown(info_card("Resume score", f"{resume_score}/100", "Weighted from key sections found in the resume.", "warm"), unsafe_allow_html=True)
                with summary_col2:
                    st.markdown(info_card("Career track", summary["career_track"], summary["role_title"], "teal"), unsafe_allow_html=True)
                with summary_col3:
                    st.markdown(info_card("Candidate level", candidate_level, f"{analysis['candidate']['page_count']} page resume", "ink"), unsafe_allow_html=True)
                with summary_col4:
                    semantic_score = f"{summary['semantic_match_score']}%" if summary["semantic_match_score"] is not None else "N/A"
                    semantic_note = "Based on your pasted JD." if semantic_results else "Add a JD to unlock matching."
                    st.markdown(info_card("JD match", semantic_score, semantic_note, "warm"), unsafe_allow_html=True)

                report_tabs = st.tabs([
                    "Overview",
                    "ATS Sections",
                    "JD Gap",
                    "Bullet Checker",
                    "Interview Prep",
                    "PDF Report",
                ])

                with report_tabs[0]:
                    st.markdown(section_card("Candidate snapshot", "Core details extracted from the uploaded resume."), unsafe_allow_html=True)
                    info_col1, info_col2 = st.columns([1.2, 1])
                    with info_col1:
                        st.markdown(analysis["candidate"]["highlights"])
                        st.write(f"Name: {analysis['candidate']['name']}")
                        st.write(f"Email: {analysis['candidate']['email']}")
                        st.write(f"Contact: {analysis['candidate']['mobile_number']}")
                        st.write(f"Degree: {analysis['candidate']['degree'] or 'Not found'}")
                    with info_col2:
                        show_pdf(save_image_path)

                    st.markdown(section_card("Skill intelligence", "Detected skills, likely track, and the strongest next-signal upgrades."), unsafe_allow_html=True)
                    render_skill_panel(
                        "Your Current Skills",
                        "Detected directly from your resume",
                        resume_skills,
                        tone="emerald",
                    )
                    st.info(
                        f"Our analysis suggests you are trending toward {summary['role_title']} roles. "
                        f"{summary['match_reason']}"
                    )
                    render_skill_panel(
                        "Recommended Skills For Your Next Iteration",
                        "Add the strongest missing signals to improve role fit",
                        recommended_skills,
                        tone="amber",
                    )
                    rec_course = course_recommender(COURSE_LIBRARY.get(summary["courses_key"], ds_course))

                    if semantic_results:
                        st.markdown(section_card("Job match", "Embeddings compare your resume, the pasted JD, and curated role profiles."), unsafe_allow_html=True)
                        match_cols = st.columns(len(semantic_results['role_matches']))
                        for index, role in enumerate(semantic_results['role_matches']):
                            with match_cols[index]:
                                st.markdown(
                                    info_card(
                                        role['title'],
                                        f"{role['score']}%",
                                        role['summary'],
                                        "teal" if index == 0 else "ink"
                                    ),
                                    unsafe_allow_html=True
                                )
                        render_semantic_evidence_panel(semantic_results)
                    elif semantic_error:
                        st.warning(
                            "Semantic matching could not start yet. Install the embedding dependencies and ensure the model can download. "
                            f"Details: {semantic_error}"
                        )
                    else:
                        st.info("Paste a target job description above to unlock semantic role matching.")

                with report_tabs[1]:
                    st.markdown(section_card("Section-level ATS score", "The original 10 ATS checks are grouped into scored categories with visual bars."), unsafe_allow_html=True)
                    render_section_scorecards(analysis["ats_section_scores"])
                    st.markdown(section_card("Detailed ATS checklist", "A weighted review of the sections recruiters usually expect to see."), unsafe_allow_html=True)
                    for check in analysis["ats_checks"]:
                        if check['matched']:
                            success_bullet(check['success'])
                        else:
                            warning_bullet(check['warning'])
                    st.subheader("Your Resume Score")
                    st.progress(resume_score / 100)
                    st.success('Your resume writing score is ' + str(resume_score) + '/100')
                    st.caption("This score is based on section coverage and positioning cues found in the uploaded resume.")

                with report_tabs[2]:
                    render_gap_explainer_panel(analysis["gap_explainer"])
                    if semantic_results:
                        detail_col1, detail_col2 = st.columns(2)
                        with detail_col1:
                            render_skill_panel(
                                "Missing JD Keywords",
                                "Keywords from the JD that do not yet appear clearly in your resume skills.",
                                semantic_results['missing_keywords'],
                                tone="slate",
                            )
                        with detail_col2:
                            render_skill_panel(
                                "Priority Keywords",
                                "High-signal terms worth proving with projects, bullets, or skills.",
                                semantic_results['priority_keywords'],
                                tone="emerald",
                            )
                        if semantic_results.get("jd_skill_matches"):
                            evidence_rows = pd.DataFrame(semantic_results["jd_skill_matches"])
                            evidence_rows["present_in_resume"] = evidence_rows["present_in_resume"].map({True: "Yes", False: "No"})
                            st.markdown(section_card("Vector search matches", "JD-aligned capabilities ranked by semantic similarity and resume coverage."), unsafe_allow_html=True)
                            st.dataframe(
                                evidence_rows.rename(
                                    columns={
                                        "skill": "Capability",
                                        "category": "Category",
                                        "score": "Semantic Score",
                                        "present_in_resume": "Found In Resume",
                                    }
                                ),
                                use_container_width=True,
                                height=320,
                            )
                    else:
                        st.info("Add a target JD to unlock the resume-to-JD gap explainer.")

                with report_tabs[3]:
                    render_bullet_quality_panel(analysis["bullet_quality"])

                with report_tabs[4]:
                    render_interview_prep_panel(analysis["interview_prep"])

                with report_tabs[5]:
                    st.markdown(section_card("PDF report export", "Download the full analysis summary as a PDF report."), unsafe_allow_html=True)
                    pdf_report_bytes = build_pdf_report_bytes("Resume Analysis Report", analysis)
                    st.download_button(
                        "Download PDF Report",
                        data=pdf_report_bytes,
                        file_name=f"{os.path.splitext(pdf_name)[0]}-analysis-report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.caption("The export includes ATS section scores, bullet rewrite guidance, JD gap summary, and interview prep prompts.")

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                insert_data(
                    str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, latlong,
                    city, state, country, act_name, act_mail, act_mob,
                    resume_data.get('name', ''), resume_data.get('email', ''), str(resume_score),
                    timestamp, str(resume_data.get('no_of_pages', 0)), reco_field, candidate_level,
                    str(resume_skills), str(recommended_skills), str(rec_course), pdf_name
                )

                st.markdown(section_card("Recommended videos", "A few extra learning resources to improve your resume storytelling and interviews."), unsafe_allow_html=True)
                vid_col1, vid_col2 = st.columns(2)
                with vid_col1:
                    st.markdown("**Resume Writing Tips**")
                    st.video(random.choice(resume_videos))
                with vid_col2:
                    st.markdown("**Interview Tips**")
                    st.video(random.choice(interview_videos))

                st.success("Analysis complete. Your resume has been reviewed, scored, and mapped to likely role directions.")
            else:
                st.error('Something went wrong while parsing the resume.')

    elif choice == 'Feedback':
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date + '_' + cur_time)

        st.markdown(section_card("Feedback", "Share what worked, what felt unclear, and what you want next."), unsafe_allow_html=True)
        with st.form("my_form"):
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            submitted = st.form_submit_button("Submit")
            if submitted:
                insertf_data(feed_name, feed_email, feed_score, comments, timestamp)
                st.success("Thanks. Your feedback was recorded.")

        plotfeed_data = pd.read_sql('select * from user_feedback', connection)
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()
        st.subheader("Past User Ratings")
        fig = px.pie(values=values, names=labels, title="User rating score from 1 to 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig, use_container_width=True)

        cursor.execute('select feed_name, comments from user_feedback')
        comments_data = cursor.fetchall()
        comments_df = pd.DataFrame(comments_data, columns=['User', 'Comment'])
        st.subheader("User Comments")
        st.dataframe(comments_df, width=1000)

    elif choice == 'About':
        st.markdown(section_card("About The Tool", "A modern resume review workflow with role matching and focused career guidance."), unsafe_allow_html=True)
        st.markdown("""
        <p align='justify'>
            This application parses resume information, identifies skills, predicts likely role direction, scores structure quality,
            and supports job-description-aware matching for clearer role alignment.
        </p>
        <p align='justify'>
            <b>User:</b> Upload a resume, optionally paste a target job description, and review role fit, gaps, and recommendations.<br/><br/>
            <b>Feedback:</b> Share suggestions and usability notes.<br/><br/>
            <b>Admin:</b> Review historical user data and platform usage trends.
        </p>
        """, unsafe_allow_html=True)

    else:
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False

        st.markdown(section_card("Admin Console v2", "A polished analytics workspace for role flow, score quality, and feedback intelligence."), unsafe_allow_html=True)

        if not st.session_state.admin_authenticated:
            login_col1, login_col2 = st.columns([1.1, 0.9])
            with login_col1:
                st.markdown(section_card("Secure access", "Enter admin credentials to open the analytics workspace."), unsafe_allow_html=True)
                ad_user = st.text_input("Username", key="admin_username")
                ad_password = st.text_input("Password", type='password', key="admin_password")
                if not ADMIN_CREDENTIALS:
                    st.warning("Admin credentials are not configured. Add them in `App/.env` before using the console.")
                if st.button('Open Admin Console', use_container_width=True):
                    if ADMIN_CREDENTIALS.get(ad_user) == ad_password:
                        st.session_state.admin_authenticated = True
                        st.session_state.admin_username = ad_user
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
        else:
            admin_action_col1, admin_action_col2 = st.columns([1, 5])
            with admin_action_col1:
                if st.button("Logout", use_container_width=True):
                    st.session_state.admin_authenticated = False
                    st.session_state.admin_username = None
                    st.rerun()
            with admin_action_col2:
                active_admin = st.session_state.get("admin_username", "Admin")
                st.success(f"Welcome {active_admin}. The analytics workspace is ready.")

            cursor.execute('''SELECT ID, ip_add, resume_score, Predicted_Field::TEXT, User_level::TEXT, city, state, country from user_data''')
            datanalys = cursor.fetchall()
            plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])

            cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, Predicted_Field::TEXT, Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, User_level::TEXT, Actual_skills::TEXT, Recommended_skills::TEXT, Recommended_courses::TEXT, city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
            user_rows = cursor.fetchall()
            users_df = pd.DataFrame(
                user_rows,
                columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                         'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page', 'File Name',
                         'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                         'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User']
            )

            cursor.execute('''SELECT * from user_feedback''')
            feedback_rows = cursor.fetchall()
            feedback_df = pd.DataFrame(feedback_rows, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])

            build_admin_console(plot_data, users_df, feedback_df, st.session_state.theme_mode)

# Calling the main (run()) function to make the whole process run
run()
