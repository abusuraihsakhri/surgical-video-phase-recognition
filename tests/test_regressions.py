"""Regression tests for audit integrity, CSV parsing, and API access controls."""
import pytest
from fastapi.testclient import TestClient

from agents.base import AuditTrail, SecurityException
from agents.api import app
from cli import parse_csv_bool as parse_main_bool
from surgiphase_agent.cli import parse_csv_bool as parse_legacy_bool


def test_tampering_rejected_even_if_links_unchanged():
    trail = AuditTrail(secret_key="test-hmac-key")
    trail.log("supervisor", "worker", "EVAL", {"task_id": "T1"})
    trail.log("supervisor", "worker", "EVAL", {"task_id": "T2"})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "forged"
    assert not trail.verify_integrity()


def test_signature_tampering_rejected():
    trail = AuditTrail(secret_key="test-hmac-key")
    trail.log("supervisor", "worker", "EVAL", {"task_id": "T1"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_exposed_audit_entries_cannot_mutate_chain():
    trail = AuditTrail(secret_key="test-hmac-key")
    trail.log("supervisor", "worker", "EVAL", {"task_id": "T1"})
    trail.get_trail()[0]["actor"] = "forged"
    assert trail.verify_integrity()


def test_phi_rejected_in_audit_actor():
    trail = AuditTrail(secret_key="test-hmac-key")
    with pytest.raises(SecurityException):
        trail.log("Patient MRN-994827", "worker", "EVAL", {"task_id": "T1"})


@pytest.mark.parametrize("parser", [parse_main_bool, parse_legacy_bool])
@pytest.mark.parametrize(("raw", "expected"), [
    ("False", False), ("0", False), ("no", False), ("", False),
    ("True", True), ("1", True), ("yes", True), (True, True),
])
def test_csv_bool(parser, raw, expected):
    assert parser(raw) is expected


@pytest.mark.parametrize("parser", [parse_main_bool, parse_legacy_bool])
def test_reject_invalid_csv_bool(parser):
    with pytest.raises(ValueError):
        parser("perhaps")


def test_api_rejects_phi_with_client_error():
    response = TestClient(app).post("/api/audit", json={
        "task_id": "MRN-994827", "target_identifier": "TARGET-01", "primary_metric": 2,
    })
    assert response.status_code == 400
    assert "994827" not in response.text


def test_audit_logs_require_token(monkeypatch):
    monkeypatch.delenv("AUDIT_LOGS_TOKEN", raising=False)
    client = TestClient(app)
    assert client.get("/api/audit/logs").status_code == 403
    monkeypatch.setenv("AUDIT_LOGS_TOKEN", "example-test-token")
    assert client.get("/api/audit/logs").status_code == 403
    response = client.get("/api/audit/logs", headers={"Authorization": "Bearer example-test-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_console_served_at_root():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Browser-only" in response.text


def test_phi_block_metric_is_incremented():
    from agents.metrics import GLOBAL_METRICS
    from agents.base import PHIGuard
    before = GLOBAL_METRICS.phi_blocks_total
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("MRN-994827")
    assert GLOBAL_METRICS.phi_blocks_total == before + 1


def test_legacy_metadata_does_not_claim_video_inference():
    from surgiphase_agent.server import create_app
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json()["domain"] == "rule-based demo"
