# Global Seismic Trends: Data-Driven Earthquake Insights

## Overview

**Global Seismic Trends** is an end-to-end Data Science project that analyzes global earthquake activity using data retrieved from the **USGS Earthquake API**.

The project covers the complete workflow from API data collection and preprocessing to MySQL storage, exploratory data analysis, SQL querying, visualization, and an interactive Streamlit dashboard.

The goal is to identify meaningful patterns in earthquake frequency, magnitude, depth, location, reporting quality, and tsunami-related events.

---

## Objectives

- Retrieve earthquake data from the USGS Earthquake API.
- Clean and transform raw earthquake records using Pandas.
- Handle missing values appropriately.
- Extract country/region information from earthquake locations.
- Create useful derived features for analysis.
- Store the cleaned dataset in MySQL.
- Use SQL and Pandas for exploratory analysis.
- Visualize global seismic trends.
- Build an interactive Streamlit dashboard.
- Identify patterns related to magnitude, depth, location, time, and tsunami events.

---

## Data Source

Earthquake data is collected from the official **USGS Earthquake Catalog API**.

API endpoint:

```text
https://earthquake.usgs.gov/fdsnws/event/1/query
```

The project retrieves earthquake records over multiple years using pagination to avoid the API result limit.

---

## Project Workflow

```text
USGS Earthquake API
        |
        v
Python Requests
        |
        v
Pandas DataFrame
        |
        v
Data Cleaning & Feature Engineering
        |
        v
MySQL Database
        |
        v
SQL + Pandas Analysis
        |
        v
EDA & Visualizations
        |
        v
Streamlit Dashboard
```

---

## Dataset Features

The project uses the following earthquake attributes.

| Column | Description |
|---|---|
| `id` | Unique earthquake event identifier |
| `time` | Time when the earthquake occurred |
| `updated` | Most recent update timestamp |
| `latitude` | Latitude of the earthquake epicenter |
| `longitude` | Longitude of the earthquake epicenter |
| `depth_km` | Earthquake depth in kilometers |
| `mag` | Earthquake magnitude |
| `magType` | Magnitude measurement type |
| `place` | Human-readable earthquake location |
| `status` | Review status of the earthquake |
| `tsunami` | Tsunami indicator |
| `sig` | Earthquake significance score |
| `net` | Reporting seismic network |
| `nst` | Number of seismic stations reporting the event |
| `dmin` | Distance to the nearest station |
| `rms` | Root mean square of seismic residuals |
| `gap` | Azimuthal gap between reporting stations |
| `magError` | Magnitude uncertainty |
| `depthError` | Depth uncertainty |
| `magNst` | Number of stations used for magnitude calculation |
| `locationSource` | Agency reporting the earthquake location |
| `magSource` | Agency reporting the magnitude |
| `types` | Associated earthquake data products |
| `ids` | Other identifiers associated with the event |
| `sources` | Reporting sources |
| `type` | Type of seismic event |

---

## Derived Features

Additional columns are created during preprocessing.

| Column | Description |
|---|---|
| `country` | Country or region extracted from `place` |
| `year` | Year extracted from earthquake time |
| `month` | Month extracted from earthquake time |
| `day` | Day extracted from earthquake time |
| `day_of_week` | Day name derived from earthquake time |
| `depth_category` | Shallow, Intermediate, or Deep classification |
| `strong_flag` | Indicates earthquakes with magnitude >= 6 |
| `destructive_flag` | Indicates earthquakes with magnitude >= 7 |

---

## Data Preparation

### Datetime Conversion

The `time` and `updated` fields are converted into Pandas datetime values.

```python
df["time"] = pd.to_datetime(
    df["time"],
    unit="ms",
    errors="coerce",
    utc=True
)

df["updated"] = pd.to_datetime(
    df["updated"],
    unit="ms",
    errors="coerce",
    utc=True
)
```

### Text Cleaning

String columns are stripped of extra whitespace and normalized where required.

```python
string_columns = [
    "magType",
    "status",
    "type",
    "net",
    "sources",
    "types",
    "locationSource",
    "magSource"
]

for col in string_columns:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()
```

### Country Extraction

Country or region information is extracted from the `place` column using regular expressions.

