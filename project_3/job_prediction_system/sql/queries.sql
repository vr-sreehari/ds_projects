-- ==============================================================================
-- HR Analytics & Job Acceptance Prediction System
-- Analytical Reporting Queries
-- Database: hr_analytics_db | Table: candidate_placements
-- ==============================================================================

USE hr_analytics_db;

-- ------------------------------------------------------------------------------
-- 1. OVERALL PLACEMENT ACCEPTANCE & OFFER DROPOUT RATE
-- Business Context: Baseline executive recruiting KPI.
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_candidates,
    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS total_accepted,
    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS total_dropouts,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct
FROM candidate_placements;


-- ------------------------------------------------------------------------------
-- 2. ACCEPTANCE & DROPOUT RATES BY HIRING COMPANY TIER
-- Business Context: Evaluates offer conversion across company tiers.
-- ------------------------------------------------------------------------------
SELECT 
    company_tier,
    COUNT(*) AS candidate_count,
    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS accepted_count,
    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS dropout_count,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct,
    ROUND(AVG(previous_ctc_lpa), 2) AS avg_prior_ctc,
    ROUND(AVG(expected_ctc_lpa), 2) AS avg_offered_expected_ctc
FROM candidate_placements
GROUP BY company_tier
ORDER BY company_tier ASC;


-- ------------------------------------------------------------------------------
-- 3. NOTICE PERIOD DURATION IMPACT ON PLACEMENT SUCCESS
-- Business Context: Determines whether long notice periods increase dropout risks.
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN notice_period_days = 0 THEN 'Immediate Joiner (0 days)'
        WHEN notice_period_days <= 15 THEN 'Short Notice (1-15 days)'
        WHEN notice_period_days <= 30 THEN 'Standard Notice (16-30 days)'
        WHEN notice_period_days <= 60 THEN 'Extended Notice (31-60 days)'
        ELSE 'Long Notice (>60 days)'
    END AS notice_period_bracket,
    COUNT(*) AS total_candidates,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct,
    ROUND(AVG(years_of_experience), 1) AS avg_experience_years
FROM candidate_placements
GROUP BY notice_period_bracket
ORDER BY acceptance_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- 4. SERVICE BOND REQUIREMENT IMPACT ON DROPOUT RATE
-- Business Context: Quantifies talent attrition caused by mandatory bond clauses.
-- ------------------------------------------------------------------------------
SELECT 
    bond_requirement,
    COUNT(*) AS candidate_count,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct,
    ROUND(AVG(technical_score), 2) AS avg_technical_score,
    ROUND(AVG(skills_match_percentage), 2) AS avg_skills_match_pct
FROM candidate_placements
GROUP BY bond_requirement;


-- ------------------------------------------------------------------------------
-- 5. JOB ROLE MATCH AND COMPANY TIER CROSS-ANALYSIS
-- Business Context: Measures role alignment vs brand equity interaction.
-- ------------------------------------------------------------------------------
SELECT 
    company_tier,
    job_role_match,
    COUNT(*) AS candidate_count,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct
FROM candidate_placements
GROUP BY company_tier, job_role_match
ORDER BY company_tier ASC, acceptance_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- 6. SALARY HIKE EXPECTATION GAP ANALYSIS
-- Business Context: Identifies realistic compensation increase sweet spots.
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN ((expected_ctc_lpa - previous_ctc_lpa) / previous_ctc_lpa) * 100 < 20 THEN 'Modest (<20% hike)'
        WHEN ((expected_ctc_lpa - previous_ctc_lpa) / previous_ctc_lpa) * 100 <= 50 THEN 'Standard (20-50% hike)'
        WHEN ((expected_ctc_lpa - previous_ctc_lpa) / previous_ctc_lpa) * 100 <= 100 THEN 'Aggressive (51-100% hike)'
        ELSE 'Extreme (>100% hike)'
    END AS salary_hike_bracket,
    COUNT(*) AS candidate_count,
    ROUND(AVG(status) * 100, 2) AS acceptance_rate_pct,
    ROUND((1 - AVG(status)) * 100, 2) AS dropout_rate_pct,
    ROUND(AVG(expected_ctc_lpa), 2) AS avg_expected_ctc
FROM candidate_placements
GROUP BY salary_hike_bracket
ORDER BY acceptance_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- 7. HIGH-RISK DROPOUT CANDIDATE IDENTIFICATION
-- Business Context: Flags applicants with 3 compounding dropout signals:
-- (Bond required + Notice Period > 30 days + Salary Hike > 50%).
-- ------------------------------------------------------------------------------
SELECT 
    candidate_id,
    gender,
    degree_specialization,
    years_of_experience,
    company_tier,
    notice_period_days,
    bond_requirement,
    ROUND(((expected_ctc_lpa - previous_ctc_lpa) / previous_ctc_lpa) * 100, 1) AS expected_hike_pct,
    status AS actual_status
FROM candidate_placements
WHERE bond_requirement = 'Required'
  AND notice_period_days > 30
  AND ((expected_ctc_lpa - previous_ctc_lpa) / previous_ctc_lpa) * 100 > 50
LIMIT 25;
