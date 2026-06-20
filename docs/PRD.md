# Product Requirements Document
## Model Risk Copilot — AI Model Risk Management Platform

**Version:** 1.0  
**Author:** Basavaraj Shepur  
**Status:** Production-Ready Demo

---

## Problem Statement

Every AI or statistical model used in a regulated financial institution — credit scoring,
fraud detection, AML, market risk, pricing — requires formal model risk management under
SR 11-7 (US) or SS1/23 (UK). The MRM process exists to prevent models from being used
in ways that produce inaccurate outputs with material financial or regulatory consequences.

The problem: MRM validation is expensive, slow, and labour-intensive.

The typical validation workflow:
1. Model development team produces a Model Development Document (MDD)
2. Independent MRM team reads the MDD and prepares a list of validation questions
3. Back-and-forth with development team over weeks/months
4. MRM writes a formal validation report
5. Model Risk Committee reviews and approves

At a tier-1 bank with hundreds of models in inventory, MRM teams are chronically
backlogged. Model approvals take 3–6 months. In a world where AI models are being
developed at accelerating pace (LLMs, GenAI), the MRM function is a bottleneck
at precisely the moment it is most needed.

This is not a marginal problem. Regulatory fines for inadequate model governance:
- Deutsche Bank: $157M (2017, Fed model risk concerns)
- Goldman Sachs: $79.5M (2018, CCAR stress testing model issues)
- HSBC: ongoing PRA pressure on AI model governance (2024)

---

## Target Users

**1. MRM Analyst (primary)**
- Reads MDDs, identifies gaps, writes validation questions, drafts reports
- Pain: 70–80% of time on mechanical compliance checking against known requirements
- Needs: pre-populated gap analysis, starting point for validation questions, report draft

**2. Model Risk Head / CRO**
- Oversees model inventory, prioritises validation backlog, governs MRC submissions
- Pain: no visibility into portfolio-wide compliance posture, slow throughput
- Needs: dashboard view, risk rating by model, backlog prioritisation

**3. Model Developer (secondary)**
- Receives validation questions, responds with evidence
- Pain: generic questions that waste time; unclear what "good" documentation looks like
- Needs: clear, specific questions tied to regulatory requirements

**4. Audit / Regulator**
- Reviews MRM quality during exam or internal audit
- Needs: complete audit trail, documented rationale for every finding

---

## User Stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | MRM Analyst | Upload an MDD and get a structured compliance gap analysis | I can focus on judgment rather than mechanical checklist review |
| US-02 | MRM Analyst | Get a list of targeted validation questions derived from the gaps | I can send a first-round questionnaire to the dev team in hours not days |
| US-03 | MRM Analyst | Get an initial validation report draft | I spend time reviewing and refining, not writing from scratch |
| US-04 | Risk Head | See model risk rating and compliance score at a glance | I can prioritise the validation backlog |
| US-05 | Model Developer | Understand exactly which SR 11-7 sections my MDD doesn't meet | I can address gaps before formal validation |

---

## Functional Requirements

### FR-01: Four-Agent Pipeline
- System must run four sequential agents: Document Analyser → Compliance Checker → Question Generator → Report Drafter
- Document Analyser must extract structured model metadata via tool use (not free text)
- Compliance Checker must assess each SR 11-7 requirement individually (MET/PARTIAL/GAP/NOT_APPLICABLE)
- Question Generator must produce targeted, evidence-focused questions referencing specific gaps
- Report Drafter must produce structured validation report with conditions for approval

### FR-02: Structured SR 11-7 Framework
- System must encode all material SR 11-7 requirements as structured objects
- Each requirement must have: id, section, criticality, evidence required, common gaps
- Compliance checks must be traceable requirement-by-requirement

### FR-03: Risk Rating
- System must derive model risk rating (LOW/MEDIUM/HIGH/CRITICAL) from gap analysis
- Rating logic: HIGH rating if any HIGH-criticality gap; CRITICAL if 3+ HIGH gaps or score <40

### FR-04: Output Formats
- Results must be exportable as JSON (full pipeline output)
- Validation questions must be exportable as JSON
- Validation report draft must be downloadable as text file

### FR-05: Sample MDDs
- System must include at least 3 sample MDDs covering strong/partial/weak documentation quality
- Sample MDDs must be realistic enough for demonstration to MRM professionals

---

## Success Metrics

| Metric | Baseline | Target |
|---|---|---|
| Time to first validation question set | 3–5 days | < 2 hours |
| MDD gap analysis completeness | Manual, inconsistent | 18 SR 11-7 requirements, systematically |
| Initial report draft time | 2–3 days | < 5 minutes |
| Gap false negative rate | N/A | <10% (analyst to verify) |

---

## Out of Scope (v1.0)

- Model inventory database integration
- SS1/23 full implementation (framework extension point in code, SR 11-7 only in v1.0)
- Regulatory exam workbench
- Multi-user access / role-based permissions
- Integration with model development toolchains (MLflow, Vertex AI, SageMaker)
- Real-time model performance monitoring feeds