```python
df["country"] = (
    df["place"]
    .astype("string")
    .str.extract(r",\s*([^,]+)$", expand=False)
    .str.strip()
)

df["country"] = df["country"].fillna("Unknown")
```

> Note: USGS `place` is a descriptive location string, so this field may contain regions or states instead of a true country name in some cases.

---

## Missing Value Handling

Missing values are handled based on the meaning and importance of each feature.

- Rows with missing `mag` are removed.
- Missing `magType` values are labeled as `unknown`.
- Small amounts of missing values in fields such as `rms` and `depthError` may be replaced using the median.
- Quality-related fields with large amounts of missing data such as `nst`, `dmin`, `gap`, `magError`, and `magNst` are retained as `NULL` rather than filled with misleading values.

Example:

```python
df = df.dropna(subset=["mag"])

df["magType"] = df["magType"].fillna("unknown")

df["rms"] = df["rms"].fillna(df["rms"].median())

df["depthError"] = df["depthError"].fillna(
    df["depthError"].median()
)
```

---

## Depth Classification

Earthquakes are classified based on depth.

```text
Shallow       < 70 km
Intermediate  70 - 300 km
Deep          > 300 km
```

```python
def classify_depth(depth):
    if pd.isna(depth):
        return "Unknown"
    elif depth < 70:
        return "Shallow"
    elif depth <= 300:
        return "Intermediate"
    return "Deep"

df["depth_category"] = df["depth_km"].apply(classify_depth)
```

---

## Magnitude-Based Flags

Strong earthquakes:

```python
df["strong_flag"] = (df["mag"] >= 6).astype(int)
```

Potentially destructive earthquakes:

```python
df["destructive_flag"] = (df["mag"] >= 7).astype(int)
```

These are analytical thresholds and do not necessarily indicate actual physical damage.

---

## MySQL Database

The cleaned earthquake dataset is stored in MySQL.

Database name:

```text
global_seismic_trends
```

Table name:

```text
earthquakes
```

The earthquake `id` is used as the primary key.

Example:

```sql
CREATE TABLE earthquakes (
    id VARCHAR(50) NOT NULL PRIMARY KEY,
    time DATETIME(3),
    updated DATETIME(3),
    latitude DOUBLE,
    longitude DOUBLE,
    depth_km DOUBLE,
    mag DOUBLE,
    magType VARCHAR(20),
    place VARCHAR(500),
    status VARCHAR(30),
    tsunami TINYINT,
    sig INT,
    net VARCHAR(30),
    nst DOUBLE,
    dmin DOUBLE,
    rms DOUBLE,
    gap DOUBLE,
    magError DOUBLE,
    depthError DOUBLE,
    magNst DOUBLE,
    locationSource VARCHAR(50),
    magSource VARCHAR(50),
    types TEXT,
    ids TEXT,
    sources TEXT,
    `type` VARCHAR(50),
    country VARCHAR(100),
    `year` SMALLINT,
    `month` TINYINT,
    `day` TINYINT,
    day_of_week VARCHAR(15),
    depth_category VARCHAR(20),
    strong_flag TINYINT,
    destructive_flag TINYINT
);
```

---

## Loading Data into MySQL

Install the required packages:

```bash
pip install sqlalchemy pymysql cryptography
```

Create a SQLAlchemy connection:

```python
from sqlalchemy import create_engine
from urllib.parse import quote_plus

MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "global_seismic_trends"

password = quote_plus(MYSQL_PASSWORD)

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{password}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
```

Insert the cleaned DataFrame:

```python
df.to_sql(
    name="earthquakes",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000
)
```

Do not use `if_exists="replace"` after defining the primary key because it recreates the table and removes manually created constraints and indexes.

---

## Loading MySQL Data into Pandas

```python
import pandas as pd

df = pd.read_sql(
    "SELECT * FROM earthquakes",
    engine
)
```

---

## Exploratory Data Analysis

The project can answer questions such as:

