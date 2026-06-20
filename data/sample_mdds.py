"""
Sample Model Development Documents for demonstration.

Three scenarios covering the range of documentation quality:
  MDD_STRONG  — well-documented model, most SR 11-7 requirements met
  MDD_PARTIAL — partial documentation, common real-world gaps
  MDD_WEAK    — poorly documented model, multiple critical gaps

This is the realistic range seen in MRM practice at tier-1 banks.
"""

MDD_STRONG = """
MODEL DEVELOPMENT DOCUMENT
===========================
Model Name: RetailPD_v3.2 — Retail Probability of Default Model
Model Type: Credit Scoring
Version: 3.2
Date: March 2025
Business Owner: Head of Retail Credit Risk, John Davies (signed)
Technical Owner: Lead Data Scientist, Sarah Chen (signed)

1. PURPOSE AND SCOPE
--------------------
This model estimates the 12-month probability of default (PD) for retail mortgage
applicants at origination. It is used exclusively for credit decisioning at the
point of application. It is NOT approved for use in IFRS 9 provisioning or
regulatory capital calculations.

Out of scope: existing portfolio management, collections scoring, IFRS 9 staging.
These are covered by separate approved models (MGMT_PD_v2.1 and COLL_v4.0).

The model is registered in the Model Inventory under ID CREDIT-023, assigned to
Tier 2 (medium complexity, high materiality) by the Model Risk Committee on 12 Jan 2025.

2. METHODOLOGY
--------------
Algorithm: Gradient Boosting (XGBoost 2.0), selected after comparison against
logistic regression (baseline) and random forest alternatives.

Logistic regression was rejected due to inability to capture non-linear interactions
between loan-to-value ratio and income volatility observed in training data.
Random forest was comparable in performance but inferior in interpretability for
regulatory purposes.

XGBoost was chosen for: (a) superior predictive performance (+4 Gini vs logistic),
(b) native handling of missing values, (c) SHAP-based interpretability support,
(d) established use in peer institution models (per Basel BCBS studies 2023).

Key features (top 10 by SHAP importance):
- Loan-to-value ratio at origination
- Debt-to-income ratio
- Bureau score at application
- Time at current address (stability proxy)
- Number of credit searches in last 6 months
- Current account balance stability (12m CV)
- Employment type (permanent/contract/self-employed)
- Number of existing credit facilities
- Payment history on existing facilities (24m)
- Property type (house/flat/new-build)

Feature engineering: bureau score was winsorised at 1st/99th percentile to
reduce outlier influence. LTV was capped at 100% (no negative equity scenarios
in training sample). Missing values in current account data (<3% of sample)
imputed using median by employment category.

3. TRAINING DATA
----------------
Source: Internal mortgage origination data 2018–2022 (pre-pandemic baseline plus
pandemic cohorts). Obtained from Data Warehouse via approved data access request
DAR-2024-112. Data lineage documented in Appendix B.

Volume: 847,291 applications (312,844 defaults, 36.9% default rate — reflecting
economic stress period inclusion).

Default definition: 90+ days past due OR formal forbearance within 12 months.
Consistent with EBA GL 2017/06.

Time period rationale: 2018–2022 captures both benign economic conditions (2018–19),
COVID shock (2020), and recovery (2021–22). Post-2022 data excluded due to
incomplete 12-month outcome window at time of development.

Data quality assessment conducted by Data Governance team (report DQ-2024-089):
- Completeness: 97.4% across required fields
- Known issues: self-employed income data sparse pre-2020 (7.2% missing). Handled
  via median imputation by employment type. Materiality assessed as low — self-employed
  segment represents 11% of mortgage book.

Train/test split: 70/30 temporal split (train 2018–2021, test 2022).
Out-of-time validation on 2023 data (post-development cohort, N=124,000).

4. MODEL ASSUMPTIONS
--------------------
1. Economic regime: training data captures a plausible range of economic conditions,
   but model should be recalibrated if UK base rate exceeds 7% for more than 6 months
   (outside training distribution).
2. Product mix: model assumes stable product mix. Material shift toward high-LTV
   products (>90% LTV) would require re-assessment.
3. Data availability: model requires bureau score at application. If bureau data
   is unavailable (estimated <1% of cases), application should be escalated to
   manual underwriting.
4. Default definition stability: model is calibrated to 90DPD definition.
   Change in default definition requires recalibration.

Assumption testing: sensitivity analysis conducted for assumptions 1 and 2 (Appendix C).
Under stressed rate scenario (+200bps), model Gini declines from 0.68 to 0.61 —
within acceptable range. High-LTV product stress shows increased miscalibration,
confirmed by sensitivity analysis.

5. KNOWN LIMITATIONS
--------------------
1. Economic extrapolation: model was not trained on a rising rate environment
   above 4%. Performance in a high-rate sustained downturn is uncertain.
2. New-build property: new-build segment (8% of training data) shows higher
   prediction error due to thinner data. Users should apply +15bps PD floor
   for new-build applications per credit policy.
3. Self-employed income volatility: imputation approach for missing self-employed
   income reduces model precision for this segment. KS statistic 0.38 vs 0.44
   for employed applicants.
4. Geographic concentration: training data over-represents South East England (44%
   vs 31% of current book). Regional performance monitoring recommended.

6. MODEL PERFORMANCE
--------------------
Development sample (2018–2021, N=593,104):
  Gini: 0.68 | KS: 0.44 | AUC: 0.84

Hold-out test (2022, N=254,187):
  Gini: 0.66 | KS: 0.42 | AUC: 0.83

Out-of-time validation (2023, N=124,000):
  Gini: 0.64 | KS: 0.40 | AUC: 0.82

Benchmark comparison:
  Internal logistic regression baseline: Gini 0.61 (−7pp vs XGBoost)
  Industry benchmark (BCBS 2023 peer study): median Gini 0.65 for similar segments
  RetailPD_v3.2 performance is above peer median.

Backtesting: Annual backtesting performed for predecessor model RetailPD_v3.1.
Results in Appendix D. PD prediction within 5% of actual default rates for
prime segment. Some miscalibration in near-prime (10–15% overprediction).
Planned recalibration in v3.3 (Q3 2025).

7. MONITORING PLAN
------------------
Owner: Credit Risk Analytics team (Sarah Chen, Lead Data Scientist)
Frequency: Monthly reporting, quarterly formal review

Metrics monitored:
  - Gini (monthly): alert threshold <0.60, review threshold <0.55
  - PSI on input features (monthly): alert >0.10, model review trigger >0.20
  - Default rate vs predicted (quarterly): alert if actual/predicted ratio >1.15
  - KS statistic (quarterly): alert <0.35

Recalibration trigger: Gini <0.60 for 2 consecutive months OR PSI >0.20
Redevelopment trigger: Gini <0.55 OR fundamental change in product mix
Retirement criteria: replacement model approved by MRC prior to decommission

Monitoring reports distributed to: Head of Credit Risk, CRO office, Model Risk

8. GOVERNANCE
-------------
Model Inventory: CREDIT-023
Risk Tier: Tier 2 (assigned MRC meeting 12 Jan 2025)
Prior version: RetailPD_v3.1 (retired Feb 2025)
Change from v3.1: updated training data to include 2022 cohort; algorithm unchanged

Change management: material changes (algorithm, feature set, retraining data)
require MRC approval. Recalibration without algorithm change requires MRC notification.
Threshold for materiality: Gini change >5pp or feature set change >20%.

Documentation version: 3.2.1 | Last updated: 15 March 2025
Version history in Appendix A.
"""


