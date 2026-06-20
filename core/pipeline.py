"""
Model Risk Copilot — four-agent pipeline orchestration.

Pipeline stages:
  1. document_analyser  — extract structured metadata from MDD
  2. compliance_checker — map metadata to SR 11-7 requirements
  3. question_generator — generate validation questions from gap analysis
  4. report_drafter     — draft validation report for MRM analyst review

Each stage has a well-defined input/output contract via Pydantic models,
making the pipeline testable, replaceable, and auditable at each stage.
"""

import json
from pathlib import Path
from datetime import datetime
from ..agents import document_analyser, compliance_checker, question_generator, report_drafter
from ..core.models import (
    RegulatoryFramework, ExtractedModelMetadata,
    ComplianceReport, ValidationReport
)


def process_mdd(
    document_text: str,
    framework: RegulatoryFramework = RegulatoryFramework.SR117,
    output_dir: Path | None = None,
) -> dict:
    """Run the full model risk assessment pipeline on a Model Development Document."""
    print(f"\n{'='*60}")
    print(f"MODEL RISK COPILOT — Regulatory Assessment Pipeline")
    print(f"Framework: {framework.value}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    print("[1/4] Analysing document and extracting model metadata...")
    metadata: ExtractedModelMetadata = document_analyser.run(document_text)
    print(f"      Model: {metadata.model_name} ({metadata.model_type.value})")
    print(f"      Documentation completeness: {metadata.documentation_completeness_score}/100")

    print(f"\n[2/4] Checking compliance against {framework.value} requirements...")
    compliance: ComplianceReport = compliance_checker.run(metadata, document_text, framework)
    print(f"      Compliance score: {compliance.overall_compliance_score}/100")
    print(f"      Risk rating: {compliance.model_risk_rating.value}")
    print(f"      Requirements met: {compliance.requirements_met}/{compliance.total_requirements}")
    print(f"      Gaps identified: {compliance.requirements_with_gaps}")

    print("\n[3/4] Generating validation questions from gap analysis...")
    questions = question_generator.run(metadata, compliance)
    print(f"      Generated {len(questions)} validation questions")

    print("\n[4/4] Drafting validation report...")
    report: ValidationReport = report_drafter.run(metadata, compliance, framework)
    print(f"      Report drafted: {len(report.conditions_for_approval)} conditions for approval")
    print(f"                      {len(report.recommended_monitoring)} monitoring requirements")

    result = {
        "metadata": metadata.model_dump(),
        "compliance": {
            "framework": compliance.framework.value,
            "overall_compliance_score": compliance.overall_compliance_score,
            "model_risk_rating": compliance.model_risk_rating.value,
            "requirements_met": compliance.requirements_met,
            "total_requirements": compliance.total_requirements,
            "requirements_with_gaps": compliance.requirements_with_gaps,
            "critical_gaps": compliance.critical_gaps,
            "high_gaps": compliance.high_gaps,
            "requirement_checks": [c.model_dump() for c in compliance.requirement_checks],
        },
        "validation_questions": [q.model_dump() for q in questions],
        "report": {
            "executive_summary": report.executive_summary,
            "model_overview": report.model_overview,
            "validation_scope": report.validation_scope,
            "overall_risk_rating": report.overall_risk_rating.value,
            "conditions_for_approval": report.conditions_for_approval,
            "recommended_monitoring": report.recommended_monitoring,
            "findings": report.findings,
        },
    }

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = output_dir / f"{metadata.model_name.replace(' ', '_')}_{ts}.json"
        out_file.write_text(json.dumps(result, indent=2, default=str))
        print(f"\n[saved] {out_file}")

    print(f"\n{'='*60}")
    print(f"ASSESSMENT COMPLETE")
    print(f"Risk rating: {compliance.model_risk_rating.value}  |  Score: {compliance.overall_compliance_score}/100")
    if compliance.critical_gaps:
        print(f"Critical gaps: {len(compliance.critical_gaps)}")
        for gap in compliance.critical_gaps[:3]:
            print(f"  {gap[:80]}...")
    print(f"{'='*60}\n")

    return result
