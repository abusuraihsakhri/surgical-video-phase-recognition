"""
Security and input validation tests for Surgical Video Phase Recognition.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from pydantic import ValidationError
from agents.base import PHIGuard, AuditTrail, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload


class TestPHIGuard:
    """Tests for PHI outbound guard functionality."""

    def test_mrn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_ssn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789 recorded")

    def test_phone_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact patient at 555-123-4567")

    def test_email_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@hospital.org")

    def test_dob_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_patient_name_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_generic_patient_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient John Doe admitted")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")

    def test_empty_string_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_passes(self):
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        redacted = PHIGuard.redact_phi("Patient MRN-12345 and SSN 123-45-6789")
        assert "MRN" not in redacted or "[REDACTED" in redacted
        assert "REDACTED_IDENTIFIER" in redacted


class TestAuditTrail:
    """Tests for HMAC-SHA256 audit trail."""

    def test_custom_secret_key(self):
        trail = AuditTrail(secret_key="test-key-123")
        assert trail.secret_key == b"test-key-123"

    def test_audit_trail_integrity(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("test_actor", "worker", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "worker", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_chain(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor", "tier", "EVENT", {"step": 1})
        trail.log("actor", "tier", "EVENT", {"step": 2})
        logs = trail.get_trail()
        assert len(logs) == 2
        assert logs[1]["prev_hash"] == logs[0]["current_hash"]

    def test_phi_blocked_in_audit(self):
        trail = AuditTrail(secret_key="test-key")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"patient": "MRN-12345"})


class TestInputValidation:
    """Tests for SystemTaskPayload input validation."""

    def test_nan_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("nan")
            )

    def test_inf_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("inf")
            )

    def test_negative_inf_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                secondary_metric=float("-inf")
            )

    def test_valid_payload(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=25.0,
            secondary_metric=10.0
        )
        assert payload.primary_metric == 25.0
        assert payload.secondary_metric == 10.0

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="   ",
                target_identifier="KEY-01",
                primary_metric=10.0
            )

    def test_whitespace_stripped(self):
        payload = SystemTaskPayload(
            task_id="  T1  ",
            target_identifier="KEY-01",
            primary_metric=10.0
        )
        assert payload.task_id == "T1"

    def test_field_length_limit(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="X" * 200,
                target_identifier="KEY-01",
                primary_metric=10.0
            )

    def test_status_descriptor_length_limit(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=10.0,
                status_descriptor="X" * 100
            )
