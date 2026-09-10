import asyncio
import json
import os

import streamlit as st
from mcp import Client

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9090/mcp")


def _extract_tool_text(content):
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks = []
        for item in content:
            if hasattr(item, "text"):
                chunks.append(item.text)
            else:
                chunks.append(str(item))
        return "\n".join(chunks)

    if hasattr(content, "text"):
        return content.text

    return str(content)


async def _fetch_dashboard_snapshot():
    snapshot = {
        "running_containers": 0,
        "unhealthy_containers": 0,
        "failing_jenkins_jobs": 0,
        "last_deployment_status": os.getenv("LAST_DEPLOYMENT_STATUS", "No deployment recorded"),
        "mcp_connectivity": "offline",
    }

    try:
        async with Client(MCP_SERVER_URL) as client:
            try:
                ping_result = await client.call_tool("ping", {})
                ping_text = _extract_tool_text(ping_result.content).lower()
                snapshot["mcp_connectivity"] = "connected" if "alive" in ping_text else "connected"
            except Exception:
                snapshot["mcp_connectivity"] = "offline"

            try:
                health_result = await client.call_tool("get_infrastructure_health", {})
                payload = _extract_tool_text(health_result.content)
                data = json.loads(payload)
                snapshot.update(data)
            except Exception:
                try:
                    containers_result = await client.call_tool("get_docker_containers", {})
                    containers = json.loads(_extract_tool_text(containers_result.content))
                    snapshot["running_containers"] = sum(
                        1 for container in containers if (container.get("status") or "").lower() == "running"
                    )
                    snapshot["unhealthy_containers"] = sum(
                        1 for container in containers if (container.get("status") or "").lower() not in {"running", "restarting"}
                    )
                except Exception:
                    pass
    except Exception:
        snapshot["mcp_connectivity"] = "offline"

    return snapshot


@st.cache_data(ttl=30)
def load_dashboard_snapshot():
    return asyncio.run(_fetch_dashboard_snapshot())


def render_health_dashboard(data):
    status = "Connected" if data.get("mcp_connectivity") == "connected" else "Offline"
    status_color = "#7ef9d3" if data.get("mcp_connectivity") == "connected" else "#ff7b7b"
    deployment = data.get("last_deployment_status", "No deployment recorded")
    unhealthy = data.get("unhealthy_containers", 0)
    failing_jobs = data.get("failing_jenkins_jobs", 0)

    connected = data.get("mcp_connectivity") == "connected"
    status_badge_color = "#7ef9d3" if connected else "#ff7b7b"
    status_badge_bg = "rgba(126,249,211,0.12)" if connected else "rgba(255,123,123,0.12)"
    status_badge_border = "rgba(126,249,211,0.28)" if connected else "rgba(255,123,123,0.28)"

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin: 0.5rem 0 1.5rem;">
            <span style="padding:0.35rem 0.7rem; border-radius:999px; background:rgba(217,255,74,0.12); color:#d9ff4a; border:1px solid rgba(217,255,74,0.3); font-size:0.72rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase;">System status</span>
            <span style="padding:0.35rem 0.7rem; border-radius:999px; background:{status_badge_bg}; color:{status_badge_color}; border:1px solid {status_badge_border}; font-size:0.72rem; font-weight:600;">MCP: {status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cards = [
        ("Running containers", data.get("running_containers", 0), "Healthy"),
        ("Unhealthy containers", unhealthy, "Needs review" if unhealthy else "Clear"),
        ("Failing Jenkins jobs", failing_jobs, "Action needed" if failing_jobs else "Stable"),
        ("Last deployment", deployment, "Latest release"),
    ]

    cols = st.columns(4)
    for col, (label, value, hint) in zip(cols, metric_cards):
        with col:
            with st.container(border=True):
                st.caption(label)
                st.markdown(f"<div style='font-size:2rem; font-weight:700; line-height:1.1; margin:0.15rem 0; color:#edf6ff;'>{value}</div>", unsafe_allow_html=True)
                st.caption(hint)

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;'><div style='font-size:1.1rem; font-weight:600; color:#edf6ff;'>Workflow health</div><span style='padding:0.35rem 0.65rem; border-radius:999px; background:rgba(217,255,74,0.12); color:#d9ff4a; border:1px solid rgba(217,255,74,0.3); font-size:0.72rem;'>Live</span></div>",
                unsafe_allow_html=True,
            )
            stages = [
                ("Build", "done", "Completed"),
                ("Test", "done", "Passed"),
                ("Deploy", "active", "In progress"),
                ("Verify", "queued", "Queued"),
            ]
            stage_cols = st.columns(4)
            for col, (label, state, text) in zip(stage_cols, stages):
                with col:
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size:0.85rem; color:#8a9ab0; margin-bottom:0.4rem;'>{label}</div>", unsafe_allow_html=True)
                        tone = {
                            "done": ("#7ef9d3", "rgba(126,249,211,0.12)", "✓"),
                            "active": ("#d9ff4a", "rgba(217,255,74,0.12)", "•"),
                            "queued": ("#8a9ab0", "rgba(138,154,176,0.08)", "○"),
                        }[state]
                        st.markdown(
                            f"<div style='display:inline-flex; align-items:center; justify-content:center; width:1.7rem; height:1.7rem; border-radius:50%; background:{tone[1]}; color:{tone[0]}; font-weight:700; margin-bottom:0.5rem;'>{tone[2]}</div>",
                            unsafe_allow_html=True,
                        )
                        st.caption(text)

    with right:
        with st.container(border=True):
            st.markdown(
                "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;'><div style='font-size:1.1rem; font-weight:600; color:#edf6ff;'>Environment status</div><span style='color:#67d3ff; font-size:0.75rem;'>Manage</span></div>",
                unsafe_allow_html=True,
            )
            envs = [
                ("Production", "Healthy", "us-east-1"),
                ("Staging", "Updating", "us-east-1"),
                ("Preview", "Idle", "local :3000"),
            ]
            for name, state, region in envs:
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; padding:0.6rem 0.25rem; border-bottom:1px solid rgba(132,151,180,0.18);'>"
                    f"<div><div style='font-weight:600; color:#edf6ff;'>{name}</div><div style='font-size:0.72rem; color:#8a9ab0; margin-top:0.15rem;'>{region}</div></div>"
                    f"<span style='padding:0.22rem 0.52rem; border-radius:999px; font-size:0.68rem; font-weight:600; color:{'#7ef9d3' if state == 'Healthy' else '#d9ff4a' if state == 'Updating' else '#8a9ab0'}; background:{'rgba(126,249,211,0.12)' if state == 'Healthy' else 'rgba(217,255,74,0.12)' if state == 'Updating' else 'rgba(138,154,176,0.08)'};'>{state}</span></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("\n")
