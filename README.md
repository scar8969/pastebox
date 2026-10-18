<p align="center">
  <img src="docs/assets/screens/root.png" alt="pastebox running" width="900">
</p>

<h1 align="center">pastebox</h1>

<p align="center"><b>A pastebin that stores ciphertext and burns after the first read.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-71.4%-green" alt="coverage: 71.4%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20answered-0969da" alt="routes: 8 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

pastebox accepts an already-encrypted paste, keeps the ciphertext, IV and salt, and returns it only to a caller who supplies the password. Pastes can carry an expiry or burn after the first read.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

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

The same work from the CLI:

```sh
python -m pastebin.cli --help
```

Commands: `put`.

A first request:

```sh
curl -s http://127.0.0.1:8000/api/pastes | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`, `cryptography`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/pastebox.yaml`](openapi/pastebox.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/pastes` | create |
| `DELETE` | `/p/<token>` | burn |

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

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (1.5 s, exit 0) |
| Line coverage | **71.4%** — 425 of 565 statements |
| Source | 15 files / 1,314 lines |
| Test code | 4 files / 232 lines |
| Documented paths | 2 in the spec, 0 GET |
| Live probe | 9 GET requests to the booted app, **8 answered 200** |
| Median latency | **6.1 ms** (single uncached request, dev server) |
| Slowest / fastest | 98.2 ms `/` / 4.7 ms `/livez` |
| Bytes served | 9.8 KB across 9 responses |
| Screenshots | 7 captured |

## Architecture

```
pastebox/
├── src/pastebin/
│   ├── http.py                         379  HTTP plumbing for pastebin: correlation ids, access 
│   ├── config.py                       171  Environment-driven configuration for pastebin
│   ├── observability.py                169  Structured logging and request correlation for paste
│   ├── app.py                          119  Application factory for pastebin
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── _app.py                          96  pastebox — Flask application entry point
│   ├── paste/api.py                     58  
│   ├── paste/store.py                   55  
│   ├── paths.py                         52  Filesystem layout for pastebin
│   ├── cli.py                           38  
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
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t pastebox .
docker run --rm -p 8000:8000 --env-file .env.example pastebox
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- A forgotten password is an unrecoverable paste: the key is derived from it, not stored.
- Decryption runs in the view page with the password you type, so a reader who never supplies one only ever holds ciphertext.

## License

MIT — see [LICENSE](LICENSE).
