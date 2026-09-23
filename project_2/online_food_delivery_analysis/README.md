# 🍔 Online Food Delivery Analysis: Data-Driven Business Insights

An end-to-end data analytics project that transforms a noisy online food delivery dataset into a cleaned analytical dataset, business insights, SQL analysis, and an interactive Streamlit dashboard.

The project focuses on customer behavior, revenue and profit, restaurant performance, delivery efficiency, cancellations, and operational demand.

---

## 📌 Project Overview

Online food delivery platforms generate large volumes of transactional and behavioral data across customers, restaurants, orders, payments, and deliveries.

The objective of this project is to use data analytics to:

- Understand customer ordering behavior
- Identify operational inefficiencies in delivery
- Evaluate restaurant performance
- Track revenue, profit, and cancellations
- Analyze customer preferences across city, cuisine, and time
- Build an interactive dashboard for business decision-making

The project emphasizes handling noisy real-world data through data cleaning, preprocessing, EDA, SQL, and dashboard development.

---

## 🎯 Business Objectives

The analysis is designed to answer questions such as:

1. Who are the highest-spending customers?
2. How does customer age group relate to order value?
3. How do weekday and weekend ordering patterns differ?
4. How does revenue change month by month?
5. What is the relationship between discounts and estimated profit?
6. Which cities and cuisines generate the most revenue?
7. Which cities have the highest average delivery time?
8. Does delivery distance influence delivery time?
9. Is delivery rating related to delivery time?
10. Which restaurants have the highest average ratings?
11. Which restaurants have the highest cancellation rates?
12. How do cuisines compare across revenue, ratings, delivery time, and cancellations?
13. How does peak-hour demand differ from non-peak demand?
14. Which payment methods are most commonly used?
15. What are the main recorded cancellation reasons?

---

## 📊 Dataset

The original dataset contains:

- **100,000 orders**
- **25 source features**
- **8,999 unique customers**
- **900 restaurant IDs**
- **500 restaurant names**

### Source Feature Groups

| Category | Columns |
|---|---|
| Customer | `Customer_ID`, `Customer_Age`, `Customer_Gender`, `City`, `Area` |
| Restaurant | `Restaurant_ID`, `Restaurant_Name`, `Cuisine_Type`, `Restaurant_Rating` |
| Order | `Order_ID`, `Order_Date`, `Order_Time`, `Order_Value`, `Discount_Applied`, `Final_Amount`, `Payment_Mode`, `Order_Status`, `Order_Day`, `Peak_Hour` |
| Delivery | `Delivery_Time_Min`, `Distance_km`, `Delivery_Partner_ID`, `Delivery_Rating` |
| Cancellation | `Cancellation_Reason` |
| Financial | `Profit_Margin` |

> The dataset intentionally contains missing values, invalid values, and logical inconsistencies to support realistic preprocessing and analytical work.

---

## 🛠️ Technology Stack

### Python

- Pandas
- NumPy
- Matplotlib
- Plotly

### Database

- MySQL
- SQLAlchemy
- PyMySQL

### Dashboard

- Streamlit
- Plotly Express

### Development

- Jupyter Notebook
- VS Code
- Git
- GitHub

---

## 🔄 Project Workflow

```text
Raw Dataset
    ↓
Data Understanding
    ↓
Missing Value Analysis
    ↓
Data Cleaning & Validation
    ↓
Outlier Detection
    ↓
Feature Engineering
    ↓
Univariate EDA
    ↓
Bivariate / Business EDA
    ↓
MySQL Storage
    ↓
SQL Business Analysis
    ↓
Streamlit Dashboard
    ↓
Business Insights & Documentation
```

---

# 🧹 Data Cleaning & Preprocessing

The dataset was cleaned column-by-column rather than applying one generic rule to all missing or invalid values.

## Missing Values

### Customer Age

Approximately half of the original `Customer_Age` values were missing.

Missing age values were filled using the median:

```python
df["Customer_Age"] = df["Customer_Age"].fillna(
    df["Customer_Age"].median()
)
```

The median age was approximately **39**.

A helper flag was also retained so that originally missing ages could be excluded from demographic analysis:

```python
df["Age_Was_Missing"] = raw_df["Customer_Age"].isna()
```

This prevents imputed ages from artificially increasing the `Middle Age` category.

