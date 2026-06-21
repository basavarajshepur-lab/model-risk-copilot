"""
Compliance Checker Agent — maps model metadata to SR 11-7 / SS1/23 requirements.

For each regulatory requirement, assesses: MET / PARTIAL / GAP / NOT_APPLICABLE.
Provides specific evidence found, gap description, and remediation suggestion.

Design decision: structured output via tool use for every requirement check.
This makes the compliance report auditable — every finding is traceable to a
specific regulatory requirement. Regulators and MRM analysts can follow the logic.
"""

import json
from anthropic import Anthropic
from core.models import (
    ExtractedModelMetadata, ComplianceReport, RequirementCheck,
    ComplianceStatus, ModelRiskRating, RegulatoryFramework
)
from core.sr117_framework import SR117_REQUIREMENTS, RequirementSpec

client = Anthropic()

SYSTEM_PROMPT = """You are a model risk management specialist with deep expertise in
SR 11-7 (US) and SS1/23 (UK) compliance. You conduct model validation for a tier-1 bank.

For each requirement you are given, assess whether the model documentation meets it:
- MET: Clear evidence in the documentation that this requirement is satisfied
- PARTIAL: Some evidence present but incomplete or insufficiently detailed
- GAP: Requirement not addressed or significant evidence missing
- NOT_APPLICABLE: Requirement does not apply to this model type (explain why)

Be specific. Reference actual content from the model documentation when citing evidence.
When identifying gaps, provide actionable remediation suggestions."""


def _check_single_requirement(
    metadata: ExtractedModelMetadata,
    req: RequirementSpec,
    document_text: str,
) -> RequirementCheck:
    """Run compliance check for a single requirement."""

    tool = {
        "name": "record_requirement_check",
        "description": "Record compliance check result for a single SR 11-7 requirement",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["MET", "PARTIAL", "GAP", "NOT_APPLICABLE"]
                },
                "evidence_found": {
                    "type": "string",
                    "description": "Specific text or section in the MDD that satisfies this requirement. Null if GAP."
                },
                "gap_description": {
                    "type": "string",
                    "description": "What is missing or insufficient. Null if MET."
                },
                "remediation_suggestion": {
                    "type": "string",
                    "description": "Specific action to address the gap. Null if MET."
                }
            },
            "required": ["status"]
        }
    }

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        temperature=0.1,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "any"},
        messages=[{
            "role": "user",
            "content": f"""Check this SR 11-7 requirement against the model documentation:

REQUIREMENT [{req.id}]: {req.requirement_text}
Criticality: {req.criticality}
Evidence required: {req.evidence_required}
Common gaps to watch for: {'; '.join(req.common_gaps)}

MODEL METADATA EXTRACTED:
- Name: {metadata.model_name}
- Type: {metadata.model_type.value}
- Methodology: {metadata.methodology}
- Data: {metadata.training_data_description}
- Assumptions: {json.dumps(metadata.key_assumptions)}
- Limitations: {json.dumps(metadata.known_limitations)}
- Performance metrics: {json.dumps(metadata.performance_metrics)}
- Monitoring plan present: {metadata.monitoring_plan_present}
- Documentation notes: {metadata.extraction_notes}

DOCUMENT EXCERPT (first 2000 chars):
{document_text[:2000]}

Assess whether this requirement is MET, PARTIAL, GAP, or NOT_APPLICABLE."""
        }],
    )

    for block in response.content:
        if block.type == "tool_use":
            data = block.input
            return RequirementCheck(
                requirement_id=req.id,
                section=req.section,
                requirement_text=req.requirement_text,
                criticality=req.criticality,
                status=ComplianceStatus(data["status"]),
                evidence_found=data.get("evidence_found"),
                gap_description=data.get("gap_description"),
                remediation_suggestion=data.get("remediation_suggestion"),
            )

    return RequirementCheck(
        requirement_id=req.id,
        section=req.section,
        requirement_text=req.requirement_text,
        criticality=req.criticality,
        status=ComplianceStatus.GAP,
        gap_description="Compliance check could not be completed",
        remediation_suggestion="Manual review required",
    )


def _calculate_risk_rating(checks: list[RequirementCheck], score: int) -> ModelRiskRating:
    """Derive model risk rating from gap analysis."""
    critical_high_gaps = sum(
        1 for c in checks
        if c.status == ComplianceStatus.GAP and c.criticality == "HIGH"
    )
    if critical_high_gaps >= 3 or score < 40:
        return ModelRiskRating.CRITICAL
    elif critical_high_gaps >= 1 or score < 60:
        return ModelRiskRating.HIGH
    elif score < 80:
        return ModelRiskRating.MEDIUM
    return ModelRiskRating.LOW


def run(
    metadata: ExtractedModelMetadata,
    document_text: str,
    framework: RegulatoryFramework = RegulatoryFramework.SR117,
) -> ComplianceReport:
    """Run full compliance check against all requirements."""
    checks = []
    for req in SR117_REQUIREMENTS:
        check = _check_single_requirement(metadata, req, document_text)
        checks.append(check)

    met = sum(1 for c in checks if c.status == ComplianceStatus.MET)
    gaps = [c for c in checks if c.status == ComplianceStatus.GAP]
    total = len(checks)
    score = round((met / total) * 100) if total else 0

    risk_rating = _calculate_risk_rating(checks, score)

    critical_gaps = [
        f"[{c.requirement_id}] {c.gap_description}"
        for c in gaps if c.criticality == "HIGH"
    ]
    high_gaps = [
        f"[{c.requirement_id}] {c.gap_description}"
        for c in gaps if c.criticality == "MEDIUM"
    ]

    return ComplianceReport(
        framework=framework,
        overall_compliance_score=score,
        model_risk_rating=risk_rating,
        requirement_checks=checks,
        critical_gaps=critical_gaps,
        high_gaps=high_gaps,
        total_requirements=total,
        requirements_met=met,
        requirements_with_gaps=len(gaps),
    )
