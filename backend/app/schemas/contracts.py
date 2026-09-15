from typing import Any, Literal
from pydantic import BaseModel, Field


class PolicyRule(BaseModel):
    field: str
    operator: Literal['<', '<=', '>', '>=', '==', '!=']
    value: int | float | str
    unit: str | None = None


class PolicyChangeRequest(BaseModel):
    policy_name: str
    old_text: str
    new_text: str


class PolicyContract(BaseModel):
    policy_name: str
    subject: str
    attribute: str
    old_rule: PolicyRule
    new_rule: PolicyRule
    change_type: str
    risk_domain: str = 'business'
    boundary_values: list[int | float] = Field(default_factory=list)


class Artifact(BaseModel):
    id: str
    name: str
    artifact_type: Literal['DOCUMENT', 'WEBSITE', 'CHATBOT', 'FORM', 'API', 'CODE']
    content: str
    relationship: str
    source_path: str | None = None


class ImpactFinding(BaseModel):
    artifact_id: str
    artifact_name: str
    affected: bool
    severity: Literal['low', 'medium', 'high', 'critical']
    confidence: float = Field(ge=0, le=1)
    relationship: str
    evidence: str
    reason: str
    status: Literal['compliant', 'stale', 'unknown']


class PatchProposal(BaseModel):
    artifact_id: str
    artifact_name: str
    original_content: str
    proposed_content: str
    diff: str
    rationale: str
    status: Literal['proposed', 'approved', 'rejected'] = 'proposed'


class VerificationCase(BaseModel):
    name: str
    input: dict[str, Any]
    expected: Any
    actual: Any
    passed: bool


class VerificationReport(BaseModel):
    total: int
    passed: int
    failed: int
    cases: list[VerificationCase]
    verified: bool


class ProofReceipt(BaseModel):
    policy_name: str
    change_summary: str
    artifacts_examined: int
    affected_artifacts: int
    confirmed_inconsistencies: int
    critical_inconsistencies: int
    approved_fixes: int
    verification_tests: int
    tests_passed: int
    tests_failed: int
    policy_coverage_percent: float
    behavior_verification: Literal['PASSED', 'FAILED']
    evidence_hash: str
