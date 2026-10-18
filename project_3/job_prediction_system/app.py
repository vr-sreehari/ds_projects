"""
HR Analytics & Job Acceptance Prediction System
Interactive Streamlit Web Application
"""

import os
import sys
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add parent directory to system path for modular imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.predict import JobAcceptancePredictor

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Job Acceptance Prediction System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern typography and cards
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6c757d;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1a1f36;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #8898aa;
        margin-top: 4px;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 30px;
        text-align: center;
    }
    .badge-low-risk {
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    .badge-medium-risk {
        background-color: #fff3cd;
        color: #664d03;
        border: 1px solid #ffecb5;
    }
    .badge-high-risk {
        background-color: #f8d7da;
        color: #842029;
        border: 1px solid #f5c2c7;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. CACHED DATA & INFERENCE ENGINE INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_resource
def load_predictor():
    """Initializes and caches the trained JobAcceptancePredictor."""
    return JobAcceptancePredictor()

@st.cache_data(ttl=600)
def load_dataset():
    """Loads placement records from MySQL if available, otherwise falls back to clean CSV."""
    load_dotenv()
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "12345678")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "hr_analytics_db")
    
    # Try MySQL Connection First
    try:
        conn_str = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            query = text("SELECT * FROM candidate_placements LIMIT 50000;")
            df = pd.read_sql(query, conn)
            # Remove candidate_id index if loaded as column
            if "candidate_id" in df.columns:
                df = df.drop(columns=["candidate_id"])
            return df, "MySQL Database (hr_analytics_db)"
    except Exception:
        pass

    # Fallback to local CSV
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "cleaned_placement_data.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df, "Local CSV (dataset/cleaned_placement_data.csv)"
    
    st.error("No dataset found. Please run the Phase 3 cleaning script.")
    st.stop()


# Load Global Assets
df_raw, data_source_name = load_dataset()
predictor = load_predictor()

# Compute engineered features if missing in display dataset
if "salary_hike_pct" not in df_raw.columns:
    df_raw["salary_hike_pct"] = ((df_raw["expected_ctc_lpa"] - df_raw["previous_ctc_lpa"]) / df_raw["previous_ctc_lpa"]) * 100
if "composite_interview_score" not in df_raw.columns:
    df_raw["composite_interview_score"] = (df_raw["technical_score"] + df_raw["aptitude_score"] + df_raw["communication_score"]) / 3.0


# -----------------------------------------------------------------------------
# 3. HEADER & EXECUTIVE KPIS
# -----------------------------------------------------------------------------
st.title("🎯 Job Acceptance Prediction System")
st.caption(f"HR Talent Acquisition & Placement Predictive Analytics Engine • Connected to: `{data_source_name}`")

# Calculate KPI Metrics
total_candidates = len(df_raw)
placed_count = int(df_raw["status"].sum())
dropout_count = total_candidates - placed_count
placement_rate = (placed_count / total_candidates) * 100.0
dropout_rate = (dropout_count / total_candidates) * 100.0
avg_skills_match = df_raw["skills_match_percentage"].mean()
avg_tech_score = df_raw["technical_score"].mean()

# Render Top KPI Cards
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Candidates</div>
        <div class="kpi-value">{total_candidates:,}</div>
        <div class="kpi-subtext">Audited talent pool</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Placement Rate</div>
        <div class="kpi-value" style="color: #2ca02c;">{placement_rate:.1f}%</div>
        <div class="kpi-subtext">{placed_count:,} offers accepted</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Offer Dropout Rate</div>
        <div class="kpi-value" style="color: #d62728;">{dropout_rate:.1f}%</div>
        <div class="kpi-subtext">{dropout_count:,} candidates declined</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Skills Match</div>
        <div class="kpi-value" style="color: #1f77b4;">{avg_skills_match:.1f}%</div>
        <div class="kpi-subtext">Job alignment benchmark</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Tech Score</div>
        <div class="kpi-value" style="color: #9467bd;">{avg_tech_score:.1f}</div>
        <div class="kpi-subtext">Screening assessment mean</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# -----------------------------------------------------------------------------
