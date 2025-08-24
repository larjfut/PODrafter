# PO Drafter

A trauma‑informed web application that helps Texas domestic‑violence survivors,
advocates, and legal‑aid staff generate **ready‑to‑file Protective‑Order (PO) packets**
through a secure chat wizard.

## Why PO Drafter?
* **Survivor‑centered** – plain‑language chat gathers only required info.
* **Privacy‑first** – drafts stay client‑side; “Quick Escape” wipes data.
* **Offline‑friendly** – PWA caching allows work without internet.
* **Rapid filing** – merges answers into PDF forms and auto‑creates cover‑letter & guide.

> **Scope v0.2** – One Texas‑wide petition + three pilot counties (Harris, Dallas, Travis).
> Firearm addendum and full 254‑county rollout are backlog items.

### Features
| Category      | Details                                                 |
|---------------|---------------------------------------------------------|
| Chat intake   | GPT‑4o + function calls; static wizard fallback offline |
| Review mode   | Users edit any field before generating documents        |
| PDF generator | Python micro‑service fills AcroForms, returns ZIP       |
| Safety        | Quick Escape, HTTPS‑only, no cookies by default         |
| Accessibility | WCAG 2.1 AA colors, keyboard‑friendly                   |

### Tech Stack
| Layer      | Choice                                 |
|------------|----------------------------------------|
| Frontend   | SvelteKit PWA, TypeScript, Tailwind CSS |
| AI Engine  | OpenAI GPT‑4o (function calling)       |
| Backend    | FastAPI on Fly.io/AWS Lambda           |
| PDF Tools  | pdfrw, PyPDF2                          |
| Tests      | Playwright (E2E), pytest (unit)        |

### Quick Start
```bash
git clone https://github.com/larjfut/PODrafter.git
cd PODrafter
# backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker run -d -p 6379:6379 redis:7
pytest
# start the server (requires OPENAI_API_KEY)
REDIS_URL=redis://localhost:6379 uvicorn backend.main:app --reload --port 8080
# frontend
cd frontend && npm install
npm test -- --watchAll=false
npm run dev
```

### Docker build

Build the backend image from the repository root:

```bash
docker build -f backend/Dockerfile .
```

### Environment Variables

Copy `.env.example` to `.env` and set these keys:

| Name | Purpose | Default |
|------|---------|---------|
| `OPENAI_API_KEY` | OpenAI token for GPT requests | – |
| `ALLOWED_ORIGINS` | comma‑separated list of allowed CORS origins (exact URLs; wildcards `*` forbidden) | `http://localhost:5173` |
| `VITE_API_BASE_URL` | Base path for the backend API | `/api` |
| `REDIS_URL` | Redis connection string for rate limiting | `redis://localhost:6379/0` |
| `CHAT_API_KEY` | shared secret for `/api/chat`; sent via `X-API-Key` header | – |

Only exact origins are accepted. Separate multiple entries with commas and avoid wildcards (`*`), which are rejected for security.

### Chat authentication

Requests to `/api/chat` must include an `X-API-Key` header matching `CHAT_API_KEY`. Ensure the frontend adds this header to chat requests.

### Installing Test Dependencies

Install Python packages for the micro‑service and Node packages for the SvelteKit front‑end before running tests.

```bash
# Python packages
pip install -r requirements.txt

# Node packages
cd frontend && npm install
```

### License

MIT – see `LICENSE.md`.
