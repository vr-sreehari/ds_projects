import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine
from urllib.parse import quote_plus


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

    host = st.secrets["mysql"]["host"]
    port = st.secrets["mysql"]["port"]
    database = st.secrets["mysql"]["database"]
    user = st.secrets["mysql"]["user"]

    password = quote_plus(
        st.secrets["mysql"]["password"]
    )

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    return engine


engine = get_engine()

@st.cache_data(ttl=600)
def load_data():

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

    return df


df = load_data()

st.title("🌍 Global Seismic Trends")

st.markdown(
    """
    ### Data-Driven Earthquake Insights

    Explore global earthquake activity using data
    collected from the USGS Earthquake API.
    """
)


st.sidebar.header("🔎 Filters")

years = sorted(
    df["year"]
    .dropna()
    .astype(int)
    .unique()
)

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years
)

countries = sorted(
    df["country"]
    .dropna()
    .unique()
)

selected_countries = st.sidebar.multiselect(
    "Country / Region",
    options=countries
)

min_mag = float(df["mag"].min())
max_mag = float(df["mag"].max())

magnitude_range = st.sidebar.slider(
    "Magnitude Range",
    min_value=min_mag,
    max_value=max_mag,
    value=(min_mag, max_mag),
    step=0.1
)

min_depth = float(df["depth_km"].min())
max_depth = float(df["depth_km"].max())

depth_range = st.sidebar.slider(
    "Depth Range (km)",
    min_value=min_depth,
    max_value=max_depth,
    value=(min_depth, max_depth)
)

filtered_df = df.copy()

if selected_years:

    filtered_df = filtered_df[
        filtered_df["year"].isin(
            selected_years
        )
    ]


if selected_countries:

    filtered_df = filtered_df[
        filtered_df["country"].isin(
            selected_countries
        )
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

st.subheader("📊 Overview")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Earthquakes",
    f"{len(filtered_df):,}"
)


col2.metric(
    "Average Magnitude",
    f"{filtered_df['mag'].mean():.2f}"
)


col3.metric(
    "Strongest Earthquake",
    f"{filtered_df['mag'].max():.2f}"
)


tsunami_count = (
    filtered_df["tsunami"] == 1
).sum()

col4.metric(
    "Tsunami Events",
    f"{tsunami_count:,}"
)

st.subheader("📈 Earthquake Activity Over Time")

yearly_data = (
    filtered_df
    .groupby("year")
    .size()
    .reset_index(
        name="earthquake_count"
    )
)

fig = px.line(
    yearly_data,
    x="year",
    y="earthquake_count",
    markers=True,
    title="Earthquakes per Year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("📊 Magnitude Distribution")

fig = px.histogram(
    filtered_df,
    x="mag",
    nbins=40,
    title="Earthquake Magnitude Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

depth_counts = (
    filtered_df[
        "depth_category"
    ]
    .value_counts()
    .reset_index()
)

depth_counts.columns = [
    "depth_category",
    "count"
]

fig = px.bar(
    depth_counts,
    x="depth_category",
    y="count",
    title="Earthquakes by Depth Category"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader(
    "🌋 Magnitude vs Depth"
)

if len(filtered_df) > 10000:

    scatter_df = filtered_df.sample(
        10000,
        random_state=42
    )

else:

    scatter_df = filtered_df

    fig = px.scatter(
    scatter_df,
    x="depth_km",
    y="mag",
    hover_name="place",
    hover_data=[
        "country",
        "time",
        "depth_category"
    ],
    title="Magnitude vs Earthquake Depth"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

if len(filtered_df) > 15000:

    map_df = filtered_df.sample(
        15000,
        random_state=42
    )

else:

    map_df = filtered_df

    st.subheader(
    "🗺️ Global Earthquake Distribution"
)

fig = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    size="mag",
    color="mag",
    hover_name="place",
    hover_data=[
        "time",
        "depth_km",
        "country"
    ],
    projection="natural earth",
    title="Global Seismic Activity"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader(
    "⚠️ Top 10 Strongest Earthquakes"
)

top_10 = (
    filtered_df
    .nlargest(
        10,
        "mag"
    )
    [
        [
            "time",
            "place",
            "country",
            "mag",
            "depth_km",
            "tsunami",
            "sig"
        ]
    ]
)

st.dataframe(
    top_10,
    use_container_width=True,
    hide_index=True
)

st.subheader(
    "🌊 Tsunami Analysis"
)

tsunami_data = (
    filtered_df
    .groupby("year")["tsunami"]
    .sum()
    .reset_index()
)

fig = px.bar(
    tsunami_data,
    x="year",
    y="tsunami",
    title="Tsunami-Flagged Earthquakes per Year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.subheader(
    "🌎 Most Seismically Active Countries / Regions"
)

country_counts = (
    filtered_df[
        filtered_df["country"] != "Unknown"
    ]
    .groupby("country")
    .size()
    .reset_index(
        name="earthquake_count"
    )
    .sort_values(
        "earthquake_count",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    country_counts,
    x="earthquake_count",
    y="country",
    orientation="h",
    title="Top 10 Countries / Regions"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader(
    "📋 Earthquake Dataset"
)

st.write(
    f"Showing {len(filtered_df):,} records"
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_earthquakes.csv",
    mime="text/csv"
)

