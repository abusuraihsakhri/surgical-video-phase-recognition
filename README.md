# Surgical Video Phase Recognition

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Surgical Video Phase Recognition is an enterprise-grade analytical platform that evaluates task payloads across specialized worker agents to determine clinical urgency, safety interlocks, and protocol conformance. It provides cryptographic audit trails, PHI outbound protection, and multi-agent consensus scoring.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Agent Consensus**: Three specialized workers evaluate each payload (QC Invariant, Safety Escalation, Protocol Conformance).

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation (Audit)
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --status DISCORDANT --critical
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task identifier (required)
- `--target`: Target entity identifier (required)
- `--primary`: Primary metric value (float, required)
- `--secondary`: Secondary metric value (float, optional)
- `--critical`: Emergency escalation flag (optional)
- `--status`: Status descriptor string (optional)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Parameter / observation metric | Required |
| `secondary_metric` | Parameter / observation metric | Optional |
| `is_critical_flag` | Parameter / observation metric | Optional |
| `status_descriptor` | Parameter / observation metric | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment environment variable before running in production:
```bash
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

Without this variable, a development-only fallback key is used with a runtime warning.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

```bash
docker build -t surgical-video-phase-recognition .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-key-here" surgical-video-phase-recognition
```

Or with docker-compose (create a `.env` file with `AUDIT_SECRET_KEY`):

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
surgical-video-phase-recognition/
├── agents/                  # Core agent modules (workers, supervisor, API, models)
│   ├── __init__.py
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # PHI guard, HMAC audit trail, security
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics collector
│   ├── models.py           # Pydantic schemas
│   ├── streamer.py         # WebSocket telemetry broadcaster
│   ├── supervisor.py       # Multi-agent orchestrator
│   └── workers.py          # Specialized evaluation workers
├── surgiphase_agent/        # Alternative agent implementation
│   ├── agents.py           # Sub-agent implementations
│   ├── cli.py              # Alternative CLI
│   ├── engine.py           # Core domain engine
│   ├── models.py           # Data models
│   └── server.py           # FastAPI server factory
├── tests/                   # Pytest test suite
├── web/index.html           # Operations console UI
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulation
├── enrichment.py            # Enrichment feature engines
├── pyproject.toml           # Project metadata & dependencies
├── Dockerfile               # Container image definition
└── docker-compose.yml       # Container orchestration
```
