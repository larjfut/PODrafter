# PO Drafter

A trauma‑informed web application that helps Texas domestic‑violence survivors, advocates, and legal‑aid staff generate **ready‑to‑file Protective‑Order (PO) packets** through a secure chat wizard.

---

## Why PO Drafter?

* **Survivor‑centered.** A plain‑language chat gathers only the information required to complete a petition.
* **Privacy‑first.** Drafts stay in the browser by default. Users can wipe all data instantly via a "Quick Escape" button.
* **Offline‑friendly.** Service‑worker caching lets users resume work even without internet access.
* **Rapid filing.** The app merges answers into county‑specific PDF forms and auto‑generates a cover letter and filing guide.

> **Scope v0.2** – Supports a single **Texas‑wide petition** form and **three pilot counties (Harris, Dallas, Travis)**. Firearm‑surrender addenda and the full 254‑county rollout sit in the backlog.

---

## Features

| Category | Details |
|----------|---------|
| Chat Intake | GPT‑4o with function‑calling outputs validated JSON; fallback static wizard when offline |
| Review Mode | Users can edit any field before generating documents |
| PDF Generator | Python micro‑service fills AcroForms and packages a ZIP for download or email |
| Safety | Quick Escape, HTTPS‑only, no cookies, optional 24‑hour S3 purge for emailed packets |
| Accessibility | WCAG 2.1 AA colors, keyboard navigation, screen‑reader labels |

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| **Frontend** | [SvelteKit](https://kit.svelte.dev/) PWA, TypeScript, Tailwind CSS |
| **AI Engine** | OpenAI GPT‑4o via function calls |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) served on Fly.io or AWS Lambda |
| **PDF Tools** | `pdfrw`, `PyPDF2`, `pdfbox‑layout` |
| **E2E Tests** | [Playwright](https://playwright.dev/) |
| **Unit Tests** | `pytest`, `pytest‑cov` |

---

## Project Structure

```text
protective-order-draft-bot/
├── backend/               # FastAPI service
│   ├── main.py
│   ├── requirements.txt
│   └── templates/
│       ├── cover_letter.html
│       └── filing_guide.html
├── forms/standard/        # Fillable PDF templates
│   ├── tx_general.pdf
│   ├── harris.pdf
│   ├── dallas.pdf
│   └── travis.pdf
├── frontend/              # SvelteKit app
│   └── ...
├── schema/                # JSON schemas for validation
│   └── petition.schema.json
├── scripts/               # CLI helpers (e.g., ingest‑pdf)
├── data/                  # Clerk directory CSV, lookup tables
└── README.md
```

---

## Quick Start (Local Dev)

### 1 – Clone & Install

```bash
git clone https://github.com/your‑org/protective-order-draft-bot.git
cd protective-order-draft-bot
```

**Backend**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

**Frontend**
```bash
cd frontend
npm install
```

### 2 – Environment Variables

Create `.env` in the repo root:

```env
OPENAI_API_KEY=sk‑...
ALLOWED_ORIGINS=http://localhost:5173
EMAIL_S3_BUCKET=po‑drafter‑packets
EMAIL_S3_TTL_HOURS=24
```

### 3 – Run Dev Servers

```bash
# Terminal 1 – backend (default :8000)
uvicorn backend.main:app --reload

# Terminal 2 – frontend (default :5173)
cd frontend
npm run dev
```

Visit `http://localhost:5173`.

---

## Running Tests

```bash
# Unit tests & coverage
pytest -q --cov=backend

# End‑to‑end tests
npm run test:e2e   # Playwright
```

---

## Linting & Formatting

* **Python :** `black`, `ruff`
* **JavaScript/TypeScript :** `eslint`, `prettier`
* **Commit hooks :** set up with `pre‑commit install`

---

## Deployment

### Fly.io (One‑Command)

```bash
fly launch  # config in fly.toml
```

### AWS Lambda + S3

1. Build a Docker image with `Dockerfile.backend`.
2. Push to ECR and deploy via SAM or CloudFormation.
3. Point CloudFront + Route 53 to the frontend static site.

---

## Security & Privacy Notes

* No server‑side storage unless the user explicitly emails a packet.
* PDF metadata is scrubbed on generation.
* CSP, HSTS, and TLS 1.2+ enforced.
* The repository **must not** contain production keys. Use secrets managers!

---

## Accessibility Checklist

- [x] Focus outlines visible
- [x] All interactive elements keyboard‑reachable
- [x] Labels + `aria‑live` regions in chat wizard
- [x] Color contrast ≥ 4.5:1

---

## Contributing

1. Fork & clone this repo.
2. Create a feature branch (`git checkout -b feat/my‑feature`).
3. Commit in logical chunks; reference issues.
4. Run tests + linters.
5. Open a pull request; fill in the PR template.

We follow the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

---

## Roadmap (Short‑Term)

- Add Spanish UI option.
- Integrate **firearm‑surrender addendum**.
- Expand template coverage to 30+ counties.
- Automatic ZIP ⇒ county lookup service.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

### Disclaimer

PO Drafter does **not** provide legal advice. Survivors should consult an attorney or legal‑aid organization to confirm filing requirements in their county.
