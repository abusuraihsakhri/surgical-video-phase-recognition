"""
Pydantic v2 schemas and data definitions for Surgical Video Phase Recognition.
Domain: Rule-based evaluation prototype
Standard: Demonstration rules (not clinical standards)
"""
import datetime
import math
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier", max_length=128)
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target", max_length=128)
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor", max_length=64)
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def _strip_and_validate_strings(cls, v: str) -> str:
        if not isinstance(v, str):
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace-only")
        return stripped

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def _reject_nan_inf(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Metric values must be finite numbers (no NaN or Inf)")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "Demonstration rules (not clinical standards)"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "surgical-video-phase-recognition"
    domain: str = "Clinical & Biomedical AI"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "Demonstration rules (not clinical standards)"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