# 4. TAB NAVIGATION
# -----------------------------------------------------------------------------
tab_analytics, tab_predict, tab_batch, tab_insights = st.tabs([
    "📊 Executive Analytics",
    "🔮 Candidate Acceptance Predictor",
    "📁 Batch Candidate Scoring",
    "🧠 Model Transparency & Drivers"
])


# =============================================================================
# TAB 1: EXECUTIVE ANALYTICS
# =============================================================================
with tab_analytics:
    st.subheader("Placement Dynamics & Behavioral Insights")
    
    # Sidebar Filters
    with st.sidebar:
        st.header("🔍 Analytics Filters")
        selected_tiers = st.multiselect(
            "Company Tier:",
            options=sorted(df_raw["company_tier"].unique().tolist()),
            default=sorted(df_raw["company_tier"].unique().tolist())
        )
        selected_bonds = st.multiselect(
            "Bond Requirement:",
            options=sorted(df_raw["bond_requirement"].unique().tolist()),
            default=sorted(df_raw["bond_requirement"].unique().tolist())
        )
        selected_roles = st.multiselect(
            "Job Role Match:",
            options=sorted(df_raw["job_role_match"].unique().tolist()),
            default=sorted(df_raw["job_role_match"].unique().tolist())
        )
        selected_specs = st.multiselect(
            "Degree Specialization:",
            options=sorted(df_raw["degree_specialization"].unique().tolist()),
            default=sorted(df_raw["degree_specialization"].unique().tolist())
        )

    # Apply Filters
    df_filtered = df_raw[
        (df_raw["company_tier"].isin(selected_tiers)) &
        (df_raw["bond_requirement"].isin(selected_bonds)) &
        (df_raw["job_role_match"].isin(selected_roles)) &
        (df_raw["degree_specialization"].isin(selected_specs))
    ]

    if df_filtered.empty:
        st.warning("No records match the selected filter combination. Please broaden your selection.")
    else:
        # Row 1: Charts
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            # Chart 1: Bond Requirement Impact
            bond_data = df_filtered.groupby("bond_requirement")["status"].agg(
                Accepted=lambda s: (s == 1).sum(),
                Dropout=lambda s: (s == 0).sum(),
                Rate=lambda s: s.mean() * 100.0
            ).reset_index()
            
            fig_bond = go.Figure()
            fig_bond.add_trace(go.Bar(
                name="Accepted (Placed)",
                x=bond_data["bond_requirement"],
                y=bond_data["Accepted"],
                marker_color="#2ca02c",
                text=[f"{val:,}" for val in bond_data["Accepted"]],
                textposition="auto"
            ))
            fig_bond.add_trace(go.Bar(
                name="Dropout (Declined)",
                x=bond_data["bond_requirement"],
                y=bond_data["Dropout"],
                marker_color="#d62728",
                text=[f"{val:,}" for val in bond_data["Dropout"]],
                textposition="auto"
            ))
            fig_bond.update_layout(
                barmode="stack",
                title="<b>Offer Acceptance vs. Dropout by Service Bond Requirement</b>",
                xaxis_title="Bond Clause",
                yaxis_title="Total Candidates",
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bond, use_container_width=True)

        with row1_col2:
            # Chart 2: Acceptance by Company Tier & Role Alignment
            tier_role_data = df_filtered.groupby(["company_tier", "job_role_match"])["status"].mean().reset_index()
            tier_role_data["Acceptance_Rate_%"] = tier_role_data["status"] * 100.0

            fig_tier = px.bar(
                tier_role_data,
                x="company_tier",
                y="Acceptance_Rate_%",
                color="job_role_match",
                barmode="group",
                title="<b>Acceptance Rate (%) by Company Tier & Role Alignment</b>",
                labels={"company_tier": "Hiring Company Tier", "Acceptance_Rate_%": "Acceptance Rate (%)", "job_role_match": "Role Fit"},
                color_discrete_map={"Matched": "#1f77b4", "Not Matched": "#ff7f0e"},
                template="plotly_white"
            )
            fig_tier.update_layout(
                yaxis_range=[0, 50],
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_tier, use_container_width=True)

        # Row 2: Charts
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            # Chart 3: Salary Hike Expectation Distribution
            df_filtered_hike = df_filtered[df_filtered["salary_hike_pct"].between(-30, 200)].copy()
            df_filtered_hike["Outcome"] = df_filtered_hike["status"].map({1: "Accepted (1)", 0: "Dropout (0)"})
            
            fig_hike = px.box(
                df_filtered_hike,
                x="Outcome",
                y="salary_hike_pct",
                color="Outcome",
                color_discrete_map={"Accepted (1)": "#2ca02c", "Dropout (0)": "#d62728"},
                title="<b>Expected Salary Hike (%) Distribution by Outcome</b>",
                labels={"salary_hike_pct": "Expected Salary Hike (%)"},
                template="plotly_white"
            )
            fig_hike.update_layout(showlegend=False)
            st.plotly_chart(fig_hike, use_container_width=True)

        with row2_col2:
            # Chart 4: Skills Alignment vs Composite Interview Score
            sample_scatter = df_filtered.sample(n=min(1200, len(df_filtered)), random_state=42).copy()
            sample_scatter["Outcome"] = sample_scatter["status"].map({1: "Accepted", 0: "Dropout"})

            fig_scatter = px.scatter(
                sample_scatter,
                x="skills_match_percentage",
                y="composite_interview_score",
                color="Outcome",
                color_discrete_map={"Accepted": "#2ca02c", "Dropout": "#d62728"},
                opacity=0.6,
                title="<b>Skills Match % vs. Composite Interview Score</b>",
                labels={
                    "skills_match_percentage": "Skills Alignment Match (%)",
                    "composite_interview_score": "Composite Interview Score (0-100)"
                },
                template="plotly_white"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)


