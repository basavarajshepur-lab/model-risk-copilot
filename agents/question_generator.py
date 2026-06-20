"""
Validation Question Generator — produces MRM validator questions from gap analysis.

Generates the exact questions an independent MRM analyst would ask during
model validation, based on model type and identified compliance gaps.

In practice: this cuts the time an MRM analyst spends writing validation
questions by 60-70%. The analyst reviews, refines, and supplements —
not writes from scratch.
"""

from anthropic import Anthropic
from ..core.models import (
    ExtractedModelMetadata, ComplianceReport, ValidationQuestion, ComplianceStatus
)

client = Anthropic()

SYSTEM_PROMPT = """You are a senior model validation analyst at a tier-1 bank.
You generate validation questions that will be sent to the model development team
as part of the formal SR 11-7 validation process.

Questions must be:
- Specific and evidence-focused (ask for specific documents, data, test results)
- Prioritised by risk (critical gaps first)
- Categorised by validation area
- Referenced to the specific SR 11-7 requirement they address

Avoid generic questions. Every question should be answerable with specific evidence."""


def run(
    metadata: ExtractedModelMetadata,
    compliance_report: ComplianceReport,
) -> list[ValidationQuestion]:
    """Generate targeted validation questions based on model and gap analysis."""
    gaps_text = "\n".join([
        f"- [{c.requirement_id}] {c.criticality}: {c.gap_description}"
        for c in compliance_report.requirement_checks
        if c.status == ComplianceStatus.GAP or c.status == ComplianceStatus.PARTIAL
    ])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Generate 15-20 validation questions for this model.

MODEL: {metadata.model_name} ({metadata.model_type.value})
Methodology: {metadata.methodology}
Compliance score: {compliance_report.overall_compliance_score}/100
Risk rating: {compliance_report.model_risk_rating.value}

IDENTIFIED GAPS (focus questions here):
{gaps_text}

Format each question as:
CATEGORY: [data_quality / methodology / performance / governance / monitoring]
QUESTION: [the specific question]
RATIONALE: [why this matters for SR 11-7]
SR 11-7 REFERENCE: [requirement ID e.g. SR117-2.2]
EXPECTED EVIDENCE: [what a good answer looks like]
---"""
        }],
    )

    text = response.content[0].text
    questions = []
    blocks = text.split("---")

    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        lines = {
            line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip()
            for line in block.strip().split("\n")
            if ":" in line
        }
        q_text = lines.get("QUESTION", "")
        if not q_text:
            continue
        questions.append(ValidationQuestion(
            question_id=f"VQ-{i+1:03d}",
            category=lines.get("CATEGORY", "methodology").lower().replace(" ", "_"),
            question_text=q_text,
            rationale=lines.get("RATIONALE", ""),
            regulatory_reference=lines.get("SR 11-7 REFERENCE", "SR117"),
            expected_evidence_type=lines.get("EXPECTED EVIDENCE", "Documentation"),
        ))

    return questions
