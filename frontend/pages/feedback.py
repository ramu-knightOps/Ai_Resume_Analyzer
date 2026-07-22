"""Feedback page."""

import plotly.express as px
import streamlit as st

from ..components.styles import section_card


def render_feedback_page(database):
    st.markdown(section_card("Feedback", "Share what worked, what felt unclear, and what you want next."), unsafe_allow_html=True)
    with st.form("feedback_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        score = st.slider("Rate Us From 1 - 5", 1, 5)
        comments = st.text_input("Comments")
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                database.save_feedback(name=name, email=email, score=score, comments=comments)
                st.success("Thanks. Your feedback was recorded.")
            except Exception as error:
                st.warning(f"Feedback was received, but storing it failed. Details: {error}")

    feedback_df = database.load_feedback()
    st.subheader("Past User Ratings")
    if feedback_df.empty:
        st.info("No feedback has been recorded yet.")
    else:
        labels = feedback_df.feed_score.unique()
        values = feedback_df.feed_score.value_counts()
        figure = px.pie(values=values, names=labels, title="User rating score from 1 to 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(figure, width="stretch")

    st.subheader("User Comments")
    st.dataframe(database.load_comments(), width=1000)
