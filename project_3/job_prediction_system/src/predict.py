"""
HR Analytics & Job Acceptance Prediction System
Inference Module & Prediction Engine
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Union, List


class JobAcceptancePredictor:
    """Production inference engine for predicting candidate job offer acceptance and dropout risks."""

    DEFAULT_MODEL_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models",
        "best_model_pipeline.joblib"
    )

    EXPECTED_NUM_COLS = [
        "age_years", "ssc_percentage", "hsc_percentage", "degree_percentage",
        "technical_score", "aptitude_score", "communication_score",
        "skills_match_percentage", "certifications_count", "years_of_experience",
        "previous_ctc_lpa", "expected_ctc_lpa", "notice_period_days",
        "employment_gap_months", "salary_hike_pct", "composite_interview_score"
    ]

    EXPECTED_CAT_COLS = [
        "gender", "degree_specialization", "internship_experience",
        "career_switch_willingness", "relevant_experience", "company_tier",
        "job_role_match", "competition_level", "bond_requirement",
        "layoff_history", "relocation_willingness"
    ]

    def __init__(self, model_path: str = None):
        """Loads serialized scikit-learn/xgboost pipeline."""
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model pipeline artifact not found at: {self.model_path}. "
                "Ensure Phase 6 training has completed successfully."
            )
        self.pipeline = joblib.load(self.model_path)

    def _engineer_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensures required numerical and categorical features exist and are properly formatted."""
        data = df.copy()

        # 1. Automatic Feature Engineering if missing
        if "salary_hike_pct" not in data.columns:
            prev_ctc = data["previous_ctc_lpa"].replace(0, 0.01)
            data["salary_hike_pct"] = ((data["expected_ctc_lpa"] - data["previous_ctc_lpa"]) / prev_ctc) * 100

        if "composite_interview_score" not in data.columns:
            data["composite_interview_score"] = (
                data["technical_score"] + data["aptitude_score"] + data["communication_score"]
            ) / 3.0

        # 2. String Cleaning & Whitespace Stripping
        for col in self.EXPECTED_CAT_COLS:
            if col in data.columns:
                data[col] = data[col].astype(str).str.strip()
                if col in ["gender", "internship_experience", "layoff_history"]:
                    data[col] = data[col].str.capitalize()

        # 3. Select columns strictly in expected schema order
        ordered_cols = self.EXPECTED_NUM_COLS + self.EXPECTED_CAT_COLS
        for col in ordered_cols:
            if col not in data.columns:
                raise ValueError(f"Missing required feature in input data: '{col}'")

        return data[ordered_cols]

    def _determine_risk(self, acceptance_prob: float) -> Dict[str, str]:
        """Categorizes candidate offer dropout risk based on acceptance probability."""
        if acceptance_prob >= 70.0:
            return {
                "dropout_risk_category": "Low Risk",
                "risk_color": "green",
                "risk_advice": "High likelihood of offer acceptance. Proceed with standard onboarding."
            }
        elif acceptance_prob >= 40.0:
            return {
                "dropout_risk_category": "Medium Risk",
                "risk_color": "orange",
                "risk_advice": "Moderate conversion risk. Recommend hiring manager check-in on compensation & role alignment."
            }
        else:
            return {
                "dropout_risk_category": "High Risk",
                "risk_color": "red",
                "risk_advice": "High probability of offer decline/dropout. Review bond clauses and salary feasibility."
            }

    def predict_single(self, candidate_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers placement acceptance probability and risk for a single candidate profile.
        
        Args:
            candidate_dict: Dictionary containing candidate features.
            
        Returns:
            Dictionary with predicted status, probability percentage, and risk classification.
        """
        input_df = pd.DataFrame([candidate_dict])
        prepared_df = self._engineer_and_validate(input_df)

        # Model inference
        prob_placed = float(self.pipeline.predict_proba(prepared_df)[0][1]) * 100.0
        prob_placed = round(prob_placed, 2)
        prob_dropout = round(100.0 - prob_placed, 2)
        prediction_label = int(self.pipeline.predict(prepared_df)[0])

        status_text = "Placed" if prediction_label == 1 else "Not Placed"
        risk_info = self._determine_risk(prob_placed)

        return {
            "predicted_status": status_text,
            "predicted_label": prediction_label,
            "acceptance_probability": prob_placed,
            "dropout_probability": prob_dropout,
            "dropout_risk_category": risk_info["dropout_risk_category"],
            "risk_color": risk_info["risk_color"],
            "risk_advice": risk_info["risk_advice"]
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Infers acceptance probability and risk tags for a batch DataFrame of candidates.
        
        Args:
            df: DataFrame containing applicant records.
            
        Returns:
            Original DataFrame augmented with prediction outcomes and risk scores.
        """
        prepared_df = self._engineer_and_validate(df)
        probabilities = self.pipeline.predict_proba(prepared_df)[:, 1] * 100.0
        predictions = self.pipeline.predict(prepared_df)

        result_df = df.copy()
        result_df["predicted_status"] = np.where(predictions == 1, "Placed", "Not Placed")
        result_df["acceptance_probability_%"] = np.round(probabilities, 2)
        result_df["dropout_probability_%"] = np.round(100.0 - probabilities, 2)
        
        # Vectorized risk categorization
        conditions = [
            result_df["acceptance_probability_%"] >= 70.0,
            result_df["acceptance_probability_%"] >= 40.0
        ]
        choices = ["Low Risk", "Medium Risk"]
        result_df["dropout_risk_category"] = np.select(conditions, choices, default="High Risk")

        return result_df


if __name__ == "__main__":
    print("=" * 70)
    print("🎯 Testing JobAcceptancePredictor Inference Module")
    print("=" * 70)

    predictor = JobAcceptancePredictor()

    # 1. Test High-Acceptance Candidate Profile
    ideal_candidate = {
        "age_years": 24,
        "gender": "Female",
        "ssc_percentage": 78.5,
        "hsc_percentage": 82.0,
        "degree_percentage": 85.0,
        "degree_specialization": "Computer Science",
        "technical_score": 88.0,
        "aptitude_score": 82.0,
        "communication_score": 80.0,
        "skills_match_percentage": 88.0,
        "certifications_count": 2,
        "internship_experience": "Yes",
        "years_of_experience": 2,
        "career_switch_willingness": "Willing",
        "relevant_experience": "Relevant",
        "previous_ctc_lpa": 6.0,
        "expected_ctc_lpa": 8.0,
        "company_tier": "Tier 1",
        "job_role_match": "Matched",
        "competition_level": "Low",
        "bond_requirement": "Not Required",
        "notice_period_days": 15,
        "layoff_history": "No",
        "employment_gap_months": 0,
        "relocation_willingness": "Willing"
    }

    result_ideal = predictor.predict_single(ideal_candidate)
    print("\n[+] Single Candidate Prediction (Ideal Profile):")
    for k, v in result_ideal.items():
        print(f"    {k:<25}: {v}")

    # 2. Test High-Dropout-Risk Candidate Profile
    risk_candidate = {
        "age_years": 32,
        "gender": "Male",
        "ssc_percentage": 60.0,
        "hsc_percentage": 62.0,
        "degree_percentage": 65.0,
        "degree_specialization": "Others",
        "technical_score": 52.0,
        "aptitude_score": 55.0,
        "communication_score": 58.0,
        "skills_match_percentage": 50.0,
        "certifications_count": 0,
        "internship_experience": "No",
        "years_of_experience": 4,
        "career_switch_willingness": "Not Willing",
        "relevant_experience": "Not Relevant",
        "previous_ctc_lpa": 4.0,
        "expected_ctc_lpa": 12.0,  # 200% hike
        "company_tier": "Tier 3",
        "job_role_match": "Not Matched",
        "competition_level": "High",
        "bond_requirement": "Required",
        "notice_period_days": 90,
        "layoff_history": "Yes",
        "employment_gap_months": 18,
        "relocation_willingness": "Not Willing"
    }

    result_risk = predictor.predict_single(risk_candidate)
    print("\n[+] Single Candidate Prediction (High-Risk Profile):")
    for k, v in result_risk.items():
        print(f"    {k:<25}: {v}")

    # 3. Test Batch Prediction on Sample Cleaned Dataset
    csv_sample_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "dataset",
        "cleaned_placement_data.csv"
    )
    if os.path.exists(csv_sample_path):
        sample_df = pd.read_csv(csv_sample_path).head(5)
        batch_out = predictor.predict_batch(sample_df)
        print("\n[+] Batch Prediction Output (First 5 candidates):")
        cols_to_show = ["company_tier", "bond_requirement", "predicted_status", "acceptance_probability_%", "dropout_risk_category"]
        print(batch_out[cols_to_show].to_string(index=False))

    print("\n" + "=" * 70)
    print("✅ All Inference Engine Tests Passed Successfully!")
    print("=" * 70)