- How many earthquakes occur each year?
- Which months have the highest earthquake activity?
- What are the strongest recorded earthquakes?
- Which regions have the highest earthquake frequency?
- What percentage of earthquakes are shallow, intermediate, or deep?
- Is earthquake magnitude related to depth?
- Which earthquakes triggered tsunami indicators?
- Which countries or regions have the most strong earthquakes?
- How does earthquake significance vary with magnitude?
- Which reporting networks contribute the most records?
- How complete are earthquake quality measurements?
- Are stronger earthquakes more likely to receive tsunami flags?

---

## Sample SQL Queries

### Total Earthquakes

```sql
SELECT COUNT(*) AS total_earthquakes
FROM earthquakes;
```

### Strongest Earthquakes

```sql
SELECT
    id,
    time,
    place,
    mag,
    depth_km
FROM earthquakes
ORDER BY mag DESC
LIMIT 10;
```

### Earthquakes by Year

```sql
SELECT
    year,
    COUNT(*) AS earthquake_count
FROM earthquakes
GROUP BY year
ORDER BY year;
```

### Earthquakes by Depth Category

```sql
SELECT
    depth_category,
    COUNT(*) AS earthquake_count
FROM earthquakes
GROUP BY depth_category;
```

### Tsunami-Related Earthquakes

```sql
SELECT
    id,
    time,
    place,
    mag,
    depth_km
FROM earthquakes
WHERE tsunami = 1
ORDER BY mag DESC;
```

### Strong Earthquakes by Country

```sql
SELECT
    country,
    COUNT(*) AS strong_earthquakes
FROM earthquakes
WHERE strong_flag = 1
GROUP BY country
ORDER BY strong_earthquakes DESC;
```

---

## Visualizations

The EDA phase can include:

- Earthquake magnitude distribution
- Depth distribution
- Earthquake frequency by year
- Earthquake frequency by month
- Magnitude vs depth scatter plot
- Global earthquake map
- Top countries/regions by earthquake count
- Tsunami vs non-tsunami earthquake comparison
- Magnitude category analysis
- Depth category analysis
- Significance vs magnitude
- Earthquake activity over time

---

## Streamlit Dashboard

The final dashboard can include:

- Total earthquake count
- Average magnitude
- Maximum magnitude
- Deepest recorded earthquake
- Year filter
- Magnitude filter
- Depth filter
- Country/region filter
- Global earthquake map
- Earthquake frequency trends
- Magnitude distribution
- Depth analysis
- Tsunami analysis
- Top strongest earthquakes
- Interactive earthquake data table

Run the app using:

```bash
streamlit run app.py
```

---

## Suggested Project Structure

```text
DS_Global_Seismic_Trends/
|
|-- data/
|   |-- global_seismic_data.csv
|
|-- notebooks/
|   |-- seismic_analysis.ipynb
|
|-- app.py
|-- requirements.txt
|-- README.md
```

---

## Requirements

Example `requirements.txt`:

```text
pandas
numpy
requests
sqlalchemy
pymysql
cryptography
matplotlib
plotly
streamlit
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## Technologies Used

- Python
- Pandas
- NumPy
- Requests
- Regex
- MySQL
- SQLAlchemy
- PyMySQL
- Matplotlib
- Plotly
- Streamlit
- Jupyter Notebook / VS Code

---

## Key Skills Demonstrated

This project demonstrates:

- REST API integration
- API pagination
- Data collection
- Data cleaning
- Missing value handling
- Feature engineering
- Regular expressions
- Pandas data manipulation
- MySQL database design
- Primary key usage
- SQL querying
- Exploratory Data Analysis
- Data visualization
- Streamlit dashboard development

---

## Future Enhancements

Possible future improvements include:

- Use reverse geocoding to obtain accurate country names from latitude and longitude.
- Automate daily or weekly USGS API updates.
- Implement MySQL UPSERT logic for revised earthquake records.
- Add magnitude-category filters.
- Add interactive Plotly geographic maps.
- Compare earthquake activity across tectonic regions.
- Build predictive models for earthquake characteristics.
- Deploy the Streamlit dashboard online.
- Add automated data-quality checks.

---

## Conclusion

The **Global Seismic Trends** project demonstrates a complete real-world Data Science pipeline using publicly available earthquake data.

It combines API integration, data preprocessing, feature engineering, database management, exploratory analysis, SQL, visualization, and dashboard development to generate meaningful insights into global earthquake activity.