---

### Categorical Missing Values

Missing values that could not be inferred reliably were represented as `Unknown`.

Examples:

```text
Customer_Gender
City
Area
Cuisine_Type
Payment_Mode
Peak_Hour
```

This avoids artificially assigning missing observations to the most common category.

---

### Order Date

`Order_Date` was converted to datetime:

```python
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)
```

Invalid or unavailable dates remain as `NaT`.

These rows are excluded only from date-specific analyses rather than assigning artificial dates.

---

### Numerical Missing Values

Median imputation was used where appropriate for numerical variables such as:

- `Delivery_Time_Min`
- `Distance_km`
- `Order_Value`
- `Discount_Applied`

Median was preferred because it is more resistant to skewed distributions than the mean.

---

## Invalid Values

### Restaurant Rating

Restaurant ratings above the valid maximum were capped at 5.

```python
df["Restaurant_Rating"] = (
    df["Restaurant_Rating"].clip(upper=5)
)
```

---

### Negative Profit Margin

Negative profit margins were treated as invalid according to the project requirements.

They were replaced using the median of valid non-negative profit margins.

```python
valid_profit_median = df.loc[
    df["Profit_Margin"] >= 0,
    "Profit_Margin"
].median()

df.loc[
    df["Profit_Margin"] < 0,
    "Profit_Margin"
] = valid_profit_median
```

---

### Discount Greater Than Order Value

Discounts were prevented from exceeding the original order value:

```python
df["Discount_Applied"] = np.minimum(
    df["Discount_Applied"],
    df["Order_Value"]
)
```

This prevents negative final order amounts.

---

### Final Amount

`Final_Amount` was recalculated using the business relationship:

```text
Final Amount = Order Value - Discount Applied
```

```python
df["Final_Amount"] = (
    df["Order_Value"]
    - df["Discount_Applied"]
)
```

---

## Logical Consistency

### Cancelled Orders and Delivery Ratings

Cancelled orders should not contribute a delivery rating.

```python
df.loc[
    df["Order_Status"] == "Cancelled",
    "Delivery_Rating"
] = np.nan
```

Missing ratings for delivered orders were filled using the median rating of delivered orders.

---

### Cancellation Reason

Delivered orders do not require a cancellation reason:

```text
Delivered → Not Applicable
```

Cancelled orders with no recorded reason are stored as:

```text
Cancelled + missing reason → Unknown
```

This preserves the distinction between a valid non-applicable field and missing business information.

---

# 📦 Outlier Analysis

The IQR method was used to evaluate outliers in:

- `Order_Value`
- `Delivery_Time_Min`

Formula:

```text
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

No observations exceeded the IQR boundaries for these two variables, so no outlier removal or capping was required.

This prevents valid high-value or long-duration observations from being removed simply because they appear large.

---

# ⚙️ Feature Engineering

Additional analytical fields were created to support business analysis and dashboarding.

## Age Group

```text
18–25  → Young Adult
26–35  → Adult
36–45  → Middle Age
46–60  → Senior Adult
Unknown → Original age was missing
```

---

## Delivery Performance

Because the dataset does not specify an official delivery SLA, delivery performance was categorized using the observed delivery-time distribution.

```text
≤ 45 min       → Fast
46–120 min     → Moderate
121–210 min    → Slow
> 210 min      → Very Slow
```

These are analytical categories and should not be interpreted as formal SLA thresholds.

---

## Profit Margin Percentage

```python
df["Profit_Margin_Percentage"] = (
    df["Profit_Margin"] * 100
)
```

---

## Cancellation Flag

```python
df["Is_Cancelled"] = np.where(
    df["Order_Status"] == "Cancelled",
    1,
    0
)
```

---

## Revenue

Cancelled orders are excluded from recognized revenue.

```python
df["Revenue"] = np.where(
    df["Order_Status"] == "Delivered",
    df["Final_Amount"],
    0
)
```

---

## Estimated Profit

```python
df["Estimated_Profit"] = (
    df["Revenue"]
    * df["Profit_Margin"]
)
```

---

## Month Features

```python
df["Order_Month"] = (
    df["Order_Date"].dt.month_name()
)

