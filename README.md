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
| `VITE_CHAT_API_KEY` | frontend copy of `CHAT_API_KEY` for requests | – |

Only exact origins are accepted. Separate multiple entries with commas and avoid wildcards (`*`), which are rejected for security.

### Chat authentication

Requests to `/api/chat` must include an `X-API-Key` header matching `CHAT_API_KEY`. The frontend reads this value from `VITE_CHAT_API_KEY` at build time and attaches it to requests.

For local development, set both `CHAT_API_KEY` and `VITE_CHAT_API_KEY` in `.env` to the same value. In production, configure the backend's `CHAT_API_KEY` and provide `VITE_CHAT_API_KEY` during the frontend build so the browser sends the correct header.

### Request size limits

The backend rejects bodies larger than `MAX_REQUEST_SIZE` (10 KB). Requests declaring a larger `Content-Length` receive a **413**. For chunked or streaming requests without `Content-Length`, the body is read incrementally and processing stops once the limit is exceeded, returning **413**.

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
