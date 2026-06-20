"""
SR 11-7 Requirements Framework

SR 11-7 (2011) is the US Federal Reserve / OCC guidance on model risk management.
It is the definitive standard for model governance at US banks and increasingly
adopted globally as best practice.

Structured as a list of RequirementSpec objects so the compliance checker agent
can reason against each requirement systematically and produce auditable output.
"""

from dataclasses import dataclass


@dataclass
class RequirementSpec:
    id: str
    section: str
    requirement_text: str
    criticality: str  # HIGH / MEDIUM / LOW
    evidence_required: str
    common_gaps: list[str]


SR117_REQUIREMENTS: list[RequirementSpec] = [
    # Section 1: Model Definition and Scope
    RequirementSpec(
        id="SR117-1.1",
        section="Model Definition and Scope",
        requirement_text="The model must have a clear, documented definition of its purpose, scope, and intended use cases.",
        criticality="HIGH",
        evidence_required="Model purpose statement, approved use cases, out-of-scope use cases",
        common_gaps=["Vague purpose statement", "No explicit out-of-scope definition", "Use cases not approved by business owner"]
    ),
    RequirementSpec(
        id="SR117-1.2",
        section="Model Definition and Scope",
        requirement_text="Models must be inventoried and tiered by complexity and risk impact.",
        criticality="HIGH",
        evidence_required="Model inventory entry, risk tier assignment with rationale",
        common_gaps=["Not registered in model inventory", "Risk tier not assigned or rationale missing"]
    ),

    # Section 2: Model Development
    RequirementSpec(
        id="SR117-2.1",
        section="Model Development",
        requirement_text="Model development must document the theoretical basis and conceptual soundness of the chosen methodology.",
        criticality="HIGH",
        evidence_required="Methodology justification, literature review or industry standard reference, alternative approaches considered",
        common_gaps=["No justification for methodology choice", "Alternative approaches not considered", "No literature or standard reference"]
    ),
    RequirementSpec(
        id="SR117-2.2",
        section="Model Development",
        requirement_text="Training data must be described including source, time period, quality assessment, and known limitations.",
        criticality="HIGH",
        evidence_required="Data dictionary, data quality report, time period covered, data lineage",
        common_gaps=["Data source not documented", "No data quality assessment", "Training/test split not specified", "Data vintage not stated"]
    ),
    RequirementSpec(
        id="SR117-2.3",
        section="Model Development",
        requirement_text="Model assumptions must be explicitly stated, justified, and tested where possible.",
        criticality="HIGH",
        evidence_required="Assumptions log, assumption testing results, sensitivity analysis",
        common_gaps=["Assumptions implicit rather than explicit", "No sensitivity analysis around key assumptions", "Assumptions not tested"]
    ),
    RequirementSpec(
        id="SR117-2.4",
        section="Model Development",
        requirement_text="Model limitations must be documented including conditions under which the model may not perform as expected.",
        criticality="HIGH",
        evidence_required="Limitations section in MDD, out-of-sample performance analysis, stress scenarios",
        common_gaps=["Limitations section absent or generic", "No stress/tail scenario analysis", "No documentation of failure modes"]
    ),
    RequirementSpec(
        id="SR117-2.5",
        section="Model Development",
        requirement_text="Model performance must be assessed using appropriate statistical metrics and benchmarks.",
        criticality="HIGH",
        evidence_required="Performance metrics table (Gini, KS, AUC, PSI, etc.), benchmark comparison, backtesting results",
        common_gaps=["Insufficient performance metrics", "No benchmark comparison", "Backtesting not performed", "Metrics not appropriate for model type"]
    ),

    # Section 3: Model Validation
    RequirementSpec(
        id="SR117-3.1",
        section="Model Validation — Conceptual Soundness",
        requirement_text="An independent validation must assess the conceptual soundness of the model's design, theory, and methodology.",
        criticality="HIGH",
        evidence_required="Independent validation report, validator credentials, validation scope statement",
        common_gaps=["Validation performed by model developer (not independent)", "Validation scope too narrow", "No conceptual soundness assessment"]
    ),
    RequirementSpec(
        id="SR117-3.2",
        section="Model Validation — Data Quality",
        requirement_text="Validation must assess data quality including completeness, accuracy, and representativeness for the model's use case.",
        criticality="HIGH",
        evidence_required="Data quality validation findings, representativeness assessment, data issues log",
        common_gaps=["No independent data quality review", "Representativeness not assessed", "Data issues not documented with materiality assessment"]
    ),
    RequirementSpec(
        id="SR117-3.3",
        section="Model Validation — Outcomes Analysis",
        requirement_text="Validation must include outcomes analysis comparing model predictions to actual outcomes where data is available.",
        criticality="HIGH",
        evidence_required="Back-testing results, prediction vs. actual comparison, time period of outcomes analysis",
        common_gaps=["No outcomes analysis performed", "Insufficient time period for outcomes analysis", "Outcomes analysis not independent"]
    ),

    # Section 4: Ongoing Monitoring
    RequirementSpec(
        id="SR117-4.1",
        section="Ongoing Monitoring",
        requirement_text="A monitoring plan must be in place covering model performance, stability, and data quality on a defined schedule.",
        criticality="HIGH",
        evidence_required="Monitoring plan document, KPIs/thresholds defined, monitoring frequency, owner assigned",
        common_gaps=["No formal monitoring plan", "Monitoring thresholds not defined", "No owner assigned for monitoring", "Monitoring frequency not specified"]
    ),
    RequirementSpec(
        id="SR117-4.2",
        section="Ongoing Monitoring",
        requirement_text="Population Stability Index (PSI) or equivalent must be tracked to detect input data drift.",
        criticality="MEDIUM",
        evidence_required="PSI monitoring results, PSI threshold for model review trigger",
        common_gaps=["PSI not tracked", "No threshold defined for PSI-triggered review", "PSI monitored but breaches not escalated"]
    ),
    RequirementSpec(
        id="SR117-4.3",
        section="Ongoing Monitoring",
        requirement_text="Criteria for model recalibration, redevelopment, or retirement must be defined.",
        criticality="MEDIUM",
        evidence_required="Redevelopment trigger criteria, escalation process for performance deterioration",
        common_gaps=["No defined triggers for recalibration", "Escalation process not documented", "Retirement criteria absent"]
    ),

    # Section 5: Model Governance
    RequirementSpec(
        id="SR117-5.1",
        section="Model Governance",
        requirement_text="Model ownership must be assigned with named business owner and technical owner accountable for the model.",
        criticality="HIGH",
        evidence_required="Named business owner, named technical owner, sign-off on MDD",
        common_gaps=["No named business owner", "Ownership at team level not individual", "Owners not signed off on MDD"]
    ),
    RequirementSpec(
        id="SR117-5.2",
        section="Model Governance",
        requirement_text="Model approval must go through a defined governance process before deployment.",
        criticality="HIGH",
        evidence_required="Approval committee minutes or sign-off record, conditions for approval (if any)",
        common_gaps=["No formal approval process", "Approval not documented", "Model deployed before validation complete"]
    ),
    RequirementSpec(
        id="SR117-5.3",
        section="Model Governance",
        requirement_text="Material model changes must trigger a re-validation process.",
        criticality="MEDIUM",
        evidence_required="Change management policy, materiality threshold definition, change log",
        common_gaps=["No change management policy", "Materiality threshold not defined", "Changes made without triggering re-validation"]
    ),

    # Section 6: Documentation
    RequirementSpec(
        id="SR117-6.1",
        section="Documentation",
        requirement_text="Model documentation must be sufficient for a knowledgeable third party to understand, replicate, and assess the model.",
        criticality="HIGH",
        evidence_required="Complete MDD, version control, change history",
        common_gaps=["Documentation insufficient for third-party replication", "No version control", "Code not documented or not available"]
    ),
    RequirementSpec(
        id="SR117-6.2",
        section="Documentation",
        requirement_text="All model limitations, assumptions, and known weaknesses must be documented and communicated to model users.",
        criticality="HIGH",
        evidence_required="User guide or model use policy, communication of limitations to business users",
        common_gaps=["Limitations not communicated to business users", "No user guide", "Known weaknesses downplayed or omitted"]
    ),
]


def get_requirements_by_section() -> dict[str, list[RequirementSpec]]:
    """Group requirements by section for structured review."""
    result: dict[str, list[RequirementSpec]] = {}
    for req in SR117_REQUIREMENTS:
        if req.section not in result:
            result[req.section] = []
        result[req.section].append(req)
    return result


def get_high_criticality_requirements() -> list[RequirementSpec]:
    return [r for r in SR117_REQUIREMENTS if r.criticality == "HIGH"]


def format_for_agent(framework: str = "SR117") -> str:
    """Format requirements as structured text for the compliance checker agent."""
    lines = [f"=== {framework} REQUIREMENTS ===\n"]
    for req in SR117_REQUIREMENTS:
        lines.append(f"[{req.id}] {req.section} — {req.criticality} CRITICALITY")
        lines.append(f"Requirement: {req.requirement_text}")
        lines.append(f"Evidence required: {req.evidence_required}")
        lines.append(f"Common gaps: {'; '.join(req.common_gaps)}")
        lines.append("")
    return "\n".join(lines)
