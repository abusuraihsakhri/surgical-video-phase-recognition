"""
FastAPI REST API Server for Surgical Video Phase Recognition.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from .metrics import GLOBAL_METRICS

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Surgical Video Phase Recognition API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "surgical-video-phase-recognition", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    """Return Prometheus-compatible text exposition format."""
    sys_lbl = "surgical-video-phase-recognition"
    dossier_count = len(supervisor.dossier_registry)
    audit_count = len(AuditLogger.get_trail())
    lines = [
        "# HELP dossiers_processed_total Total dossiers processed by the supervisor",
        "# TYPE dossiers_processed_total counter",
        f'dossiers_processed_total{{system="{sys_lbl}"}} {dossier_count}',
        "",
        "# HELP audit_blocks_total Total HMAC-SHA256 audit blocks signed",
        "# TYPE audit_blocks_total counter",
        f'audit_blocks_total{{system="{sys_lbl}"}} {audit_count}',
        "",
        "# HELP phi_outbound_blocks_total Total PHI outbound guard blocks",
        "# TYPE phi_outbound_blocks_total counter",
        f'phi_outbound_blocks_total{{system="{sys_lbl}"}} {GLOBAL_METRICS.phi_blocks_total}',
        "",
    ]
    return Response(content="\n".join(lines) + "\n", media_type="text/plain")


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