df["Order_Month_Number"] = (
    df["Order_Date"].dt.month
)
```

---

# 🔍 Exploratory Data Analysis

EDA was performed using both univariate and bivariate techniques.

## Univariate Analysis

Analyzed distributions of:

- Order value
- Delivery time
- Customer age
- Age group
- City
- Cuisine
- Payment mode
- Order status
- Peak hour
- Customer gender

Techniques included:

- `describe()`
- `value_counts()`
- percentages
- histograms
- bar charts
- boxplots
- skewness

---

## Bivariate & Business Analysis

Relationships analyzed include:

```text
Age Group           ↔ Order Value
Order Day           ↔ Order Demand
City                ↔ Revenue
Cuisine             ↔ Revenue
Distance            ↔ Delivery Time
Delivery Rating     ↔ Delivery Time
Discount            ↔ Estimated Profit
Restaurant          ↔ Cancellation Rate
Peak Hour           ↔ Demand
```

---

# 📈 Key Analytical Results

The following values were observed using the preprocessing rules described above.

## Overall KPIs

| KPI | Result |
|---|---:|
| Total Orders | 100,000 |
| Delivered Orders | 84,964 |
| Cancelled Orders | 15,036 |
| Cancellation Rate | 15.04% |
| Total Recognized Revenue | ₹144.60M |
| Average Revenue per Delivered Order | ₹1,701.90 |
| Average Delivered Order Time | 124.98 min |
| Average Delivery Rating | 2.99 / 5 |
| Weighted Estimated Profit Margin | 24.85% |

> Results may vary slightly if preprocessing rules are modified.

---

## Revenue by City

Among orders with a known city:

| City | Revenue |
|---|---:|
| Bangalore | ₹24.38M |
| Hyderabad | ₹24.20M |
| Delhi | ₹24.03M |
| Chennai | ₹23.89M |
| Mumbai | ₹23.87M |

Revenue is relatively evenly distributed across the five known cities.

---

## Revenue by Cuisine

Among known cuisine values:

| Cuisine | Revenue |
|---|---:|
| Chinese | ₹24.19M |
| Mexican | ₹24.17M |
| Indian | ₹24.07M |
| Arabian | ₹23.86M |
| Italian | ₹23.70M |

Cuisine revenue is also relatively balanced.

---

## Monthly Revenue

The highest observed monthly revenue occurred in:

```text
July ≈ ₹12.48M
```

The lowest observed monthly revenue occurred in:

```text
February ≈ ₹11.44M
```

The overall monthly pattern is relatively stable rather than showing extreme seasonality.

---

## Weekday vs Weekend

Total order counts:

```text
Weekday → 71,370
Weekend → 28,630
```

However, there are five weekdays and only two weekend days in a normal week.

Average orders per calendar day were approximately:

```text
Weekday → 270.57
Weekend → 272.77
```

This indicates that comparing raw totals alone could be misleading.

---

## Distance vs Delivery Time

Pearson correlation:

```text
≈ 0.002
```

This indicates almost no linear relationship between delivery distance and delivery time in this dataset.

Distance alone therefore does not explain delivery-time variation well.

---

## Delivery Rating vs Delivery Time

Pearson correlation:

```text
≈ 0.002
```

There is almost no linear relationship between delivery time and delivery rating in the analyzed data.

---

## Discount vs Estimated Profit

Pearson correlation:

```text
≈ -0.043
```

This represents only a weak negative linear relationship.

Although higher discount groups can show lower average profit, discount amount alone does not strongly explain profit variation.

---

## Customer Age Group

Average order values for customers with known original ages were close across groups.

This suggests that customer age may not be a major differentiator of order value in this dataset.

---

## Cancellation Reasons

Among recorded cancellation reasons, counts were approximately:

| Cancellation Reason | Count |
|---|---:|
| Late Delivery | 3,059 |
| Customer Cancelled | 2,993 |
| Restaurant Issue | 2,979 |

A substantial number of cancelled orders also have an `Unknown` cancellation reason, which represents a data-quality gap rather than a business reason.

---

## Payment Mode

Known payment modes are almost evenly distributed:

```text
Card     20,094
Wallet   20,086
COD      19,977
UPI      19,932
```

No payment method strongly dominates the known payment records.

---

# 🗄️ MySQL Integration

The cleaned analytical dataset is stored in MySQL.

Database:

```sql
online_food_delivery
```

Table:

```sql
food_delivery_orders
```

Python uses SQLAlchemy and PyMySQL to connect and insert the cleaned data.

Example connection:

```python
from sqlalchemy import create_engine
from urllib.parse import quote_plus

