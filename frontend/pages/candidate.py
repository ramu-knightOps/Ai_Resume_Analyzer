"""Candidate upload and analysis page."""

import streamlit as st

from ..api_client import BackendAPIError, ResumeAnalyzerClient
from ..components.report import recommended_courses_for, render_analysis_report
from ..components.styles import section_card
from ..services.pdf_parser import extract_text
from ..services.storage import build_session_record


def _validate_contact(name: str, email: str, mobile: str, pdf_file) -> bool:
    if not name.strip() or not email.strip() or not mobile.strip():
        st.warning("Please fill name, email, and mobile number before analysis.")
        return False
    if pdf_file is None:
        st.warning("Please upload a PDF resume first.")
        return False
    return True


def render_candidate_page(database, client: ResumeAnalyzerClient):
    st.markdown(
        section_card("Candidate workspace", "Upload a resume, add a job description, and get a more realistic fit review."),
        unsafe_allow_html=True,
    )

    with st.form("resume_analysis_form"):
        form_col1, form_col2, form_col3 = st.columns(3)
        with form_col1:
            name = st.text_input("Name*")
        with form_col2:
            email = st.text_input("Mail*")
        with form_col3:
            mobile = st.text_input("Mobile Number*")

        job_description = st.text_area(
            "Target Job Description",
            height=180,
            placeholder="Paste a job description here to unlock semantic role search, fit scoring, and skill-gap analysis.",
        )
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        submitted = st.form_submit_button("Analyze Resume", width="stretch")

    if submitted:
        if not _validate_contact(name, email, mobile, pdf_file):
            return

        pdf_content = pdf_file.getvalue()
        with st.spinner("Reading PDF and asking the backend for analysis..."):
            try:
                resume_text = extract_text(pdf_content)
                api_payload = {
                    "candidate_name": name,
                    "resume_text": resume_text,
                    "resume_skills": [],
                    "job_description": job_description,
                }
                analysis = client.analyze(**api_payload)
            except BackendAPIError as error:
                st.error(str(error))
                return
            except Exception as error:
                st.error(f"Resume parsing failed. Details: {error}")
                return

        recommended_courses = recommended_courses_for(analysis)
        contact = {"name": name, "email": email, "mobile": mobile}
        try:
            database.save_analysis(
                build_session_record(
                    contact=contact,
                    analysis=analysis,
                    recommended_courses=recommended_courses,
                    pdf_name=pdf_file.name,
                    pdf_content=pdf_content,
                )
            )
        except Exception as error:
            st.warning(f"Analysis finished, but the session record could not be stored. Details: {error}")

        st.session_state.latest_analysis = {
            "analysis": analysis,
            "pdf_name": pdf_file.name,
            "pdf_content": pdf_content,
            "api_payload": api_payload,
        }
        st.success("Analysis complete. Your resume has been reviewed, scored, and mapped to likely role directions.")

    result = st.session_state.get("latest_analysis")
    if result:
        render_analysis_report(
            analysis=result["analysis"],
            pdf_name=result["pdf_name"],
            pdf_content=result["pdf_content"],
            api_payload=result["api_payload"],
            client=client,
        )
