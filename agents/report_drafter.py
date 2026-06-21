"""
Model Validation Report Drafter — produces initial validation report draft.

Generates a structured model risk validation report in the format used by
tier-1 bank MRM teams. The draft is for MRM analyst review — it compresses
the initial report writing phase from days to minutes.
"""

from anthropic import Anthropic
from core.models import (
    ExtractedModelMetadata, ComplianceReport, ValidationReport,
    ModelRiskRating, RegulatoryFramework, ComplianceStatus
)

client = Anthropic()

SYSTEM_PROMPT = """You are a model risk management analyst writing a formal model
validation report for submission to the Model Risk Committee.

The report must be:
- Professional and precise — this is a regulatory document
- Evidence-based — reference specific findings from the compliance analysis
- Proportionate — findings severity should match compliance gaps found
- Actionable — conditions for approval and monitoring requirements must be specific

This draft will be reviewed by the Head of Model Risk before issuance."""


def run(
    metadata: ExtractedModelMetadata,
    compliance_report: ComplianceReport,
    framework: RegulatoryFramework = RegulatoryFramework.SR117,
) -> ValidationReport:
    """Draft model validation report for MRM analyst review."""
    gap_summary = "\n".join([
        f"- [{c.requirement_id}] ({c.criticality}) {c.gap_description} | Fix: {c.remediation_suggestion}"
        for c in compliance_report.requirement_checks
        if c.status in [ComplianceStatus.GAP, ComplianceStatus.PARTIAL]
    ])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Draft a model validation report with these sections:

MODEL: {metadata.model_name}
TYPE: {metadata.model_type.value}
FRAMEWORK: {framework.value}
OVERALL COMPLIANCE: {compliance_report.overall_compliance_score}/100
RISK RATING: {compliance_report.model_risk_rating.value}
DOCUMENTATION COMPLETENESS: {metadata.documentation_completeness_score}/100

METHODOLOGY: {metadata.methodology}
DATA: {metadata.training_data_description}
PERFORMANCE: {metadata.performance_metrics}
ASSUMPTIONS: {metadata.key_assumptions}
LIMITATIONS: {metadata.known_limitations}
MONITORING PLAN: {'Present' if metadata.monitoring_plan_present else 'ABSENT — critical gap'}

GAPS IDENTIFIED:
{gap_summary}

Write these sections (use the exact headers):

EXECUTIVE_SUMMARY:
[2-3 sentences: model purpose, overall rating, key conclusion]

MODEL_OVERVIEW:
[Methodology, intended use, data, scope]

VALIDATION_SCOPE:
[What was reviewed, what was not reviewed, limitations of this validation]

CONDITIONS_FOR_APPROVAL:
[Numbered list of conditions that must be met before model can be used in production. If risk rating is LOW, write "None — recommended for unconditional approval"]

RECOMMENDED_MONITORING:
[Numbered list of specific monitoring requirements post-approval]"""
        }],
    )

    text = response.content[0].text

    def extract(text: str, header: str) -> str:
        import re
        pattern = rf"{header}:\s*(.+?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def extract_list(text: str, header: str) -> list[str]:
        section = extract(text, header)
        lines = [l.strip().lstrip("0123456789.-) ") for l in section.split("\n") if l.strip()]
        return [l for l in lines if l]

    findings = [
        {
            "requirement_id": c.requirement_id,
            "section": c.section,
            "criticality": c.criticality,
            "status": c.status.value,
            "gap": c.gap_description,
            "remediation": c.remediation_suggestion,
        }
        for c in compliance_report.requirement_checks
        if c.status in [ComplianceStatus.GAP, ComplianceStatus.PARTIAL]
    ]

    return ValidationReport(
        model_name=metadata.model_name,
        framework=framework,
        executive_summary=extract(text, "EXECUTIVE_SUMMARY"),
        model_overview=extract(text, "MODEL_OVERVIEW"),
        validation_scope=extract(text, "VALIDATION_SCOPE"),
        findings=findings,
        overall_risk_rating=compliance_report.model_risk_rating,
        conditions_for_approval=extract_list(text, "CONDITIONS_FOR_APPROVAL"),
        recommended_monitoring=extract_list(text, "RECOMMENDED_MONITORING"),
    )