# =============================================================================
# TAB 2: INDIVIDUAL CANDIDATE PREDICTOR
# =============================================================================
with tab_predict:
    st.subheader("Predict Job Acceptance & Evaluate Dropout Risk")
    st.markdown("Enter candidate qualifications and contract terms to compute acceptance probability in real-time.")

    with st.form("candidate_prediction_form"):
        form_col1, form_col2, form_col3 = st.columns(3)

        with form_col1:
            st.markdown("##### 🎓 1. Academic & Demographics")
            inp_age = st.number_input("Candidate Age (Years)", min_value=18, max_value=60, value=25, step=1)
            inp_gender = st.selectbox("Gender", options=["Male", "Female"])
            inp_spec = st.selectbox(
                "Undergraduate Degree Specialization",
                options=["Computer Science", "Information Technology", "Electronics", "Mechanical", "Others"]
            )
            inp_ssc = st.slider("SSC (10th) Percentage", min_value=40.0, max_value=100.0, value=75.0, step=0.5)
            inp_hsc = st.slider("HSC (12th) Percentage", min_value=40.0, max_value=100.0, value=78.0, step=0.5)
            inp_degree = st.slider("Undergraduate Degree Percentage", min_value=40.0, max_value=100.0, value=80.0, step=0.5)

        with form_col2:
            st.markdown("##### 💼 2. Skills & Work History")
            inp_tech = st.slider("Technical Assessment Score", min_value=0.0, max_value=100.0, value=82.0, step=1.0)
            inp_apt = st.slider("Aptitude / Reasoning Score", min_value=0.0, max_value=100.0, value=75.0, step=1.0)
            inp_comm = st.slider("Communication Evaluation Score", min_value=0.0, max_value=100.0, value=72.0, step=1.0)
            inp_skills_match = st.slider("Skills Alignment to Role (%)", min_value=0.0, max_value=100.0, value=85.0, step=1.0)
            inp_certs = st.number_input("Completed Certifications", min_value=0, max_value=15, value=2, step=1)
            inp_exp_years = st.number_input("Total Years of Work Experience", min_value=0.0, max_value=25.0, value=2.0, step=0.5)
            inp_internship = st.selectbox("Completed Internships?", options=["Yes", "No"])
            inp_relevant_exp = st.selectbox("Prior Experience Role Alignment", options=["Relevant", "Not Relevant"])

        with form_col3:
            st.markdown("##### 📑 3. Offer Terms & Hiring Profile")
            inp_prev_ctc = st.number_input("Previous CTC (LPA)", min_value=0.5, max_value=50.0, value=5.5, step=0.5)
            inp_exp_ctc = st.number_input("Offered / Expected CTC (LPA)", min_value=1.0, max_value=60.0, value=8.0, step=0.5)
            inp_tier = st.selectbox("Hiring Organization Tier", options=["Tier 1", "Tier 2", "Tier 3"])
            inp_role_match = st.selectbox("Job Role Match", options=["Matched", "Not Matched"])
            inp_bond = st.selectbox("Service Bond Clause", options=["Not Required", "Required"])
            inp_notice = st.selectbox("Current Notice Period (Days)", options=[0, 15, 30, 60, 90], index=1)
            inp_competition = st.selectbox("Market Competition Level", options=["Low", "Medium", "High"])
            inp_relocation = st.selectbox("Willing to Relocate?", options=["Willing", "Not Willing"])
            inp_career_switch = st.selectbox("Career Switch Willingness?", options=["Willing", "Not Willing"])
            inp_layoff = st.selectbox("Experienced Prior Layoff?", options=["No", "Yes"])
            inp_gap = st.number_input("Employment Career Gap (Months)", min_value=0, max_value=60, value=0, step=1)

        submit_prediction = st.form_submit_button("🚀 Compute Job Acceptance & Risk Score", type="primary", use_container_width=True)

    if submit_prediction:
        candidate_input = {
            "age_years": int(inp_age),
            "gender": str(inp_gender),
            "ssc_percentage": float(inp_ssc),
            "hsc_percentage": float(inp_hsc),
            "degree_percentage": float(inp_degree),
            "degree_specialization": str(inp_spec),
            "technical_score": float(inp_tech),
            "aptitude_score": float(inp_apt),
            "communication_score": float(inp_comm),
            "skills_match_percentage": float(inp_skills_match),
            "certifications_count": int(inp_certs),
            "internship_experience": str(inp_internship),
            "years_of_experience": float(inp_exp_years),
            "career_switch_willingness": str(inp_career_switch),
            "relevant_experience": str(inp_relevant_exp),
            "previous_ctc_lpa": float(inp_prev_ctc),
            "expected_ctc_lpa": float(inp_exp_ctc),
            "company_tier": str(inp_tier),
            "job_role_match": str(inp_role_match),
            "competition_level": str(inp_competition),
            "bond_requirement": str(inp_bond),
            "notice_period_days": int(inp_notice),
            "layoff_history": str(inp_layoff),
            "employment_gap_months": int(inp_gap),
            "relocation_willingness": str(inp_relocation)
        }

        # Run Inference
        result = predictor.predict_single(candidate_input)
        prob_val = result["acceptance_probability"]
        risk_cat = result["dropout_risk_category"]

        st.markdown("---")
        st.subheader("Prediction Result & Risk Diagnostic")

        res_col1, res_col2 = st.columns([1.1, 1])

        with res_col1:
            # Plotly Gauge Chart for Acceptance Probability
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob_val,
                number={"suffix": "%", "font": {"size": 42, "weight": "bold"}},
                title={"text": "<b>Job Offer Acceptance Probability</b>", "font": {"size": 17}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#495057"},
                    "bar": {"color": "#1f77b4", "thickness": 0.28},
                    "bgcolor": "white",
                    "borderwidth": 1,
                    "bordercolor": "#dee2e6",
                    "steps": [
                        {"range": [0, 40], "color": "#f8d7da"},
                        {"range": [40, 70], "color": "#fff3cd"},
                        {"range": [70, 100], "color": "#d1e7dd"}
                    ],
                    "threshold": {
                        "line": {"color": "#0d6efd", "width": 4},
                        "thickness": 0.8,
                        "value": prob_val
                    }
                }
            ))
            fig_gauge.update_layout(height=290, margin=dict(l=20, r=20, t=50, b=20), template="plotly_white")
            st.plotly_chart(fig_gauge, use_container_width=True)

        with res_col2:
            st.markdown("#### Outcome Assessment")
            
            badge_class = "badge-low-risk" if risk_cat == "Low Risk" else ("badge-medium-risk" if risk_cat == "Medium Risk" else "badge-high-risk")
            
            if result["predicted_status"] == "Placed":
                st.success(f"### Predicted Status: **Offer Accepted (Placed)**")
            else:
                st.error(f"### Predicted Status: **Offer Declined (Dropout Risk)**")

            st.markdown(f"**Dropout Risk Category:** <span class='risk-badge {badge_class}'>{risk_cat}</span>", unsafe_allow_html=True)
            st.markdown(f"**Strategic HR Action Advice:**\n> {result['risk_advice']}")

            # Key Feature Signals
            hike_computed = ((inp_exp_ctc - inp_prev_ctc) / max(inp_prev_ctc, 0.1)) * 100
            comp_score = (inp_tech + inp_apt + inp_comm) / 3

            st.markdown(f"""
            **Signal Diagnostics:**
            - **Offered Salary Hike:** `{hike_computed:.1f}%` (Market standard: 20-40%)
            - **Composite Assessment Score:** `{comp_score:.1f} / 100`
            - **Contract Clause:** `{inp_bond}`
            - **Role Alignment:** `{inp_role_match}`
            """)


