"""
Model Risk Copilot — Streamlit Interface

Four-tab UI:
  1. Assess Model — paste MDD, run full assessment
  2. Sample MDDs  — use pre-built examples to explore output
  3. Validation Questions — browse generated questions
  4. Reports     — view and download validation report
"""

from dotenv import load_dotenv
load_dotenv()

import json
import os
import streamlit as st
from pathlib import Path
from core.models import RegulatoryFramework
from core.pipeline import process_mdd
from data.sample_mdds import SAMPLE_MDDS

st.set_page_config(
    page_title="Model Risk Copilot",
    page_icon="🏦",
    layout="wide",
)

st.title("Model Risk Copilot")
st.markdown(
    "**Multi-agent SR 11-7 / SS1/23 compliance assessment** | "
    "Document analysis → Compliance check → Validation questions → Report draft"
)

# --- Trial mode ---
TRIAL_MODE = os.environ.get("TRIAL_MODE", "false").lower() == "true"
TRIAL_RUN_CAP = 3
GITHUB_URL = "https://github.com/basavarajshepur-lab/model-risk-copilot"

if "trial_runs_used" not in st.session_state:
    st.session_state["trial_runs_used"] = 0
trial_limit_reached = TRIAL_MODE and st.session_state["trial_runs_used"] >= TRIAL_RUN_CAP

if TRIAL_MODE:
    st.info(
        f"🔒 **Live Trial** — sample MDDs only, {TRIAL_RUN_CAP} runs per browser session. "
        f"[Clone the repo]({GITHUB_URL}) to assess your own documents.",
        icon="🔒",
    )

st.divider()

if "result" not in st.session_state:
    st.session_state.result = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    framework = st.selectbox(
        "Regulatory Framework",
        options=["SR117 (US Fed/OCC)", "SS123 (UK PRA)"],
        index=0,
    )
    fw_enum = RegulatoryFramework.SR117 if "SR117" in framework else RegulatoryFramework.SS123

    st.divider()
    st.markdown("**How it works**")
    st.markdown("""
1. **Document Analyser** extracts structured model metadata
2. **Compliance Checker** maps metadata to 18 SR 11-7 requirements
3. **Question Generator** drafts validation questions from gaps
4. **Report Drafter** writes initial validation report

All agents use Claude claude-haiku-4-5-20251001 with structured output via tool use.
    """)

    st.divider()
    if st.session_state.result:
        score = st.session_state.result["compliance"]["overall_compliance_score"]
        rating = st.session_state.result["compliance"]["model_risk_rating"]
        colour = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴", "CRITICAL": "🔴"}.get(rating, "⚪")
        st.metric("Compliance Score", f"{score}/100")
        st.metric("Risk Rating", f"{colour} {rating}")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Assess Model", "Sample MDDs", "Validation Questions", "Report"])

