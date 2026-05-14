import json
import os
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("natural-disasters")

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

CSV_PATH_1900 = os.environ.get(
    "DISASTERS_CSV_1900",
    str(_DATA_DIR / "1900_2021_DISASTERS.xlsx - emdat data.csv"),
)
CSV_PATH_1970 = os.environ.get(
    "DISASTERS_CSV_1970",
    str(_DATA_DIR / "1970_2021_DISASTERS.xlsx - emdat data.csv"),
)

df_disasters_1900 = pd.read_csv(CSV_PATH_1900)
df_disasters_1970 = pd.read_csv(CSV_PATH_1970)
print(f"Loaded 1900-2021: {df_disasters_1900.shape[0]} rows, {df_disasters_1900.shape[1]} columns")
print(f"Loaded 1970-2021: {df_disasters_1970.shape[0]} rows, {df_disasters_1970.shape[1]} columns")

df_disasters = pd.concat([df_disasters_1900, df_disasters_1970], ignore_index=True)
print(f"Combined disasters data: {df_disasters.shape[0]} rows, {df_disasters.shape[1]} columns")


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
        disaster_type: Filter by disaster type (case-insensitive). Supported types: "Animal accident", "Drought", "Earthquake", "Epidemic", "Extreme temperature", "Flood", "Fog", "Glacial lake outburst", "Impact", "Insect infestation", "Landslide", "Mass movement (dry)", "Storm", "Volcanic activity", "Wildfire". If None, no disaster type filter is applied.
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


def main():
    mcp.run()
