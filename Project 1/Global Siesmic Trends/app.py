from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import streamlit as st


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide"
)


# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

@st.cache_resource
def get_engine():
    credentials = None

    # 1. Try Streamlit native secrets
    try:
        if "mysql" in st.secrets:
            credentials = st.secrets["mysql"]
    except Exception:
        pass

    # 2. Fallback to secrets.toml in script's local .streamlit folder
    if not credentials:
        local_secrets = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
        if local_secrets.exists():
            import toml
            credentials = toml.load(local_secrets).get("mysql")

    # 3. Fallback to secrets.toml in current working directory .streamlit folder
    if not credentials:
        cwd_secrets = Path.cwd() / ".streamlit" / "secrets.toml"
        if cwd_secrets.exists():
            import toml
            credentials = toml.load(cwd_secrets).get("mysql")

    if not credentials:
        st.error(
            "❌ MySQL credentials not found. Please ensure `.streamlit/secrets.toml` exists "
            "with a `[mysql]` section containing host, port, database, user, and password."
        )
        st.stop()

    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"]
    user = credentials["user"]
    password = quote_plus(str(credentials["password"]))

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )

    return engine


# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------

@st.cache_data(ttl=600, show_spinner="Loading earthquake data from database...")
def load_data():
    engine = get_engine()

    query = """
    SELECT *
    FROM earthquakes
    """

    df = pd.read_sql(
        query,
        engine
    )

    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    df["updated"] = pd.to_datetime(
        df["updated"],
        errors="coerce"
    )

    # Fill year from time column if missing
    if df["year"].isnull().any():
        df["year"] = df["year"].fillna(df["time"].dt.year)

    return df


df = load_data()


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🌍 Global Seismic Trends")

st.markdown(
    """
    ### Data-Driven Earthquake Insights

    Explore global earthquake activity using data collected from the USGS Earthquake API.
    """
)


# ---------------------------------------------------
# FILTERS (SIDEBAR)
# ---------------------------------------------------

st.sidebar.header("🔎 Filters")

valid_years = df["year"].dropna()
if not valid_years.empty:
    years = sorted(valid_years.astype(int).unique())
else:
    years = []

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years
)

valid_countries = df["country"].dropna().unique()
countries = sorted(
    [str(c) for c in valid_countries if str(c).strip() and str(c) != "Unknown"]
)

selected_countries = st.sidebar.multiselect(
    "Country / Region",
    options=countries
)

min_mag = float(df["mag"].min()) if not df["mag"].dropna().empty else 0.0
max_mag = float(df["mag"].max()) if not df["mag"].dropna().empty else 10.0

magnitude_range = st.sidebar.slider(
    "Magnitude Range",
    min_value=round(min_mag, 1),
    max_value=round(max_mag, 1),
    value=(round(min_mag, 1), round(max_mag, 1)),
    step=0.1
)

min_depth = float(df["depth_km"].min()) if not df["depth_km"].dropna().empty else 0.0
max_depth = float(df["depth_km"].max()) if not df["depth_km"].dropna().empty else 700.0

depth_range = st.sidebar.slider(
    "Depth Range (km)",
    min_value=round(min_depth, 1),
    max_value=round(max_depth, 1),
    value=(round(min_depth, 1), round(max_depth, 1)),
    step=1.0
)

# Apply filters
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[
        filtered_df["year"].isin(selected_years)
    ]
else:
    st.sidebar.info("Select at least one year to display results.")

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["country"].isin(selected_countries)
    ]

filtered_df = filtered_df[
    filtered_df["mag"].between(
        magnitude_range[0],
        magnitude_range[1]
    )
]

filtered_df = filtered_df[
    filtered_df["depth_km"].between(
        depth_range[0],
        depth_range[1]
    )
]

# Guard against empty filtered results
if filtered_df.empty:
    st.warning("⚠️ No earthquake records match the selected filter criteria. Please adjust your filters.")
    st.stop()


