import asyncio
import json

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Load the csv with pandas
import os
import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("natural-disasters")

# Load files
#    Final-Practical-Task-chatbot\disasters-server\data\1900_2021_DISASTERS.xlsx - emdat data.csv
#    Final-Practical-Task-chatbot\disasters-server\data\1970-2021_DISASTERS.xlsx - emdat data.csv

CSV_PATH_1900_2021_DISASTERS = os.environ.get("DISASTERS_CSV_PATH", "..\\disasters-server\\data\\1900_2021_DISASTERS.xlsx - emdat data.csv")
CSV_PATH_1970_2021_DISASTERS = os.environ.get("DISASTERS_CSV_PATH", "..\\disasters-server\\data\\1970_2021_DISASTERS.xlsx - emdat data.csv")

df_disasters_1900_2021 = pd.read_csv(CSV_PATH_1900_2021_DISASTERS)
df_disasters_1970_2021 = pd.read_csv(CSV_PATH_1970_2021_DISASTERS)
print(f"Disasters data loaded: {df_disasters_1970_2021.shape[0]} rows, {df_disasters_1970_2021.shape[1]} columns")

# unify both datasets into a single DataFrame
df_disasters = pd.concat([df_disasters_1900_2021, df_disasters_1970_2021], ignore_index=True)
print(f"Combined disasters data: {df_disasters.shape[0]} rows, {df_disasters.shape[1]} columns")

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("disasters-server")

@mcp.tool()
async def query_disasters(
        country: str | None = None,
        year: int | None = None,
        disaster_type: str | None = None,
        limit: int = 10,
) -> str:
    """
    Query the natural disasters CSV dataset.
 

    Args: 
        country: Filter by country name (case-insensitive). E.g. "Argentina", "Australia". If None, no country filter is applied.
        year: Filter by year (e.g. 1970). If None, no year filter is applied.
        disaster_type: Filter by disaster type (case-insensitive, e.g. "Flood", "Storm", "Earthquake"). If None, no disaster type filter is applied.
        limit: Maximum number of results to return

    Expected output: A JSON string containing a list of disasters matching the criteria, with key details for each disaster. If no disasters match, a message indicating no results found. If the dataset is not loaded, an error message is returned.
    {   "total": 3,
        "disasters": [
            {
            "Year": 2021,
            "Seq": 182,
            "Disaster Group": "Natural",
            "Disaster Subgroup": "Hydrological",
            "Disaster Type": "Flood",
            "Country": "Colombia",
            "ISO": "COL",
            "Region": "South America",
            "Continent": "Americas",
            "Location": "Florencia City (Caquetá Department); Quípama Town (Boyacá Department), Bogotá",
            "Origin": "Heavy rains",
            "Associated Dis": "Slide (land, mud, snow, rock)",
            "Dis Mag Scale": "Km2",
            "Start Year": 2021,
            "Start Month": 4.0,
            "Start Day": 1.0,
            "End Year": 2021,
            "End Month": 4.0,
            "End Day": 5.0,
            "Total Deaths": 3.0,
            "No Injured": 5.0,
            "No Affected": 360.0,
            "Total Affected": 365.0,
            "Adm Level": "2",
            "Admin2 Code": "13608;13691;13914",
            "Geo Locations": "Florencia, Quipama, Santafe De Bogota D.c. (Adm2). "
            }
        ]
    }
    """

    if df_disasters is None or df_disasters.empty:
        return "Disasters data not loaded"
    
    df = df_disasters.copy()

    if country:
        df = df[df["Country"].str.contains(country, case=False, na=False)]
    if year:
        if "Year" in df.columns:
            df = df[df["Year"] == year]
    if disaster_type:
        df = df[df["Disaster Type"].str.contains(disaster_type, case=False, na=False)]

    if df.empty:
        return "No disasters found matching the criteria."

    df = df.head(limit)

    columns = [
        "Dis No",
        "Year",
        "Seq",
        "Glide",
        "Disaster Group",
        "Disaster Subgroup",
        "Disaster Type",
        "Disaster Subtype",
        "Disaster Subsubtype",
        "Event Name",
        "Country",
        "ISO",
        "Region",
        "Continent",
        "Location",
        "Origin",
        "Associated Dis",
        "Associated Dis2",
        "OFDA Response",
        "Appeal",
        "Declaration",
        "Aid Contribution",
        "Dis Mag Value",
        "Dis Mag Scale",
        "Latitude",
        "Longitude",
        "Local Time",
        "River Basin",
        "Start Year",
        "Start Month",
        "Start Day",
        "End Year",
        "End Month",
        "End Day",
        "Total Deaths",
        "No Injured",
        "No Affected",
        "No Homeless",
        "Total Affected",
        "Reconstruction Costs ('000 US$)",
        "Insured Damages ('000 US$)",
        "Total Damages ('000 US$)",
        "CPI",
        "Adm Level",
        "Admin1 Code",
        "Admin2 Code",
        "Geo Locations",
    ]

    available = [c for c in columns if c in df.columns]
    records = [
        {k: v for k, v in row.items() if not pd.isna(v)}
        for row in df[available].to_dict(orient="records")
    ]
    return json.dumps({"total": len(records), "disasters": records}, default=str)


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name != "add-note":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    note_name = arguments.get("name")
    content = arguments.get("content")

    if not note_name or not content:
        raise ValueError("Missing name or content")

    # Update server state
    notes[note_name] = content

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"Added note '{note_name}' with content: {content}",
        )
    ]

async def main():
    await mcp.run_sse_async()