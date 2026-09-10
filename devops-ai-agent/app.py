import streamlit as st


st.set_page_config(
    page_title="DevOps AI Agent",
    page_icon=":material/health_and_safety:",
    layout="wide",
)

pages = [
    st.Page("app_pages/overview.py", title="Overview", icon=":material/dashboard:"),
    st.Page("app_pages/chat.py", title="Assistant", icon=":material/chat:"),
]

page = st.navigation(pages, position="sidebar")
page.run()
