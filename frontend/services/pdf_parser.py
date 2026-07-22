"""PDF helpers used by the Streamlit frontend."""

import base64
import io

import streamlit as st
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer3.pdfpage import PDFPage


def extract_text(pdf_bytes: bytes) -> str:
    resource_manager = PDFResourceManager()
    text_handle = io.StringIO()
    converter = TextConverter(resource_manager, text_handle, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, converter)

    try:
        with io.BytesIO(pdf_bytes) as file_handle:
            for page in PDFPage.get_pages(file_handle, caching=True, check_extractable=True):
                interpreter.process_page(page)
        return text_handle.getvalue()
    finally:
        converter.close()
        text_handle.close()


def render_pdf_preview(pdf_bytes: bytes):
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f"""
        <iframe
            src="data:application/pdf;base64,{encoded_pdf}"
            width="400"
            height="500"
            type="application/pdf"
            style="border-radius: 10px; border: 2px solid #1ed760;">
        </iframe>
        """,
        unsafe_allow_html=True,
    )
