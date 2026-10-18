-- ==============================================================================
-- HR Analytics & Job Acceptance Prediction System
-- DDL Schema for Table: candidate_placements
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS hr_analytics_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE hr_analytics_db;

DROP TABLE IF EXISTS candidate_placements;

CREATE TABLE candidate_placements (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique candidate placement identifier',
    age_years INT NOT NULL COMMENT 'Age in years',
    gender VARCHAR(10) NOT NULL COMMENT 'Gender (Male/Female)',
    ssc_percentage DECIMAL(5, 2) NOT NULL COMMENT 'Secondary School Certificate score %',
    hsc_percentage DECIMAL(5, 2) NOT NULL COMMENT 'Higher Secondary Certificate score %',
    degree_percentage DECIMAL(5, 2) NOT NULL COMMENT 'Undergraduate Degree score %',
    degree_specialization VARCHAR(50) NOT NULL COMMENT 'Academic discipline/domain',
    technical_score DECIMAL(5, 2) NOT NULL COMMENT 'Technical test score (0-100)',
    aptitude_score DECIMAL(5, 2) NOT NULL COMMENT 'Aptitude/reasoning score (0-100)',
    communication_score DECIMAL(5, 2) NOT NULL COMMENT 'Communication score (0-100)',
    skills_match_percentage DECIMAL(5, 2) NOT NULL COMMENT 'Skills alignment to job %',
    certifications_count INT NOT NULL DEFAULT 0 COMMENT 'Number of certifications',
    internship_experience VARCHAR(5) NOT NULL COMMENT 'Internship completed (Yes/No)',
    years_of_experience DECIMAL(4, 1) NOT NULL DEFAULT 0.0 COMMENT 'Work experience in years',
    career_switch_willingness VARCHAR(20) NOT NULL COMMENT 'Willingness to pivot careers',
    relevant_experience VARCHAR(20) NOT NULL COMMENT 'Prior domain relevance',
    previous_ctc_lpa DECIMAL(5, 2) NOT NULL COMMENT 'Prior compensation in LPA',
    expected_ctc_lpa DECIMAL(5, 2) NOT NULL COMMENT 'Expected compensation in LPA',
    company_tier VARCHAR(10) NOT NULL COMMENT 'Company brand tier (Tier 1/2/3)',
    job_role_match VARCHAR(20) NOT NULL COMMENT 'Role profile alignment',
    competition_level VARCHAR(10) NOT NULL COMMENT 'Applicant competition density',
    bond_requirement VARCHAR(20) NOT NULL COMMENT 'Service bond clause (Required/Not Required)',
    notice_period_days INT NOT NULL DEFAULT 0 COMMENT 'Notice period in days',
    layoff_history VARCHAR(5) NOT NULL DEFAULT 'No' COMMENT 'Layoff history (Yes/No)',
    employment_gap_months INT NOT NULL DEFAULT 0 COMMENT 'Career gap duration in months',
    relocation_willingness VARCHAR(20) NOT NULL COMMENT 'Relocation flexibility',
    status TINYINT(1) NOT NULL COMMENT 'Target: 1 = Placed (Accepted), 0 = Not Placed (Dropout)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record insertion timestamp',
    
    -- Indexes for high-frequency analytical queries
    INDEX idx_status (status),
    INDEX idx_company_tier (company_tier),
    INDEX idx_bond_requirement (bond_requirement),
    INDEX idx_job_role_match (job_role_match),
    INDEX idx_experience_level (years_of_experience)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Candidate placement records for HR predictive analytics';
