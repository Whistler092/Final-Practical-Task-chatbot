# Natural Disasters Chatbot — Streamlit Application

A conversational chatbot that queries historical natural disaster data (1900–2021) using a custom MCP server as its knowledge source. Built with Streamlit, LangGraph, and Azure OpenAI.

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Streamlit Web UI (port 8501)        │
│  ┌───────────────────────────────────────┐  │
│  │  Chat Interface + Streaming Tokens    │  │
│  │  Sidebar: Model & Server Info         │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ user question
                   ▼
         ┌─────────────────────────┐
         │   LangGraph Agent       │
         │  ┌───────────────────┐  │
         │  │ Azure OpenAI LLM  │  │
         │  │ (gpt-5-nano)      │  │
         │  └───────────────────┘  │
         │  ┌───────────────────┐  │
         │  │ query_disasters   │  │
         │  │ tool (from MCP)   │  │
         │  └───────────────────┘  │
         └────────────┬────────────┘
                      │ tool_use (MCP protocol)
                      ▼
         ┌─────────────────────────┐
         │  MCP Stack Provider     │
         │  (MultiServerMCPClient) │
         │  stdio transport        │
         └────────────┬────────────┘
                      │ spawns subprocess
                      ▼
         ┌─────────────────────────┐
         │  disasters-server       │
         │  (FastMCP)              │
         │  Loads CSV → filters →  │
         │  returns JSON           │
         └─────────────────────────┘
```

## How It Works (End-to-End Flow)

### 1. User sends a message

`streamlit_agent.py` captures the input via `st.chat_input()`, appends it to `st.session_state.messages`, and renders it in the chat.

### 2. Agent is created (cached)

`load_agent()` builds a LangGraph agent with:
- An **Azure OpenAI LLM** (configured via `.env`)
- **MCP tools** loaded from the `disasters-server` via `MCPStackProvider`
- A **system prompt** that instructs the LLM to always use `query_disasters` instead of guessing

### 3. MCP connection is established

`mcp_stack_provider.py` uses `langchain_mcp_adapters.MultiServerMCPClient` to spawn the MCP server as a subprocess:

```
uv --directory ../disasters-server run disasters-server
```

The MCP server communicates over **stdio** (stdin/stdout JSON-RPC). The adapter converts MCP tools into LangChain `BaseTool` objects that the agent can invoke.

### 4. LLM decides to call tools

The LangGraph agent sends the conversation to Azure OpenAI. Based on the system prompt and user query, the LLM generates one or more `tool_use` blocks specifying:
- Tool name: `query_disasters`
- Arguments: `country`, `year`, `disaster_type`, `limit`

### 5. MCP server processes the query

The `disasters-server` receives the tool call, loads its CSV datasets into pandas DataFrames, applies filters (case-insensitive partial match), and returns a JSON response:

```json
{
  "total": 42,
  "disasters": [
    {"Year": 2011, "Country": "Japan", "Disaster Type": "Earthquake", ...}
  ]
}
```

### 6. Results stream to the UI

`agent_streaming.py` listens to agent events via `agent.astream()` with two modes:

| Stream Mode | What it captures | Where it displays |
|-------------|-----------------|-------------------|
| `values` | Tool calls & tool results (state changes) | `st.status()` widget (collapsible box) |
| `messages` | LLM response tokens (AIMessageChunk only) | Chat bubble with live cursor `▍` |

- When an `AIMessage` with `tool_calls` appears → status shows "Calling tools: query_disasters"
- When a `ToolMessage` appears → status shows "Tool finished: `query_disasters` — 42 records returned"
- LLM response tokens stream in real time to the chat bubble

### 7. Final response

The LLM synthesizes the tool results into a human-readable answer (summarizing deaths, locations, dates, etc.) which is stored in `st.session_state.messages` for history.

## The MCP Server (`disasters-server/`)

### What it is

A standalone [Model Context Protocol](https://modelcontextprotocol.io/) server built with **FastMCP** that exposes disaster data as a queryable tool.

### Where it's implemented

```
disasters-server/
├── src/disasters_server/
│   ├── __init__.py          # Entry point (calls main())
│   └── server.py            # Tool definition + data loading
├── data/
│   ├── 1900_2021_DISASTERS.xlsx - emdat data.csv
│   └── 1970_2021_DISASTERS.xlsx - emdat data.csv
└── pyproject.toml           # Defines "disasters-server" script entry
```

### Tool: `query_disasters`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | str | No | Filter by country (case-insensitive, e.g. "Japan") |
| `year` | int | No | Filter by year (e.g. 2011) |
| `disaster_type` | str | No | Filter by type ("Earthquake", "Flood", "Storm", "Drought") |
| `limit` | int | No | Max results to return (default: 10) |

### Data Source

- ~10,000 historical disaster records from the [EM-DAT / EOSDIS](https://www.emdat.be/) dataset (via Kaggle)
- 47 fields per record: geographic info, temporal data, impact metrics (deaths, injuries, affected populations), damage estimates
- Both CSV files are concatenated at startup into a single DataFrame

### How it runs

The server is spawned as a **subprocess** by the Streamlit app. It communicates over stdio using the MCP JSON-RPC protocol. It stays alive for the duration of the tool call, then the connection is closed.

## File Reference

| File | Purpose |
|------|---------|
| `streamlit_agent.py` | Main Streamlit entrypoint. Renders UI, captures input, orchestrates agent. |
| `app_config.py` | Environment validation, logging setup, system prompt definition. |
| `mcp_stack_provider.py` | Bridge between LangChain and the MCP server (spawns subprocess, converts tools). |
| `agent_streaming.py` | Async streaming loop. Drives `agent.astream()`, updates status box and chat placeholder. |
| `agent_messages.py` | Parses LangChain messages into status lines. Counts MCP result records. |
| `conversation.py` | Formats chat history (last 6 turns) into the agent's input message. |
| `streamlit_ui.py` | Renders chat history and sidebar configuration panel. |

## Configuration

### Required Environment Variables (`.env`)

```env
OPENAI_API_KEY=<your Azure OpenAI API key>
MODEL=gpt-5-nano
AZURE_ENDPOINT=https://<your-resource>.openai.azure.com
API_VERSION=2024-08-01-preview
```

### Dependencies

```
streamlit
python-dotenv
langchain / langchain-core / langchain-community / langchain-openai
langchain-mcp-adapters
pandas
uv
```

## Running the Application

```bash
# From the streamlit/ directory
pip install -r requirements.txt
streamlit run streamlit_agent.py
```

The app will:
1. Load environment variables from `.env`
2. Initialize the LangGraph agent with Azure OpenAI
3. Spawn the MCP server subprocess (requires `uv` and the `disasters-server` package)
4. Open the web UI at `http://localhost:8501`

## Key Design Decisions

- **MCP over direct database access**: The MCP protocol decouples the data layer from the agent, making the tool reusable across different clients (CLI, notebooks, other UIs).
- **Stdio transport**: Simple subprocess communication — no HTTP server to manage. The MCP server is ephemeral.
- **Streaming with filtering**: Only `AIMessageChunk` tokens are streamed to the UI. Tool results (`ToolMessage`) are summarized as record counts in the status widget, not dumped as raw JSON.
- **History window of 6 turns**: Keeps the prompt size manageable while maintaining conversational context.
- **LangGraph agent**: Supports multi-step tool use (the LLM can call `query_disasters` multiple times with different filters in a single turn).
