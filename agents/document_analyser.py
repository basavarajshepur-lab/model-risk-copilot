"""
Document Analyser Agent — extracts structured model metadata from an MDD.

Takes raw model documentation text and extracts the key elements an MRM
validator needs: purpose, methodology, data, performance, assumptions,
limitations, and monitoring plan.

Design decision: extraction precedes compliance checking. This gives the
compliance checker a clean, structured input rather than raw text — reduces
hallucination risk and makes the compliance check more precise.
"""

from anthropic import Anthropic
from ..core.models import ExtractedModelMetadata, ModelType

client = Anthropic()

SYSTEM_PROMPT = """You are an expert model risk analyst at a tier-1 investment bank.
Your task is to read a Model Development Document (MDD) and extract structured
information that will be used for SR 11-7 / SS1/23 compliance checking.

Be precise and evidence-based. Extract what is actually present in the document.
Do not infer or assume — if something is not explicitly stated, note that it is absent.
Your extraction quality directly determines the accuracy of the compliance check."""


def _build_extraction_tool() -> dict:
    return {
        "name": "extract_model_metadata",
        "description": "Extract structured model metadata from the MDD",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string"},
                "model_type": {
                    "type": "string",
                    "enum": ["credit_scoring", "fraud_detection", "aml_monitoring",
                             "market_risk", "pricing", "customer_churn", "stress_testing", "other"]
                },
                "intended_use": {"type": "string", "description": "What the model is used for and who uses it"},
                "methodology": {"type": "string", "description": "Algorithm/approach used (e.g. logistic regression, gradient boosting, neural network)"},
                "training_data_description": {"type": "string", "description": "Data sources, time period, volume, quality notes"},
                "performance_metrics": {
                    "type": "object",
                    "description": "Key performance metrics and their values (e.g. {'Gini': '0.67', 'KS': '0.42', 'AUC': '0.84'})",
                    "additionalProperties": {"type": "string"}
                },
                "key_assumptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Explicit assumptions stated in the document"
                },
                "known_limitations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Documented limitations and failure modes"
                },
                "monitoring_plan_present": {
                    "type": "boolean",
                    "description": "Is a formal monitoring plan documented?"
                },
                "documentation_completeness_score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Your assessment of documentation completeness for SR 11-7 purposes"
                },
                "extraction_notes": {
                    "type": "string",
                    "description": "Any important observations about what is missing or unclear"
                }
            },
            "required": ["model_name", "model_type", "intended_use", "methodology",
                        "training_data_description", "performance_metrics", "key_assumptions",
                        "known_limitations", "monitoring_plan_present", "documentation_completeness_score"]
        }
    }


def run(document_text: str) -> ExtractedModelMetadata:
    """Extract structured metadata from model documentation."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[_build_extraction_tool()],
        tool_choice={"type": "any"},
        messages=[{
            "role": "user",
            "content": f"Extract structured metadata from this Model Development Document:\n\n{document_text}"
        }],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_model_metadata":
            data = block.input
            return ExtractedModelMetadata(
                model_name=data["model_name"],
                model_type=ModelType(data["model_type"]),
                intended_use=data["intended_use"],
                methodology=data["methodology"],
                training_data_description=data["training_data_description"],
                performance_metrics=data.get("performance_metrics", {}),
                key_assumptions=data.get("key_assumptions", []),
                known_limitations=data.get("known_limitations", []),
                monitoring_plan_present=data["monitoring_plan_present"],
                documentation_completeness_score=data["documentation_completeness_score"],
                extraction_notes=data.get("extraction_notes", ""),
            )

    raise ValueError("Document analyser did not return structured output")
