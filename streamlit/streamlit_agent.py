"""
Streamlit entrypoint: natural disasters agent backed by a custom MCP server and Azure OpenAI.

Uses the disasters-server MCP for querying historical disaster data (see mcp_stack_provider.py).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import streamlit as st

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:

    def load_dotenv(*args: Any, **kwargs: Any) -> bool:
        return False


from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool

from agent_streaming import run_agent_sync
from app_config import API_VERSION, SYSTEM_PROMPT, configure_logging, validate_env
from conversation import format_history
from mcp_stack_provider import MCPStackProvider
from streamlit_ui import render_chat_history, render_sidebar

logger = logging.getLogger(__name__)
 
@st.cache_resource(show_spinner=False)
def load_agent() -> Any:
    """Build and cache the LangGraph agent (LLM + MCP tools + music tool)."""
    load_dotenv()

    ok, message = validate_env()
    if not ok:
        raise RuntimeError(message)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")

    logger.info("Loading AzureChatOpenAI: endpoint=%s model=%s", azure_endpoint, model)

    if not azure_endpoint or not openai_api_key:
        raise ValueError("Azure OpenAI endpoint and key must be set in environment variables.")

    llm = AzureChatOpenAI(
        api_key=openai_api_key,
        api_version=API_VERSION,
        azure_endpoint=azure_endpoint,
        azure_deployment=model,
        temperature=1,
    )

    mcp_tools = MCPStackProvider().get_tools()
    tools = list(mcp_tools)

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

def main() -> None:
    """Configure logging, render the chat UI, and run one agent turn per user message."""
    configure_logging()

    render_sidebar()

    st.title("Natural disaster tracker agent")
    st.caption("This agent retrieves information about natural disasters around the world up to 2021.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello. Ask me anything about natural disasters in any location. "
                    "For example, you can ask 'What's the latest earthquake in Japan?' "
                    "or 'Are there any hurricanes in Colombia before?'"
                ),
            }
        ]

    render_chat_history()

    user_input = st.chat_input("Type your question...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        stream_placeholder = st.empty()
        try:
            agent = load_agent()
            history_text = format_history(st.session_state.messages)
            with st.status("Running the agent (tools may take a few seconds)…", expanded=True) as status:
                status.write("Starting…")
                answer = run_agent_sync(
                    agent,
                    history_text,
                    user_input,
                    status_container=status,
                    stream_placeholder=stream_placeholder,
                )
        except Exception as exc:
            logger.exception("Agent run failed")
            st.error(f"Error: {exc}")
            return

    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
