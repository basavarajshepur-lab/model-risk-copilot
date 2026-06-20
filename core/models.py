"""Pydantic models for the Model Risk Copilot pipeline."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RegulatoryFramework(str, Enum):
    SR117 = "SR117"   # US Federal Reserve / OCC
    SS123 = "SS123"   # UK PRA


class ModelType(str, Enum):
    CREDIT_SCORING = "credit_scoring"
    FRAUD_DETECTION = "fraud_detection"
    AML_MONITORING = "aml_monitoring"
    MARKET_RISK = "market_risk"
    PRICING = "pricing"
    CUSTOMER_CHURN = "customer_churn"
    STRESS_TESTING = "stress_testing"
    OTHER = "other"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    OVERDUE = "overdue"
    CONDITIONALLY_APPROVED = "conditionally_approved"


class ModelRiskRating(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplianceStatus(str, Enum):
    MET = "MET"
    PARTIAL = "PARTIAL"
    GAP = "GAP"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RequirementCheck(BaseModel):
    requirement_id: str
    section: str
    requirement_text: str
    criticality: str  # HIGH / MEDIUM / LOW
    status: ComplianceStatus
    evidence_found: Optional[str] = None
    gap_description: Optional[str] = None
    remediation_suggestion: Optional[str] = None


class ExtractedModelMetadata(BaseModel):
    model_name: str
    model_type: ModelType
    intended_use: str
    methodology: str
    training_data_description: str
    performance_metrics: dict[str, str]
    key_assumptions: list[str]
    known_limitations: list[str]
    monitoring_plan_present: bool
    documentation_completeness_score: int = Field(ge=0, le=100)
    extraction_notes: str = ""


class ComplianceReport(BaseModel):
    framework: RegulatoryFramework
    overall_compliance_score: int = Field(ge=0, le=100)
    model_risk_rating: ModelRiskRating
    requirement_checks: list[RequirementCheck]
    critical_gaps: list[str]
    high_gaps: list[str]
    total_requirements: int
    requirements_met: int
    requirements_with_gaps: int


class ValidationQuestion(BaseModel):
    question_id: str
    category: str  # data_quality / methodology / performance / governance / monitoring
    question_text: str
    rationale: str
    regulatory_reference: str
    expected_evidence_type: str


class ValidationReport(BaseModel):
    model_name: str
    framework: RegulatoryFramework
    executive_summary: str
    model_overview: str
    validation_scope: str
    findings: list[dict]
    overall_risk_rating: ModelRiskRating
    conditions_for_approval: list[str]
    recommended_monitoring: list[str]


class ModelInventoryEntry(BaseModel):
    model_id: str
    model_name: str
    model_type: ModelType
    business_owner: str
    tech_owner: str
    validation_status: ValidationStatus
    risk_rating: Optional[ModelRiskRating] = None
    last_validated: Optional[str] = None
    next_review_date: Optional[str] = None
    compliance_score: Optional[int] = None
    framework: RegulatoryFramework = RegulatoryFramework.SR117
    notes: str = ""