# =============================================================================
# TAB 3: BATCH CSV PREDICTION
# =============================================================================
with tab_batch:
    st.subheader("Bulk Candidate Scoring Engine")
    st.markdown("Upload applicant CSV files to generate predictions, acceptance probabilities, and dropout risk tags at scale.")

    uploaded_file = st.file_uploader("Upload Applicant CSV File", type=["csv"])

    # Template Generator Button
    sample_template = df_raw.drop(columns=["status", "salary_hike_pct", "composite_interview_score"], errors="ignore").head(5)
    csv_buffer = io.StringIO()
    sample_template.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="📥 Download Sample Applicant CSV Template",
        data=csv_buffer.getvalue(),
        file_name="applicant_sample_template.csv",
        mime="text/csv"
    )

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            st.success(f"Uploaded `{uploaded_file.name}` successfully with {len(batch_df):,} applicant records.")

            with st.spinner("Scoring candidate profiles with XGBoost inference engine..."):
                scored_results = predictor.predict_batch(batch_df)

            # Metrics Summary of Batch
            b_total = len(scored_results)
            b_placed = (scored_results["predicted_status"] == "Placed").sum()
            b_dropout = b_total - b_placed
            b_high_risk = (scored_results["dropout_risk_category"] == "High Risk").sum()

            b_col1, b_col2, b_col3, b_col4 = st.columns(4)
            b_col1.metric("Scored Applicants", f"{b_total:,}")
            b_col2.metric("Predicted Placed", f"{b_placed:,}", f"{b_placed/b_total*100:.1f}%")
            b_col3.metric("Predicted Dropouts", f"{b_dropout:,}", f"{b_dropout/b_total*100:.1f}%", delta_color="inverse")
            b_col4.metric("High-Risk Dropouts", f"{b_high_risk:,}", f"{b_high_risk/b_total*100:.1f}%", delta_color="inverse")

            # Data Preview with Highlights
            st.markdown("#### Scored Candidate Results Preview")
            display_cols = [
                "company_tier", "degree_specialization", "years_of_experience",
                "technical_score", "bond_requirement", "job_role_match",
                "predicted_status", "acceptance_probability_%", "dropout_risk_category"
            ]
            cols_to_render = [c for c in display_cols if c in scored_results.columns]
            st.dataframe(scored_results[cols_to_render].head(50), use_container_width=True)

            # Export Button
            out_buffer = io.StringIO()
            scored_results.to_csv(out_buffer, index=False)
            st.download_button(
                label="📥 Download Fully Scored Applicant CSV",
                data=out_buffer.getvalue(),
                file_name="scored_candidate_predictions.csv",
                mime="text/csv",
                type="primary"
            )

        except Exception as e:
            st.error(f"Error processing uploaded batch CSV: {e}")