# ---------------------------------------------------
# OVERVIEW METRICS
# ---------------------------------------------------

st.subheader("📊 Overview")

col1, col2, col3, col4 = st.columns(4)

total_count = len(filtered_df)
avg_mag = filtered_df["mag"].mean()
strongest_mag = filtered_df["mag"].max()
tsunami_count = (filtered_df["tsunami"] == 1).sum()

col1.metric(
    "Total Earthquakes",
    f"{total_count:,}"
)

col2.metric(
    "Average Magnitude",
    f"{avg_mag:.2f}" if pd.notnull(avg_mag) else "N/A"
)

col3.metric(
    "Strongest Earthquake",
    f"{strongest_mag:.2f}" if pd.notnull(strongest_mag) else "N/A"
)

col4.metric(
    "Tsunami Events",
    f"{tsunami_count:,}"
)


# ---------------------------------------------------
# ACTIVITY OVER TIME
# ---------------------------------------------------

st.subheader("📈 Earthquake Activity Over Time")

yearly_data = (
    filtered_df.dropna(subset=["year"])
    .groupby("year")
    .size()
    .reset_index(name="earthquake_count")
)
yearly_data["year"] = yearly_data["year"].astype(int)

fig_yearly = px.line(
    yearly_data,
    x="year",
    y="earthquake_count",
    markers=True,
    title="Earthquakes per Year",
    labels={"year": "Year", "earthquake_count": "Total Earthquakes"}
)
fig_yearly.update_xaxes(type="category")

st.plotly_chart(
    fig_yearly,
    width="stretch",
    key="chart_yearly_activity"
)


# ---------------------------------------------------
# MAGNITUDE DISTRIBUTION
# ---------------------------------------------------

st.subheader("📊 Magnitude Distribution")

fig_hist = px.histogram(
    filtered_df,
    x="mag",
    nbins=40,
    title="Earthquake Magnitude Distribution",
    labels={"mag": "Magnitude", "count": "Count"}
)

st.plotly_chart(
    fig_hist,
    width="stretch",
    key="chart_mag_distribution"
)


# ---------------------------------------------------
# DEPTH CATEGORY DISTRIBUTION
# ---------------------------------------------------

depth_counts = (
    filtered_df["depth_category"]
    .value_counts()
    .reset_index()
)

depth_counts.columns = [
    "depth_category",
    "count"
]

fig_depth = px.bar(
    depth_counts,
    x="depth_category",
    y="count",
    title="Earthquakes by Depth Category",
    labels={"depth_category": "Depth Category", "count": "Count"}
)

st.plotly_chart(
    fig_depth,
    width="stretch",
    key="chart_depth_counts"
)


# ---------------------------------------------------
# MAGNITUDE VS DEPTH
# ---------------------------------------------------

st.subheader("🌋 Magnitude vs Depth")

if len(filtered_df) > 10000:
    scatter_df = filtered_df.sample(
        10000,
        random_state=42
    )
    st.caption("Displaying a representative sample of 10,000 events for optimal chart performance.")
else:
    scatter_df = filtered_df

fig_scatter = px.scatter(
    scatter_df,
    x="depth_km",
    y="mag",
    hover_name="place",
    hover_data=[
        "country",
        "time",
        "depth_category"
    ],
    title="Magnitude vs Earthquake Depth",
    labels={"depth_km": "Depth (km)", "mag": "Magnitude"}
)

st.plotly_chart(
    fig_scatter,
    width="stretch",
    key="chart_mag_vs_depth"
)


# ---------------------------------------------------
# GLOBAL EARTHQUAKE DISTRIBUTION (MAP)
# ---------------------------------------------------

st.subheader("🗺️ Global Earthquake Distribution")

geo_df = filtered_df.dropna(subset=["latitude", "longitude"])

