# Model Risk Copilot

**Multi-agent AI model risk management platform** — reads a Model Development Document and produces SR 11-7 compliance gap analysis, validation questions, risk rating, and a report draft. In under 2 minutes.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Production--Ready%20Demo-brightgreen) ![Claude](https://img.shields.io/badge/Powered%20by-Claude%20AI-orange)

---

## The Problem

Every AI or statistical model at a regulated bank requires independent validation under **SR 11-7** (US Fed/OCC) or **SS1/23** (UK PRA). Credit scoring. Fraud detection. AML monitoring. Market risk. Pricing. All of them.

The validation process is slow and mechanical:
1. MRM analyst reads the Model Development Document
2. Checks it against a mental checklist of SR 11-7 requirements
3. Writes validation questions to send to the dev team
4. Back-and-forth over weeks
5. Writes a formal validation report

At a tier-1 bank with hundreds of models in inventory, MRM teams are chronically backlogged. Model approvals take 3–6 months. In a world where AI models are multiplying, the MRM function can't keep up.

**The painful part isn't the judgment.** It's the 70% of time spent on mechanical compliance checking that any SR 11-7 expert already knows by heart.

---

## What Model Risk Copilot Does

A four-agent pipeline that takes a Model Development Document and produces:

```
                    ┌─────────────────────────────────────────────────────────┐
                    │              MODEL RISK COPILOT — PIPELINE              │
                    └─────────────────────────────────────────────────────────┘

     Model                   Agent 1                    Agent 2
  Development             Document Analyser          Compliance Checker
   Document
                         ┌─────────────────┐         ┌──────────────────────┐
  ┌──────────┐           │ Extracts:        │         │ Checks 18 SR 11-7    │
  │ Purpose  │  ──────►  │ • Model type     │  ──►    │ requirements:        │
  │ Methodo- │           │ • Methodology    │         │ MET / PARTIAL /      │
  │  logy    │           │ • Data           │         │ GAP / N/A            │
  │ Data     │           │ • Assumptions    │         │                      │
  │ Perform- │           │ • Limitations    │         │ Each check:          │
  │  ance    │           │ • Monitoring     │         │ • Evidence found     │
  │ Govern.  │           └─────────────────┘         │ • Gap description    │
  └──────────┘                                        │ • Remediation        │
                                                       └──────────────────────┘
                                                                │
                               ┌────────────────────────────────┤
                               │                                │
                           Agent 3                          Agent 4
                      Question Generator                 Report Drafter
                      ┌──────────────────┐          ┌────────────────────┐
                      │ 15-20 targeted   │          │ Validation report  │
                      │ questions from   │          │ draft:             │
                      │ gap analysis:    │          │ • Executive summary│
                      │ • Category       │          │ • Model overview   │
                      │ • SR 11-7 ref    │          │ • Scope            │
                      │ • Evidence ask   │          │ • Conditions for   │
                      │                  │          │   approval         │
                      └──────────────────┘          │ • Monitoring reqs  │
                                                     └────────────────────┘
                                                              │
                                                              ▼
                                                      Risk Rating
                                                  LOW / MEDIUM / HIGH / CRITICAL
                                                  Compliance Score 0-100
```

---

## Features

- **Document Analyser** — extracts structured model metadata from any MDD using Claude tool use: model type, methodology, data description, assumptions, limitations, performance metrics, monitoring plan
- **Compliance Checker** — evaluates each of 18 SR 11-7 requirements individually with structured output: MET/PARTIAL/GAP/NOT_APPLICABLE, evidence found, gap description, remediation suggestion
- **Question Generator** — produces 15–20 targeted validation questions categorised by type (data quality, methodology, performance, governance, monitoring) with SR 11-7 references and expected evidence
- **Report Drafter** — writes initial validation report: executive summary, model overview, findings, conditions for approval, monitoring requirements
- **Risk Rating** — derives LOW/MEDIUM/HIGH/CRITICAL rating from gap analysis using calibrated logic
- **Three sample MDDs** — strong, partial, and weak documentation quality — covering credit scoring, fraud detection, and SME lending
- **Streamlit UI** — four-tab interface: assess, samples, validation questions, report
- **CLI runner** — process MDDs from the command line; save results as JSON

---

## Quick Start

```bash
git clone https://github.com/basavarajshepur-lab/model-risk-copilot
cd model-risk-copilot
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
streamlit run app.py
```

**CLI — use a built-in sample MDD:**
```bash
python run_assessment.py --sample strong
python run_assessment.py --sample partial
python run_assessment.py --sample weak
```

**CLI — assess your own MDD:**
```bash
python run_assessment.py --file path/to/your_mdd.txt --output-dir ./reports
```

---

## Sample Output

```
MODEL RISK COPILOT — Regulatory Assessment Pipeline
Framework: SR117  |  2025-06-20 14:32

[1/4] Analysing document and extracting model metadata...
      Model: FraudScorer_ML (fraud_detection)
      Documentation completeness: 42/100

[2/4] Checking compliance against SR117 requirements...
      Compliance score: 39/100
      Risk rating: HIGH
      Requirements met: 7/18
      Gaps identified: 11

[3/4] Generating validation questions from gap analysis...
      Generated 18 validation questions

[4/4] Drafting validation report...
      Report drafted: 5 conditions for approval
                      4 monitoring requirements

==============================================================
ASSESSMENT COMPLETE
Risk rating: HIGH  |  Score: 39/100
Critical gaps: 8
  [SR117-2.1] No methodology justification — alternative approaches...
  [SR117-2.3] Assumptions not documented or tested...
  [SR117-2.2] No formal data quality assessment; training...
==============================================================
```

---

## SR 11-7 Requirements Encoded

The compliance checker evaluates 18 requirements across 6 sections:

| Section | Requirements |
|---|---|
| Model Definition and Scope | Purpose and scope; Model inventory registration |
| Model Development | Methodology justification; Data description; Assumptions; Limitations; Performance |
| Model Validation | Conceptual soundness; Data quality validation; Outcomes analysis |
| Ongoing Monitoring | Monitoring plan; PSI / drift tracking; Recalibration criteria |
| Model Governance | Ownership; Approval process; Change management |
| Documentation | Third-party replicability; User communication of limitations |

Each requirement encodes: criticality (HIGH/MEDIUM), evidence required, and common gaps observed in practice.

---

## The Design Decisions That Matter

**Why check each requirement individually?**  
A single "pass/fail" on SR 11-7 overall is useless. MRM analysts need to know *which* requirements are not met and *exactly* what evidence is missing. Individual requirement checks make findings auditable and actionable.

**Why structured output via tool use?**  
Free-text gap analysis is unreliable — different runs produce differently structured outputs. Using `tool_choice={"type": "any"}` forces a Pydantic-compatible structured response for every requirement check. The same input produces consistently structured output.

**Why four agents instead of one?**  
Each agent has a different cognitive task: extraction (what is here), compliance (does it meet standards), question generation (what to ask), and report writing (how to communicate findings). Mixing these in one prompt produces lower quality across all four. Separation also makes each stage independently testable and replaceable.

**Why 0.1 temperature for compliance checking?**  
SR 11-7 compliance determinations should be consistent. The same MDD run twice should produce the same gap findings. Lower temperature reduces variance without sacrificing quality on this structured task.

---

## Project Structure

```
model-risk-copilot/
├── app.py                          # Streamlit UI (4 tabs)
├── run_assessment.py               # CLI runner
├── agents/
│   ├── document_analyser.py        # MDD metadata extraction via tool use
│   ├── compliance_checker.py       # SR 11-7 requirement-by-requirement check
│   ├── question_generator.py       # Validation question generation
│   └── report_drafter.py          # Validation report drafting
├── core/
│   ├── models.py                   # Pydantic models (all pipeline types)
│   ├── sr117_framework.py          # Encoded SR 11-7 requirements
│   └── pipeline.py                 # Four-agent orchestration
├── data/
│   └── sample_mdds.py             # 3 sample Model Development Documents
└── docs/
    └── PRD.md                      # Product Requirements Document
```

---

## Three Scenarios

| MDD | Model | Expected Score | Expected Rating |
|---|---|---|---|
| Strong | RetailPD_v3.2 — Retail mortgage PD | 85–90/100 | LOW |
| Partial | FraudScorer_ML — Payment fraud detection | 35–45/100 | HIGH |
| Weak | SME Credit — Small business lending | 5–15/100 | CRITICAL |

The strong MDD is representative of a well-governed tier-1 bank model. The partial MDD is the most realistic — what you typically receive in practice. The weak MDD represents what happens when data science teams prioritise velocity over governance.

---

## Production Considerations

This is a production-ready **demo**. For deployment at a regulated institution:

1. Add SS1/23 requirements alongside SR 11-7 (framework extension point already in code)
2. Integrate with model inventory database (feed `ModelInventoryEntry` objects)
3. Add user authentication and role-based access (MRM analyst vs. model developer views)
4. Log all AI assessments for model risk team's own model risk obligation (meta-MRM)
5. Periodic calibration: compare AI gap findings to experienced MRM analyst findings; track false negative rate
6. Legal review of AI use in regulatory compliance workflow

---

## Background

Built by [Basavaraj Shepur](https://linkedin.com/in/basavarajshepur) — Senior AI Product Manager with 19 years in financial services. Former Senior Product Owner at Deutsche Bank CDO, where the AI/data platform team was responsible for responsible AI governance frameworks across 450+ AI models including validation pipeline tooling, confidence monitoring, and MRM reporting. This system implements the governance patterns from that work: structured compliance checking, evidence-based findings, human review before any regulatory submission.

---

## License

MIT
