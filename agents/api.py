"""
FastAPI REST API Server for Surgical Video Phase Recognition.
"""
import os
import secrets
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from .metrics import GLOBAL_METRICS

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Surgical Video Phase Recognition API",
    description="Deterministic rule-based task evaluation prototype; no video analysis or clinical validation.",
    version="2.0.1",
)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2048)


@app.get("/", include_in_schema=False)
def console():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "surgical-video-phase-recognition", "domain": "rule-based evaluation prototype", "standard": "demonstration rules only", "version": "2.0.1"}


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
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=400, detail="Identifier contains a prohibited data pattern") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Query contains a prohibited data pattern") from None


@app.get("/api/audit/logs")
def api_audit_logs(authorization: str | None = Header(default=None)):
    """Audit metadata is available only when an explicit access token is configured."""
    token = os.getenv("AUDIT_LOGS_TOKEN")
    if not token or not authorization or not secrets.compare_digest(authorization, f"Bearer {token}"):
        raise HTTPException(status_code=403, detail="Audit log access disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
