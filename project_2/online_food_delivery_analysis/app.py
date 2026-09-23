
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Online Food Delivery Analysis",
    page_icon="🍔",
    layout="wide",
)

st.title("🍔 Online Food Delivery Analysis")
st.caption("Data-Driven Business Insights")


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_csv():
    possible_paths = [
        Path("dataset/food_delivery_eda_ready.csv"),
    ]

    for path in possible_paths:
        if path.exists():
            return pd.read_csv(
                path,
                parse_dates=["Order_Date"],
            )

    raise FileNotFoundError(
        "Cleaned CSV not found. Put it in dataset/ "
        "or update the path in load_csv()."
    )


@st.cache_data
def load_mysql():
    mysql = st.secrets["mysql"]

    password = quote_plus(str(mysql["password"]))

    engine = create_engine(
        f"mysql+pymysql://{mysql['user']}:{password}"
        f"@{mysql['host']}:{mysql['port']}/{mysql['database']}"
    )

    df = pd.read_sql(
        "SELECT * FROM food_delivery_orders",
        engine,
    )

    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"],
        errors="coerce",
    )

    return df


def load_data():
    """
    Prefer MySQL when Streamlit secrets are configured.
    Otherwise fall back to the cleaned CSV.
    """
    try:
        if "mysql" in st.secrets:
            return load_mysql()
    except Exception:
        pass

    return load_csv()


try:
    df = load_data()
except Exception as exc:
    st.error(f"Unable to load data: {exc}")
    st.stop()


# ============================================================
# DATA TYPE / DERIVED COLUMN SAFETY
# ============================================================

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce",
)

if "Revenue" not in df.columns:
    df["Revenue"] = df["Final_Amount"].where(
        df["Order_Status"].eq("Delivered"),
        0,
    )

if "Is_Cancelled" not in df.columns:
    df["Is_Cancelled"] = (
        df["Order_Status"]
        .eq("Cancelled")
        .astype(int)
    )

if "Estimated_Profit" not in df.columns:
    df["Estimated_Profit"] = (
        df["Revenue"] * df["Profit_Margin"]
    )

if "Profit_Margin_Percentage" not in df.columns:
    df["Profit_Margin_Percentage"] = (
        df["Profit_Margin"] * 100
    )

if "Order_Month" not in df.columns:
    df["Order_Month"] = (
        df["Order_Date"]
        .dt.month_name()
    )

if "Order_Month_Number" not in df.columns:
    df["Order_Month_Number"] = (
        df["Order_Date"]
        .dt.month
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Filters")

city_options = sorted(
    [
        value
        for value in df["City"].dropna().unique().tolist()
        if value != "Unknown"
    ]
)

selected_cities = st.sidebar.multiselect(
    "City",
    city_options,
    default=city_options,
)

cuisine_options = sorted(
    [
        value
        for value in df["Cuisine_Type"].dropna().unique().tolist()
        if value != "Unknown"
    ]
)

selected_cuisines = st.sidebar.multiselect(
    "Cuisine",
    cuisine_options,
    default=cuisine_options,
)

status_options = sorted(
    df["Order_Status"]
    .dropna()
    .unique()
    .tolist()
)

selected_status = st.sidebar.multiselect(
    "Order Status",
    status_options,
    default=status_options,
)

peak_options = sorted(
    [
        value
        for value in df["Peak_Hour"].dropna().unique().tolist()
        if value != "Unknown"
    ]
)

selected_peak = st.sidebar.multiselect(
    "Peak Hour",
    peak_options,
    default=peak_options,
)

valid_dates = df["Order_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    selected_dates = None

st.sidebar.markdown(
    """
    ---
    ### About

    This dashboard analyzes online food delivery data across:

    - Customers
    - Restaurants
    - Revenue and profit
    - Delivery performance
    - Cancellations
    - Operational demand
    """
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_cities:
    filtered_df = filtered_df[
        filtered_df["City"].isin(selected_cities)
    ]

if selected_cuisines:
    filtered_df = filtered_df[
        filtered_df["Cuisine_Type"].isin(selected_cuisines)
    ]

if selected_status:
    filtered_df = filtered_df[
        filtered_df["Order_Status"].isin(selected_status)
    ]

if selected_peak:
    filtered_df = filtered_df[
        filtered_df["Peak_Hour"].isin(selected_peak)
    ]

if selected_dates and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["Order_Date"].isna()
        |
        (
            (filtered_df["Order_Date"].dt.date >= start_date)
            &
            (filtered_df["Order_Date"].dt.date <= end_date)
        )
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_orders = filtered_df["Order_ID"].nunique()

total_revenue = filtered_df["Revenue"].sum()

delivered_df = filtered_df[
    filtered_df["Order_Status"] == "Delivered"
]

average_order_value = (
    delivered_df["Revenue"].mean()
    if not delivered_df.empty
    else 0
)

average_delivery_time = (
    delivered_df["Delivery_Time_Min"].mean()
    if not delivered_df.empty
    else 0
)

cancelled_orders = (
    filtered_df["Order_Status"]
    .eq("Cancelled")
    .sum()
)

cancellation_rate = (
    cancelled_orders / total_orders * 100
    if total_orders
    else 0
)

average_delivery_rating = (
    delivered_df["Delivery_Rating"].mean()
    if not delivered_df.empty
    else 0
)

total_profit = filtered_df["Estimated_Profit"].sum()

profit_margin = (
    total_profit / total_revenue * 100
    if total_revenue
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Executive KPIs")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total Orders",
    f"{total_orders:,}",
)

k2.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}",
)

k3.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}",
)

