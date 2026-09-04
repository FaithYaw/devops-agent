import asyncio
import os

import streamlit as st

from agent import run_agent


st.set_page_config(page_title="DevOps AI Agent", page_icon="🛠️")
st.title("DevOps AI Agent")
st.caption("Ask infrastructure questions using the MCP-connected DevOps agent.")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9090/mcp")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_conversation" not in st.session_state:
    st.session_state.agent_conversation = []

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


def reset_chat():

    st.session_state.messages = []
    st.session_state.agent_conversation = []
    st.session_state.pending_approval = None


def handle_agent_result(result):

    st.session_state.agent_conversation = result["conversation"]

    if result["status"] == "completed":
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"]
        })
        st.session_state.pending_approval = None
        return

    st.session_state.pending_approval = {
        "tool_name": result["tool_name"],
        "arguments": result["arguments"],
        "call_id": result["call_id"],
        "message": result["message"],
    }
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["message"]
    })


with st.sidebar:
    st.markdown("### MCP connection")
    st.code(MCP_SERVER_URL, language="text")
    st.caption("Make sure the DevOps MCP server is running before chatting.")

    if st.button("Clear chat"):
        reset_chat()
        st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


pending_approval = st.session_state.pending_approval
if pending_approval:
    with st.chat_message("assistant"):
        st.warning(pending_approval["message"])

    col1, col2 = st.columns(2)
    if col1.button("Approve", use_container_width=True):
        result = asyncio.run(run_agent(
            conversation=st.session_state.agent_conversation,
            approval_decision={
                "tool_name": pending_approval["tool_name"],
                "arguments": pending_approval["arguments"],
                "call_id": pending_approval["call_id"],
                "approved": True,
            }
        ))
        handle_agent_result(result)
        st.rerun()

    if col2.button("Deny", use_container_width=True):
        result = asyncio.run(run_agent(
            conversation=st.session_state.agent_conversation,
            approval_decision={
                "tool_name": pending_approval["tool_name"],
                "arguments": pending_approval["arguments"],
                "call_id": pending_approval["call_id"],
                "approved": False,
            }
        ))
        handle_agent_result(result)
        st.rerun()


prompt = st.chat_input(
    "Ask the DevOps agent...",
    disabled=st.session_state.pending_approval is not None
)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = asyncio.run(run_agent(
                user_message=prompt,
                conversation=st.session_state.agent_conversation
            ))
    handle_agent_result(result)
    st.rerun()
