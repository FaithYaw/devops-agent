import streamlit as st

from dashboard import load_dashboard_snapshot, render_health_dashboard

st.title("Overview")
st.caption("Live infrastructure health for the DevOps MCP environment.")

with st.spinner("Checking infrastructure health..."):
    dashboard_snapshot = load_dashboard_snapshot()

render_health_dashboard(dashboard_snapshot)