k4.metric(
    "Average Delivery Time",
    f"{average_delivery_time:.2f} min",
)

k5, k6, k7 = st.columns(3)

k5.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%",
)

k6.metric(
    "Average Delivery Rating",
    f"{average_delivery_rating:.2f}/5",
)

k7.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%",
)


# ============================================================
# KEY BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Key Business Insights")

insight_col1, insight_col2 = st.columns(2)

# Highest revenue city
city_insight = (
    filtered_df[
        filtered_df["City"] != "Unknown"
    ]
    .groupby("City")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

if not city_insight.empty:
    top_city = city_insight.index[0]
    top_city_revenue = city_insight.iloc[0]

    insight_col1.info(
        f"🏙️ {top_city} generated the highest revenue "
        f"of ₹{top_city_revenue:,.0f}."
    )

# Highest revenue cuisine
cuisine_insight = (
    filtered_df[
        filtered_df["Cuisine_Type"] != "Unknown"
    ]
    .groupby("Cuisine_Type")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

if not cuisine_insight.empty:
    top_cuisine = cuisine_insight.index[0]
    top_cuisine_revenue = cuisine_insight.iloc[0]

    insight_col2.info(
        f"🍽️ {top_cuisine} generated the highest cuisine revenue "
        f"of ₹{top_cuisine_revenue:,.0f}."
    )

# Most common recorded cancellation reason
known_cancellations = filtered_df[
    (filtered_df["Order_Status"] == "Cancelled")
    &
    (
        filtered_df["Cancellation_Reason"]
        .notna()
    )
    &
    (
        filtered_df["Cancellation_Reason"]
        .ne("Unknown")
    )
]

reason_counts = (
    known_cancellations["Cancellation_Reason"]
    .value_counts()
)

if not reason_counts.empty:
    top_reason = reason_counts.index[0]
    top_reason_count = reason_counts.iloc[0]

    insight_col1.warning(
        f"❌ Most frequently recorded cancellation reason: "
        f"{top_reason} ({top_reason_count:,} orders)."
    )

# Slowest average city
city_delivery_insight = (
    filtered_df[
        filtered_df["City"] != "Unknown"
    ]
    .groupby("City")["Delivery_Time_Min"]
    .mean()
    .sort_values(ascending=False)
)

if not city_delivery_insight.empty:
    slowest_city = city_delivery_insight.index[0]
    slowest_time = city_delivery_insight.iloc[0]

    insight_col2.warning(
        f"🚚 {slowest_city} has the highest average delivery time "
        f"at {slowest_time:.1f} minutes."
    )

# Correlation insight cards
correlation_left, correlation_right = st.columns(2)

distance_corr_df = filtered_df[
    ["Distance_km", "Delivery_Time_Min"]
].dropna()

if len(distance_corr_df) > 1:
    distance_delivery_corr = (
        distance_corr_df["Distance_km"]
        .corr(distance_corr_df["Delivery_Time_Min"])
    )

    if pd.notna(distance_delivery_corr):
        if abs(distance_delivery_corr) < 0.3:
            distance_message = (
                "The linear relationship is weak."
            )
        elif distance_delivery_corr > 0:
            distance_message = (
                "Longer distances are associated with longer delivery times."
            )
        else:
            distance_message = (
                "Longer distances are associated with shorter delivery times."
            )

        correlation_left.info(
            f"📍 Distance vs delivery-time correlation: "
            f"{distance_delivery_corr:.2f}. {distance_message}"
        )

discount_corr_df = filtered_df[
    ["Discount_Applied", "Estimated_Profit"]
].dropna()

if len(discount_corr_df) > 1:
    discount_profit_corr = (
        discount_corr_df["Discount_Applied"]
        .corr(discount_corr_df["Estimated_Profit"])
    )

    if pd.notna(discount_profit_corr):
        if discount_profit_corr < -0.3:
            discount_message = (
                "Higher discounts are associated with lower estimated profit."
            )
        elif discount_profit_corr > 0.3:
            discount_message = (
                "Higher discounts are associated with higher estimated profit."
            )
        else:
            discount_message = (
                "Discount amount has only a weak linear relationship "
                "with estimated profit."
            )

        correlation_right.info(
            f"💰 Discount vs profit correlation: "
            f"{discount_profit_corr:.2f}. {discount_message}"
        )


# ============================================================
# MAIN ANALYSIS TABS
# ============================================================

overview_tab, customer_tab, restaurant_tab = st.tabs(
    [
        "📊 Executive Overview",
        "👥 Customer Analysis",
        "🍽️ Restaurant & Delivery",
    ]
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

with overview_tab:

    st.subheader("Monthly Revenue Trend")

    monthly_revenue = (
        filtered_df
        .dropna(subset=["Order_Date"])
        .groupby(
            ["Order_Month_Number", "Order_Month"],
            as_index=False,
        )
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("Order_ID", "nunique"),
        )
        .sort_values("Order_Month_Number")
    )

    fig = px.line(
        monthly_revenue,
        x="Order_Month",
        y="Total_Revenue",
        markers=True,
        title="Monthly Revenue",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        city_revenue = (
            filtered_df[
                filtered_df["City"] != "Unknown"
            ]
            .groupby(
                "City",
                as_index=False,
            )
            .agg(
                Total_Revenue=("Revenue", "sum")
            )
            .sort_values(
                "Total_Revenue",
                ascending=False,
            )
        )

        fig = px.bar(
            city_revenue,
            x="City",
            y="Total_Revenue",
            title="Revenue by City",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        cuisine_revenue = (
            filtered_df[
                filtered_df["Cuisine_Type"] != "Unknown"
            ]
            .groupby(
                "Cuisine_Type",
                as_index=False,
            )
            .agg(
                Total_Revenue=("Revenue", "sum")
            )
            .sort_values(
                "Total_Revenue",
                ascending=False,
            )
        )

        fig = px.bar(
            cuisine_revenue,
            x="Cuisine_Type",
            y="Total_Revenue",
            title="Revenue by Cuisine",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    left, right = st.columns(2)

    with left:
        cancellation_reasons = (
            filtered_df[
                filtered_df["Order_Status"] == "Cancelled"
            ]["Cancellation_Reason"]
            .value_counts()
            .reset_index()
        )

        cancellation_reasons.columns = [
            "Cancellation_Reason",
            "Count",
        ]

        fig = px.bar(
            cancellation_reasons,
            x="Cancellation_Reason",
            y="Count",
            title="Cancellation Reasons",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        payment_df = filtered_df[
            filtered_df["Payment_Mode"] != "Unknown"
        ]

        payment_counts = (
            payment_df["Payment_Mode"]
            .value_counts()
            .reset_index()
        )

        payment_counts.columns = [
            "Payment_Mode",
            "Count",
        ]

        fig = px.pie(
            payment_counts,
            names="Payment_Mode",
            values="Count",
            hole=0.4,
            title="Payment Mode Preference",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# CUSTOMER ANALYSIS
# ============================================================

with customer_tab:

    st.subheader("Top-Spending Customers")

    customer_spending = (
        filtered_df
        .groupby(
            "Customer_ID",
            as_index=False,
        )
        .agg(
            Total_Orders=("Order_ID", "count"),
            Total_Spending=("Revenue", "sum"),
        )
        .sort_values(
            "Total_Spending",
            ascending=False,
        )
        .head(10)
    )

    fig = px.bar(
        customer_spending,
        x="Total_Spending",
        y="Customer_ID",
        orientation="h",
        title="Top 10 Spending Customers",
    )

    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        age_df = filtered_df[
            filtered_df["Age_Group"].notna()
            &
            (
                filtered_df["Age_Group"]
                != "Unknown"
            )
        ]

        age_order = (
            age_df
            .groupby(
                "Age_Group",
                as_index=False,
            )
            .agg(
                Average_Order_Value=(
                    "Order_Value",
                    "mean",
                )
            )
        )

        fig = px.bar(
            age_order,
            x="Age_Group",
            y="Average_Order_Value",
            title="Age Group vs Average Order Value",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        day_orders = (
            filtered_df
            .groupby(
                "Order_Day",
                as_index=False,
            )
            .agg(
                Total_Orders=(
                    "Order_ID",
                    "count",
                )
            )
        )

        fig = px.bar(
            day_orders,
            x="Order_Day",
            y="Total_Orders",
            title="Weekday vs Weekend Orders",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.subheader("Peak vs Non-Peak Demand")

    peak_df = filtered_df[
        filtered_df["Peak_Hour"] != "Unknown"
    ]

    peak_analysis = (
        peak_df
        .groupby(
            "Peak_Hour",
            as_index=False,
        )
        .agg(
            Total_Orders=("Order_ID", "count"),
            Average_Delivery_Time=(
                "Delivery_Time_Min",
                "mean",
            ),
            Total_Revenue=("Revenue", "sum"),
        )
    )

    fig = px.bar(
        peak_analysis,
        x="Peak_Hour",
        y="Total_Orders",
        hover_data=[
            "Average_Delivery_Time",
            "Total_Revenue",
        ],
        title="Peak Hour Demand",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# RESTAURANT & DELIVERY
# ============================================================

with restaurant_tab:

    left, right = st.columns(2)

    with left:
        # Restaurant_ID and Restaurant_Name are not one-to-one in this dataset.
        # Group by Restaurant_Name for restaurant-level analysis.
        restaurant_rating = (
            filtered_df
            .groupby(
                "Restaurant_Name",
                as_index=False,
            )
            .agg(
                Average_Rating=(
                    "Restaurant_Rating",
                    "mean",
                ),
                Total_Orders=(
                    "Order_ID",
                    "count",
                ),
            )
        )

        # Scale the minimum sample-size requirement with the active filters.
        # Full dataset -> about 50 orders; narrower filters -> smaller threshold.
        min_restaurant_orders = max(
            3,
            min(
                50,
                round(len(filtered_df) * 0.0005),
            ),
        )

        eligible_ratings = restaurant_rating[
            restaurant_rating["Total_Orders"] >= min_restaurant_orders
        ].copy()

        # If filters are extremely narrow, fall back to available restaurants
        # instead of leaving the chart empty.
        if eligible_ratings.empty:
            eligible_ratings = restaurant_rating.copy()

        restaurant_rating_top10 = (
            eligible_ratings
            .sort_values(
                [
                    "Average_Rating",
                    "Total_Orders",
                ],
                ascending=[False, False],
            )
            .head(10)
        )

        if restaurant_rating_top10.empty:
            st.info(
                "No restaurant rating data is available for the selected filters."
            )
        else:
            fig = px.bar(
                restaurant_rating_top10,
                x="Average_Rating",
                y="Restaurant_Name",
                orientation="h",
                title=(
                    "Top 10 Rated Restaurants "
                    f"(minimum {min_restaurant_orders} orders where possible)"
                ),
                hover_data=["Total_Orders"],
            )

            fig.update_layout(
                yaxis={
                    "categoryorder": "total ascending"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    with right:
        restaurant_cancel = (
            filtered_df
            .groupby(
                "Restaurant_Name",
                as_index=False,
            )
            .agg(
                Total_Orders=(
                    "Order_ID",
                    "count",
                ),
                Cancelled_Orders=(
                    "Is_Cancelled",
                    "sum",
                ),
            )
        )

        restaurant_cancel[
            "Cancellation_Rate"
        ] = (
            restaurant_cancel["Cancelled_Orders"]
            / restaurant_cancel["Total_Orders"]
            * 100
        )

        eligible_cancellations = restaurant_cancel[
            restaurant_cancel["Total_Orders"] >= min_restaurant_orders
        ].copy()

        if eligible_cancellations.empty:
            eligible_cancellations = restaurant_cancel.copy()

        restaurant_cancel_top10 = (
            eligible_cancellations
            .sort_values(
                [
                    "Cancellation_Rate",
                    "Total_Orders",
                ],
                ascending=[False, False],
            )
            .head(10)
        )

        if restaurant_cancel_top10.empty:
            st.info(
                "No restaurant cancellation data is available for the selected filters."
            )
        else:
            fig = px.bar(
                restaurant_cancel_top10,
                x="Cancellation_Rate",
                y="Restaurant_Name",
                orientation="h",
                title=(
                    "Highest Restaurant Cancellation Rates "
                    f"(minimum {min_restaurant_orders} orders where possible)"
                ),
                hover_data=[
                    "Total_Orders",
                    "Cancelled_Orders",
                ],
            )

            fig.update_layout(
                yaxis={
                    "categoryorder": "total ascending"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    st.subheader("Distance vs Delivery Time")

    scatter_df = filtered_df[
        [
            "Distance_km",
            "Delivery_Time_Min",
            "City",
            "Order_Status",
        ]
    ].dropna()

    if len(scatter_df) > 15000:
        scatter_df = scatter_df.sample(
            15000,
            random_state=42,
        )

    fig = px.scatter(
        scatter_df,
        x="Distance_km",
        y="Delivery_Time_Min",
        color="Order_Status",
        hover_data=["City"],
        opacity=0.45,
        title="Distance vs Delivery Time",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Delivery Rating vs Delivery Time")

    rating_delivery = (
        filtered_df[
            (
                filtered_df["Order_Status"]
                == "Delivered"
            )
            &
            (
                filtered_df["Delivery_Rating"]
                .notna()
            )
        ]
        .groupby(
            "Delivery_Rating",
            as_index=False,
        )
        .agg(
            Average_Delivery_Time=(
                "Delivery_Time_Min",
                "mean",
            ),
            Total_Orders=(
                "Order_ID",
                "count",
            ),
        )
    )

    fig = px.bar(
        rating_delivery,
        x="Delivery_Rating",
        y="Average_Delivery_Time",
        hover_data=["Total_Orders"],
        title="Delivery Rating vs Average Delivery Time",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Cuisine Performance")

    cuisine_performance = (
        filtered_df[
            filtered_df["Cuisine_Type"]
            != "Unknown"
        ]
        .groupby(
            "Cuisine_Type",
            as_index=False,
        )
        .agg(
            Total_Orders=("Order_ID", "count"),
            Total_Revenue=("Revenue", "sum"),
            Average_Order_Value=(
                "Order_Value",
                "mean",
            ),
            Average_Delivery_Time=(
                "Delivery_Time_Min",
                "mean",
            ),
            Average_Restaurant_Rating=(
                "Restaurant_Rating",
                "mean",
            ),
            Cancellation_Rate=(
                "Is_Cancelled",
                "mean",
            ),
        )
    )

    cuisine_performance[
        "Cancellation_Rate"
    ] *= 100

    st.dataframe(
        cuisine_performance,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DATA QUALITY / PREPROCESSING
# ============================================================

with st.expander("🧹 Data Quality & Preprocessing"):

    st.markdown(
        """
        ### Cleaning performed

        - Missing numerical values were handled using suitable median-based methods.
        - Missing categorical information was represented as **Unknown** where appropriate.
        - Missing cancellation reasons for delivered orders were treated as **Not Applicable**.
        - Restaurant ratings above 5 were capped to the valid rating range.
        - Invalid negative profit-margin values were corrected during preprocessing.
        - Discounts exceeding order value were corrected.
        - Final amount was recalculated using order value and discount.
        - Cancelled orders were prevented from contributing delivery ratings.
        - Outliers in order value and delivery time were evaluated using the IQR method.
        - Derived analytical fields were created for downstream analysis.
        """
    )

    null_summary = (
        df.isnull()
        .sum()
        .reset_index()
    )

    null_summary.columns = [
        "Column",
        "Missing_Count",
    ]

    null_summary = null_summary[
        null_summary["Missing_Count"] > 0
    ]

    if not null_summary.empty:
        st.write("Remaining intentional / unresolved missing values:")
        st.dataframe(
            null_summary,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# DATASET OVERVIEW
# ============================================================

with st.expander("📋 Dataset Overview"):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Rows",
        f"{len(df):,}",
    )

    c2.metric(
        "Columns",
        df.shape[1],
    )

    c3.metric(
        "Customers",
        f"{df['Customer_ID'].nunique():,}",
    )

    c4.metric(
        "Restaurants",
        f"{df['Restaurant_ID'].nunique():,}",
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FILTERED DATA + DOWNLOAD
# ============================================================

with st.expander("🔎 View Filtered Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_food_delivery_data.csv",
    mime="text/csv",
)

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} records"
)