# ── Tab 1: Assess Model ───────────────────────────────────────────────────────
with tab1:
    st.header("Assess a Model Development Document")

    if TRIAL_MODE:
        st.info(
            f"Pasting your own MDD is disabled in trial mode. Use the **Sample MDDs** tab, "
            f"or [clone the repo]({GITHUB_URL}) to assess your own documents."
        )
    else:
        doc_text = st.text_area(
            "Paste your Model Development Document (MDD) here",
            height=400,
            placeholder="Paste the full text of your Model Development Document...",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            run_btn = st.button("Run Assessment", type="primary", use_container_width=True)

        if run_btn:
            if not doc_text.strip():
                st.error("Please paste a Model Development Document first.")
            else:
                with st.spinner("Running 4-agent pipeline... (takes ~60–90 seconds)"):
                    try:
                        result = process_mdd(doc_text, fw_enum)
                        st.session_state.result = result
                        st.success("Assessment complete.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pipeline error: {e}")
                        st.info("Check that your ANTHROPIC_API_KEY is set in .env")

    if st.session_state.result:
        r = st.session_state.result
        meta = r["metadata"]
        comp = r["compliance"]

        st.subheader("Results Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Compliance Score", f"{comp['overall_compliance_score']}/100")
        m2.metric("Risk Rating", comp["model_risk_rating"])
        m3.metric("Requirements Met", f"{comp['requirements_met']}/{comp['total_requirements']}")
        m4.metric("Gaps", comp["requirements_with_gaps"])

        with st.expander("Model Metadata Extracted", expanded=False):
            st.json(meta)

        with st.expander("Requirement-by-Requirement Breakdown", expanded=True):
            for check in comp["requirement_checks"]:
                status_icon = {"MET": "✅", "PARTIAL": "⚠️", "GAP": "❌", "NOT_APPLICABLE": "➖"}.get(
                    check["status"], "❓"
                )
                with st.expander(
                    f"{status_icon} [{check['requirement_id']}] {check['section']} — {check['criticality']}",
                    expanded=(check["status"] == "GAP" and check["criticality"] == "HIGH"),
                ):
                    st.markdown(f"**Requirement:** {check['requirement_text']}")
                    st.markdown(f"**Status:** {check['status']}")
                    if check.get("evidence_found"):
                        st.markdown(f"**Evidence found:** {check['evidence_found']}")
                    if check.get("gap_description"):
                        st.markdown(f"**Gap:** {check['gap_description']}")
                    if check.get("remediation_suggestion"):
                        st.markdown(f"**Remediation:** {check['remediation_suggestion']}")

        if comp.get("critical_gaps"):
            with st.expander("Critical Gaps (HIGH severity)", expanded=True):
                for gap in comp["critical_gaps"]:
                    st.error(gap)

# ── Tab 2: Sample MDDs ────────────────────────────────────────────────────────
with tab2:
    st.header("Try Sample Model Documents")
    st.markdown(
        "Three pre-built MDDs covering the quality range seen in practice. "
        "Select one to auto-populate the assessment tab, or run directly."
    )

    if trial_limit_reached:
        st.warning(
            f"Trial limit reached ({TRIAL_RUN_CAP} runs used this session). "
            f"[Clone the repo]({GITHUB_URL}) to keep exploring with your own documents."
        )

    for name, text in SAMPLE_MDDS.items():
        with st.expander(name):
            st.text_area("Document preview", text[:500] + "...", height=150, disabled=True, key=f"prev_{name}")
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(
                    "Run Assessment" + (" (trial limit reached)" if trial_limit_reached else ""),
                    key=f"run_{name}",
                    disabled=trial_limit_reached,
                ):
                    if TRIAL_MODE:
                        st.session_state["trial_runs_used"] += 1
                    with st.spinner("Running 4-agent pipeline..."):
                        try:
                            result = process_mdd(text, fw_enum)
                            st.session_state.result = result
                            st.success(
                                f"Complete — Score: {result['compliance']['overall_compliance_score']}/100 | "
                                f"Rating: {result['compliance']['model_risk_rating']}"
                            )
                        except Exception as e:
                            st.error(f"Error: {e}")

# ── Tab 3: Validation Questions ───────────────────────────────────────────────
with tab3:
    st.header("Validation Questions")
    if not st.session_state.result:
        st.info("Run an assessment first to generate validation questions.")
    else:
        questions = st.session_state.result.get("validation_questions", [])
        if not questions:
            st.warning("No questions generated.")
        else:
            st.markdown(f"**{len(questions)} questions generated** for the model development team:")

            categories = sorted(set(q["category"] for q in questions))
            selected_cat = st.selectbox("Filter by category", ["All"] + categories)

            for q in questions:
                if selected_cat != "All" and q["category"] != selected_cat:
                    continue
                with st.expander(f"[{q['question_id']}] {q['question_text'][:80]}..."):
                    st.markdown(f"**Category:** {q['category']}")
                    st.markdown(f"**Full question:** {q['question_text']}")
                    st.markdown(f"**Rationale:** {q['rationale']}")
                    st.markdown(f"**SR 11-7 reference:** {q['regulatory_reference']}")
                    st.markdown(f"**Expected evidence:** {q['expected_evidence_type']}")

            st.download_button(
                "Download Questions (JSON)",
                data=json.dumps(questions, indent=2),
                file_name="validation_questions.json",
                mime="application/json",
            )

# ── Tab 4: Report ─────────────────────────────────────────────────────────────
with tab4:
    st.header("Validation Report Draft")
    if not st.session_state.result:
        st.info("Run an assessment first to generate a report.")
    else:
        report = st.session_state.result["report"]
        meta = st.session_state.result["metadata"]

        st.subheader(f"Model Validation Report — {meta['model_name']}")
        st.caption(f"Framework: {report.get('framework', 'SR117')} | Risk Rating: {report['overall_risk_rating']}")

        st.markdown("### Executive Summary")
        st.markdown(report["executive_summary"])

        st.markdown("### Model Overview")
        st.markdown(report["model_overview"])

        st.markdown("### Validation Scope")
        st.markdown(report["validation_scope"])

        if report["conditions_for_approval"]:
            st.markdown("### Conditions for Approval")
            for i, c in enumerate(report["conditions_for_approval"], 1):
                st.markdown(f"{i}. {c}")

        if report["recommended_monitoring"]:
            st.markdown("### Recommended Monitoring")
            for i, m in enumerate(report["recommended_monitoring"], 1):
                st.markdown(f"{i}. {m}")

        st.markdown("### Findings Summary")
        for f in report["findings"]:
            icon = "❌" if f["status"] == "GAP" else "⚠️"
            st.markdown(f"{icon} **[{f['requirement_id']}]** ({f['criticality']}) {f.get('gap', 'See detail')}")

        report_text = f"""MODEL VALIDATION REPORT
{meta['model_name']}
Framework: {report.get('framework', 'SR117')} | Risk Rating: {report['overall_risk_rating']}

EXECUTIVE SUMMARY
{report['executive_summary']}

MODEL OVERVIEW
{report['model_overview']}

VALIDATION SCOPE
{report['validation_scope']}

CONDITIONS FOR APPROVAL
{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(report['conditions_for_approval']))}

RECOMMENDED MONITORING
{chr(10).join(f'{i+1}. {m}' for i, m in enumerate(report['recommended_monitoring']))}
"""
        st.download_button(
            "Download Report (text)",
            data=report_text,
            file_name=f"validation_report_{meta['model_name'].replace(' ', '_')}.txt",
            mime="text/plain",
        )