password = quote_plus(MYSQL_PASSWORD)

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{password}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/online_food_delivery"
)
```

The DataFrame is inserted using:

```python
df.to_sql(
    name="food_delivery_orders",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000
)
```

---

# 🧾 SQL Analysis

The project includes a complete SQL analysis file:

```text
sql/online_food_delivery_analysis.sql
```

It contains queries for:

- KPI summary
- Top-spending customers
- Age group vs order value
- Weekday vs weekend demand
- Monthly revenue
- Discount vs profit
- Revenue by city
- Revenue by cuisine
- Delivery time by city
- Distance vs delivery time
- Delivery rating vs delivery time
- Top-rated restaurants
- Restaurant cancellation rate
- Cuisine performance
- Peak-hour demand
- Payment preferences
- Cancellation reasons
- Correlation calculations
- Additional city and delivery summaries

---

# 📊 Streamlit Dashboard

The interactive dashboard is implemented in:

```text
app.py
```

## Dashboard Features

### Filters

- City
- Cuisine
- Date range
- Order status
- Peak hour

### KPI Cards

- Total Orders
- Total Revenue
- Average Order Value
- Average Delivery Time
- Cancellation Rate
- Average Delivery Rating
- Profit Margin %

### Executive Overview

- Monthly revenue trend
- Revenue by city
- Revenue by cuisine
- Cancellation reasons
- Payment mode preference
- Dynamic business insights

### Customer Analysis

- Top-spending customers
- Age group vs order value
- Weekday vs weekend demand
- Peak vs non-peak demand

### Restaurant & Delivery

- Top-rated restaurants
- Restaurants with high cancellation rates
- Distance vs delivery time
- Delivery rating vs delivery time
- Cuisine performance

### Additional Dashboard Features

- Dynamic insight messages
- Data quality summary
- Dataset overview
- Filtered-data preview
- Download filtered data as CSV

---

# 📁 Recommended Project Structure

```text
online_food_delivery_analysis/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/
│   │   └── ONINE_FOOD_DELIVERY_ANALYSIS.csv
│   │
│   └── processed/
│       ├── online_food_delivery_preprocessed.csv
│       ├── online_food_delivery_cleaned.csv
│       └── food_delivery_eda_ready.csv
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_univariate_eda.ipynb
│   ├── 05_bivariate_business_eda.ipynb
│   └── 06_mysql_integration.ipynb
│
├── sql/
│   └── online_food_delivery_analysis.sql
│
└── .streamlit/
    └── secrets.toml
```

> Do not commit real database passwords or credentials to GitHub.

---

# ▶️ Running the Project Locally

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd online_food_delivery_analysis
```

