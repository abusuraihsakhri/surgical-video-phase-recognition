# Surgical Video Phase Recognition

**Status: deterministic task-evaluation prototype, not a surgical video recognition model.**

This repository evaluates numeric task payloads using threshold and descriptor rules. Despite the repository name, it **does not** process video, classify operative phases, track instruments, or contain a trained model. Its thresholds are illustrative software defaults, not validated clinical decision limits.

## Browser application

The `web/index.html` console runs locally in the browser without installing Python. It reproduces the three rule checks, reports results as an **unsigned demonstration**, and exports JSON. It does not upload data, use browser storage, or generate fabricated audit signatures. The `Local FastAPI service` option posts to a same-origin Python API when the backend is running.

To open the browser console from a local checkout, open `web/index.html` in a modern browser. GitHub Pages may serve the same console through the repository homepage if Pages is enabled.

**Do not enter patient-identifiable data. Not for clinical decisions.**

## Python installation

Python 3.10 or later:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Usage

Single task:

```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --status DISCORDANT --critical
```

Batch CSV (accepts `true/false`, `1/0`, `yes/no` in `is_critical_flag`):

```bash
python cli.py batch -i sample.csv -o results.csv
```

Alternative installed command-line interface:

```bash
surgical-video-phase-recognition audit
```

Start the API and open <http://127.0.0.1:8000/>:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
```

Endpoints: `GET /` (console), `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`.

The audit log endpoint requires an `AUDIT_LOGS_TOKEN` environment variable and an `Authorization: Bearer <token>` request header; without a configured token it responds with HTTP 403. `/api/chat` uses a deterministic placeholder, **not** an integrated language model.

## Rule semantics

| Input | Condition | Outcome |
| --- | --- | --- |
| `primary_metric` | `> 25` | Elevated alert |
| `secondary_metric` | `> 12` | Elevated alert |
| `is_critical_flag` | True | Critical alert |
| `status_descriptor` | Contains DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL, or REJECT | Elevated alert |

Critical alerts take precedence over elevated alerts. The browser reproduces these rules without cryptographic signing; server-side audit records are HMAC-chained in memory using `AUDIT_SECRET_KEY`. Chain verification recomputes each record's HMAC. The log is not persistent and these controls do **not** establish HIPAA compliance or comprehensive de-identification.

## Security and deployment

Avoid uploading clinical records or identifiers: the server implements only heuristic identifier-pattern blocking, not comprehensive PHI detection. The API does not have general authentication or rate limiting; bind it to a trusted local interface or secure it behind a gateway before exposing it.

To run Docker:

```bash
docker build -t surgical-video-phase-recognition .
docker run --rm -p 127.0.0.1:8000:8000 -e AUDIT_SECRET_KEY="replace-with-unique-random-key" surgical-video-phase-recognition
```

For Compose, copy `.env.example` to `.env`, set a unique `AUDIT_SECRET_KEY`, then run `docker compose up --build`.

## Development and verification

CI installs the package, checks Python compilation and dependencies, verifies browser-script syntax, and runs the pytest suite on Python 3.10–3.12. Tests cover core rule evaluation, the legacy CLI, HMAC tampering, boolean CSV parsing, API validation, and access controls.

Technology: Python, FastAPI, Pydantic, JavaScript, HTML/CSS. No WebAssembly or Pyodide is required because the browser demonstration reimplements the small deterministic rule set directly in JavaScript. The Python API and in-memory HMAC audit cannot run on GitHub Pages.

## License

MIT — see [LICENSE](LICENSE).