# =============================================================================
# TAB 4: MODEL TRANSPARENCY & INSIGHTS
# =============================================================================
with tab_insights:
    st.subheader("Machine Learning Model Transparency & Drivers")
    st.markdown("Evaluation leaderboard, cross-validation metrics, and tree feature importance weights.")

    t_col1, t_col2 = st.columns([1.1, 1])

    with t_col1:
        st.markdown("#### Model Architecture & Evaluation Leaderboard")
        leaderboard_data = pd.DataFrame({
            "Model Architecture": ["XGBoost (Tuned Champion)", "LightGBM Classifier", "Random Forest Classifier", "Logistic Regression"],
            "Accuracy": ["90.39%", "90.39%", "88.20%", "86.37%"],
            "Precision": ["85.04%", "84.75%", "86.03%", "79.29%"],
            "Recall": ["82.82%", "83.21%", "72.84%", "74.39%"],
            "F1-Score": ["0.8391", "0.8398", "0.7888", "0.7676"],
            "ROC-AUC": ["0.9669", "0.9671", "0.9533", "0.9362"]
        })
        st.dataframe(leaderboard_data, use_container_width=True, hide_index=True)

        st.markdown("""
        **Champion Model Specifications:**
        - **Algorithm:** Tuned Extreme Gradient Boosting (`XGBClassifier`)
        - **Pipeline Preprocessing:** `StandardScaler` (16 numeric columns) + `OneHotEncoder` (11 categoricals)
        - **Holdout Test Set:** 10,000 candidate records (Stratified 20% split)
        - **Cross-Validation ROC-AUC:** **0.9690** (3-fold Stratified CV)
        """)

    with t_col2:
        st.markdown("#### Top 10 Most Influential Features")
        
        # Feature Importances Plot
        feature_importance_data = pd.DataFrame({
            "Feature": [
                "technical_score",
                "years_of_experience",
                "job_role_match_Matched",
                "layoff_history_No",
                "internship_experience_No",
                "relevant_experience_Not Relevant",
                "skills_match_percentage",
                "bond_requirement_Not Required",
                "salary_hike_pct",
                "competition_level_High"
            ],
            "Relative Importance": [0.1423, 0.0996, 0.0845, 0.0701, 0.0690, 0.0621, 0.0542, 0.0498, 0.0472, 0.0436]
        }).sort_values(by="Relative Importance", ascending=True)

        fig_imp = px.bar(
            feature_importance_data,
            x="Relative Importance",
            y="Feature",
            orientation="h",
            color="Relative Importance",
            color_continuous_scale="Blues",
            title="<b>Tree Feature Importance Weights</b>",
            template="plotly_white"
        )
        fig_imp.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Strategic HR Recommendations Derived from ML Drivers")
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    
    with rec_col1:
        st.info("""
        **1. Eliminate Restrictive Bonds**
        Service bonds trigger a **~26% decline** in candidate offer acceptance. High-caliber talent with competing offers consistently declines bond clauses.
        """)
    with rec_col2:
        st.info("""
        **2. Prioritize Role Fit Early**
        A mismatched job role cuts acceptance rate by more than half (from **34.7% down to 15.7%**), regardless of company brand tier.
        """)
    with rec_col3:
        st.info("""
        **3. Benchmark Salary Hikes**
        Candidates expecting salary increases **>75%** exhibit twice the dropout rate. Discuss compensation ranges early in the screening process.
        """)