---

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
streamlit
pandas
numpy
plotly
sqlalchemy
pymysql
matplotlib
```

---

## 4. CSV Mode

The Streamlit app can run directly from the cleaned CSV.

Place the final analytical file at:

```text
data/processed/food_delivery_eda_ready.csv
```

Then run:

```bash
streamlit run app.py
```

---

# 🔐 Optional MySQL Configuration

The Streamlit application can also load directly from MySQL.

Create:

```text
.streamlit/secrets.toml
```

Example:

```toml
[mysql]
host = "localhost"
port = 3306
database = "online_food_delivery"
user = "root"
password = "YOUR_PASSWORD"
```

Do not push this file to a public GitHub repository.

Add it to `.gitignore`:

```text
.streamlit/secrets.toml
```

---

# ☁️ Streamlit Cloud Deployment

For deployment:

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select the repository.
4. Set the entry file to:

```text
app.py
```

5. Add database secrets in Streamlit's secret-management interface if using a remote MySQL database.
6. Deploy the application.

For the simplest deployment, include the final cleaned dataset in the repository if its size is appropriate and run the app in CSV mode.

---

# ⚠️ Challenges Encountered

## Large Missing-Value Percentages

Several important features contained significant missing data.

**Solution:**  
Use column-specific treatment instead of applying `dropna()` globally.

---

## Customer Age Imputation

Approximately half of the age values were unavailable.

Filling them with the median creates a large artificial concentration at age 39.

**Solution:**  
Maintain an `Age_Was_Missing` flag and exclude imputed ages from demographic interpretation.

---

## Invalid Restaurant Ratings

Some ratings exceeded the maximum rating of 5.

**Solution:**  
Cap ratings at the valid maximum.

---

## Negative Final Amounts

Some discounts exceeded the associated order value.

**Solution:**  
Cap discounts at order value and recalculate `Final_Amount`.

---

## Cancelled Orders with Delivery Ratings

This produced a logical inconsistency.

**Solution:**  
Set delivery ratings for cancelled orders to null.

---

## Missing Cancellation Reasons

Missing cancellation reasons mean different things depending on order status.

**Solution:**

```text
Delivered order → Not Applicable
Cancelled order → Unknown
```

---

## Order Time Quality

Most non-null `Order_Time` values are `0:00`, making the field unsuitable for reliable time-of-day analysis.

**Solution:**  
Use the provided `Peak_Hour` field and retain unknown peak-hour values explicitly.

---

## Restaurant Grouping

`Restaurant_ID` and `Restaurant_Name` are not one-to-one in the source data.

Grouping by both fields created many small groups and caused restaurant charts to become empty after applying minimum-order thresholds.

**Solution:**  
Perform the dashboard's restaurant-level analysis using `Restaurant_Name` and apply an adaptive sample-size threshold.

---

# 💡 Business Interpretation

The analysis highlights several important points:

- Revenue is relatively evenly distributed across cities and cuisines.
- Raw weekday totals are much higher than weekend totals, but average orders per calendar day are similar.
- Delivery distance has almost no linear relationship with delivery time in this dataset.
- Delivery time has almost no linear relationship with delivery rating.
- Payment methods are distributed relatively evenly.
- Cancellation causes should be analyzed using recorded reasons only; `Unknown` represents missing information.
- Missing-data quality should remain visible rather than being hidden through aggressive imputation.
- Operational variables beyond distance may be required to explain delivery delays more effectively.

---

# 📌 Limitations

This analysis has several limitations:

- A large share of demographic and operational features were originally missing.
- `Order_Time` contains almost no useful variation.
- `Peak_Hour` itself contains missing values and cannot reliably be reconstructed from `Order_Time`.
- Delivery-performance categories are data-driven and are not official SLA thresholds.
- `Estimated_Profit` is derived from the supplied profit-margin field rather than an independently verified accounting measure.
- Correlation describes linear association and does not establish causation.
- Some restaurant identifiers and restaurant names do not form a strict one-to-one relationship.

These limitations should be considered when interpreting the results.

---

# 🚀 Future Improvements

Possible future improvements include:

- Add richer delivery-partner performance analysis
- Include weather and traffic data
- Introduce actual restaurant location coordinates
- Add customer segmentation
- Build predictive models for cancellation risk
- Predict delivery time
- Add demand forecasting
- Add formal SLA targets when business rules are available
- Improve cancellation-reason data capture
- Add authentication and role-based dashboard access
- Connect Streamlit directly to a production database

---

# ✅ Project Deliverables

This repository is designed to contain:

- Python notebooks for cleaning and analysis
- Cleaned analytical datasets
- MySQL integration code
- Complete SQL analysis
- Interactive Streamlit dashboard
- Business insights
- Project documentation

---

# 📚 Evaluation Coverage

The implementation addresses the major evaluation areas:

| Area | Project Coverage |
|---|---|
| Data Cleaning & EDA | Missing values, invalid data, outliers, logical consistency, EDA |
| Analytics & Business Insights | Customer, revenue, delivery, restaurant, cancellation and KPI analysis |
| Visualization & Dashboard | Interactive Streamlit dashboard with filters and Plotly visualizations |
| Documentation & Communication | README, documented cleaning decisions, business interpretations |
| Organization & Reproducibility | Structured notebooks, SQL scripts, processed datasets and setup instructions |

---

## 🏁 Conclusion

This project demonstrates a complete analytics workflow from raw, noisy data to business-ready insights.

The main value of the project is not only producing charts, but also ensuring that:

- data-quality problems are identified explicitly,
- preprocessing decisions are explainable,
- analytical metrics use appropriate business logic,
- SQL and Python produce reproducible results,
- and the final Streamlit dashboard turns the analysis into an accessible decision-support tool.