if len(geo_df) > 10000:
    map_df = geo_df.sample(
        10000,
        random_state=42
    ).copy()
    st.caption("Displaying a representative sample of 10,000 events on the map.")
else:
    map_df = geo_df.copy()

# Plotly scatter_geo size must be non-negative (>= 0); clip to ensure no negative values
map_df["marker_size"] = np.clip(map_df["mag"], 1.0, None)

fig_map = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    size="marker_size",
    color="mag",
    hover_name="place",
    hover_data={
        "marker_size": False,
        "mag": ":.2f",
        "time": True,
        "depth_km": ":.1f",
        "country": True
    },
    projection="natural earth",
    title="Global Seismic Activity",
    color_continuous_scale="Viridis"
)
fig_map.update_layout(height=600)

st.plotly_chart(
    fig_map,
    width="stretch",
    key="chart_global_map"
)


# ---------------------------------------------------
# TOP 10 STRONGEST EARTHQUAKES
# ---------------------------------------------------

st.subheader("⚠️ Top 10 Strongest Earthquakes")

top_cols = [
    col for col in [
        "time",
        "place",
        "country",
        "mag",
        "depth_km",
        "tsunami",
        "sig"
    ] if col in filtered_df.columns
]

top_10 = (
    filtered_df
    .nlargest(10, "mag")
    [top_cols]
)

st.dataframe(
    top_10,
    width="stretch",
    hide_index=True
)


# ---------------------------------------------------
# TSUNAMI ANALYSIS
# ---------------------------------------------------

st.subheader("🌊 Tsunami Analysis")

tsunami_data = (
    filtered_df.dropna(subset=["year"])
    .groupby("year")["tsunami"]
    .sum()
    .reset_index()
)
tsunami_data["year"] = tsunami_data["year"].astype(int)

fig_tsunami = px.bar(
    tsunami_data,
    x="year",
    y="tsunami",
    title="Tsunami-Flagged Earthquakes per Year",
    labels={"year": "Year", "tsunami": "Tsunami Events"}
)
fig_tsunami.update_xaxes(type="category")

st.plotly_chart(
    fig_tsunami,
    width="stretch",
    key="chart_tsunami_analysis"
)


# ---------------------------------------------------
# MOST SEISMICALLY ACTIVE COUNTRIES
# ---------------------------------------------------

st.subheader("🌎 Most Seismically Active Countries / Regions")

valid_country_df = filtered_df[
    filtered_df["country"].notnull()
    & (filtered_df["country"] != "Unknown")
    & (filtered_df["country"] != "")
]

if not valid_country_df.empty:
    country_counts = (
        valid_country_df
        .groupby("country")
        .size()
        .reset_index(name="earthquake_count")
        .sort_values("earthquake_count", ascending=True)
        .tail(10)
    )

    fig_country = px.bar(
        country_counts,
        x="earthquake_count",
        y="country",
        orientation="h",
        title="Top 10 Countries / Regions",
        labels={"earthquake_count": "Earthquakes", "country": "Country / Region"}
    )

    st.plotly_chart(
        fig_country,
        width="stretch",
        key="chart_active_countries"
    )
else:
    st.info("No country records available for the selected filters.")


# ---------------------------------------------------
# EARTHQUAKE DATASET TABLE & EXPORT
# ---------------------------------------------------

st.subheader("📋 Earthquake Dataset")

st.write(
    f"Showing {len(filtered_df):,} records"
)

# Display first 1,000 records for fast browser rendering
st.dataframe(
    filtered_df.head(1000),
    width="stretch",
    hide_index=True
)

if len(filtered_df) > 1000:
    st.caption("Interactive table preview displays the first 1,000 records. Download below for the full dataset.")


@st.cache_data
def convert_to_csv(data_df):
    return data_df.to_csv(index=False).encode("utf-8")


csv = convert_to_csv(filtered_df)

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_earthquakes.csv",
    mime="text/csv",
    key="btn_download_csv"
)
