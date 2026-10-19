<p align="center">
  <img src="docs/assets/screens/root.png" alt="pastebox running" width="900">
</p>

<h1 align="center">pastebox</h1>

<p align="center"><b>A pastebin that stores ciphertext and burns after the first read.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/pastebox/actions/workflows/ci.yml"><img src="https://github.com/scar8969/pastebox/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-71.4%-green" alt="coverage: 71.4%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20live-0969da" alt="routes: 8 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

pastebox accepts an already-encrypted paste, keeps the ciphertext, IV and salt, and returns it only to a caller who supplies the password. Pastes can carry an expiry or burn after the first read.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

A pastebin that stores plaintext is a database of other people's secrets waiting to be read. pastebox never receives the plaintext: the CLI derives a key with PBKDF2-HMAC-SHA256 and encrypts with AES-GCM before upload, so the row it stores is bytes it cannot open without the password.

## What it does

| Capability | How it works |
| --- | --- |
| **Encrypted by construction** | The API requires ciphertext; there is no plaintext column and no route that accepts one. |
| **PBKDF2 + AES-GCM** | A 16-byte salt, a 12-byte nonce and a 256-bit derived key, authenticated on decrypt. |
| **Expiry and burn** | A paste expires on read, or deletes itself after the first view. |
| **CLI** | put reads stdin, encrypts locally with the password you pass and prints the share URL. |

## Quickstart

```sh
git clone https://github.com/scar8969/pastebox.git
cd pastebox
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/view-demo.png" alt="/view/demo" width="100%"><br><sub><code>/view/demo</code> &middot; 22.6 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.2 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.8 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 25.7 KB</sub></td>
</tr>
</table>

## API

Every route below is declared in [`openapi/pastebox.yaml`](openapi/pastebox.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/pastes` | create |
| `GET` | `/p/<token>` | view |
| `DELETE` | `/p/<token>` | burn |

## CLI

The same operations without an HTTP client. Installed as `pastebox`, and runnable from a checkout with no install:

```sh
python -m pastebin.cli --help
```

```text
usage: pb [-h] {put} ...

positional arguments:
  {put}

options:
  -h, --help  show this help message and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (1.7 s, exit 0) |
| Line coverage | **71.4%** — 425 of 565 statements |
| Source | 15 files / 1,315 lines |
| Test code | 4 files / 232 lines |
| Documented paths | 2 in the spec, 1 GET |
| Live probe | 9 GET requests to the booted app, **8 answered 200** |
| Median latency | **6.1 ms** (single uncached request, dev server) |
| Slowest / fastest | 98.2 ms `/` / 4.7 ms `/livez` |
| Bytes served | 9.8 KB across 9 responses |
| Screenshots | 7 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ pastebin/app.py:get_app()
                │  reads config once (pastebin/config.py)
                │  registers the `paste` blueprint
                ▼
           route handler
             ├──▶ pastebin/models.py        tables, via Flask-SQLAlchemy
             ├──▶ pastebin/errors.py        raises typed errors → one JSON envelope
             └──▶ pastebin/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
pastebox/
├── src/pastebin/
│   ├── http.py                         379  HTTP plumbing for pastebin: correlation ids, access 
│   ├── observability.py                169  Structured logging and request correlation for paste
│   ├── config.py                       168  Environment-driven configuration for pastebin
│   ├── app.py                          119  Application factory for pastebin
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── _app.py                          96  pastebox — Flask application entry point
│   ├── paste/api.py                     58  
│   ├── paste/store.py                   55  
│   ├── paths.py                         52  Filesystem layout for pastebin
│   ├── cli.py                           42  
│   ├── paste/crypto.py                  36  
│   ├── models.py                        20  
├── openapi/pastebox.yaml                  the contract of record
├── schema/pastebox.sql                    the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `paste/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t pastebox .
docker run --rm -p 8000:8000 --env-file .env.example pastebox
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- A forgotten password is an unrecoverable paste: the key is derived from it, not stored.
- Decryption runs in the view page with the password you type, so a reader who never supplies one only ever holds ciphertext.

## License

MIT — see [LICENSE](LICENSE).