MDD_PARTIAL = """
MODEL DEVELOPMENT DOCUMENT
Model Name: FraudScorer_ML — Real-time Payment Fraud Detection
Version: 2.0
Date: January 2025
Author: Payments Analytics Team

PURPOSE
The FraudScorer_ML model detects fraudulent card-not-present transactions in
real-time at payment authorisation. It generates a fraud probability score (0-100)
which feeds into the payment authorisation rules engine.

This is a business-critical model processing approximately 2 million transactions
per day. Incorrect fraud flags result in transaction decline (customer friction);
missed fraud results in financial loss and reputational damage.

METHODOLOGY
We use a neural network approach — specifically a feedforward network with 3 hidden
layers. This architecture was chosen because it handles the high-dimensional
transaction feature space well.

Key features include transaction amount, merchant category, time of day, device
fingerprint, velocity features (transactions in last hour/day/week), and historical
spending patterns.

DATA
Training data was sourced from our payment processing system covering 2022-2024.
The dataset contains approximately 15 million transactions with confirmed fraud labels.
Fraud prevalence in training data: 0.8% (class imbalance handled via oversampling).

No formal data quality report was conducted but the data engineering team reviewed
the data extract and confirmed it looked reasonable.

PERFORMANCE
The model achieves strong performance on test data:
- AUC: 0.96
- Precision at 3% FPR: 0.78
- Recall at 3% FPR: 0.71

This compares favourably to the previous rule-based system.

LIMITATIONS
Real-time scoring means we cannot use some features that would be available in
batch processing. The model may underperform on new merchant categories not well
represented in training data.

DEPLOYMENT
Model is deployed to production via the payments platform API. Score threshold for
decline is set by the rules engine team. Model scoring happens in <50ms.

MONITORING
The payments analytics team reviews model performance metrics quarterly. Key metrics
include fraud detection rate and false positive rate.
"""


MDD_WEAK = """
Credit Model Documentation

This document describes our new credit scoring model for small business lending.

The model uses machine learning to predict whether a small business loan will default.
We trained it on our historical loan data and it performs well.

Features used: various financial metrics from the loan application and bureau data.

The model was developed by the data science team and validated internally.
Performance is good — better than our previous model.

We plan to monitor it going forward.

Owner: Data Science Team
Date: Q4 2024
"""

SAMPLE_MDDS = {
    "RetailPD_v3.2 (Strong documentation)": MDD_STRONG,
    "FraudScorer_ML (Partial documentation)": MDD_PARTIAL,
    "SME Credit Model (Weak documentation)": MDD_WEAK,
}
