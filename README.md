# MandateOps

**A constraint-aware UPI AutoPay retry sequencer — built for the Razorpay Buildathon (Track 03: AI Revenue Recovery).**

UPI AutoPay gives every failed mandate exactly one initial attempt plus three retries, inside fixed non-peak execution windows, with a mandatory 24-hour pre-debit notice. MandateOps treats every retry attempt as a scarce, budgeted resource — not a cron job — and uses AI only where AI belongs: reading messy text, never moving money.

See [`../BUILD-BLUEPRINT.md`](../BUILD-BLUEPRINT.md) for the full architecture, UI system, and AI design this project implements.

## Project structure

```
mandateops/
├── backend/          FastAPI + SQLite backend (deterministic core, statistical scorer, Gemini AI layer, simulation engine)
├── frontend/          React + Vite + TypeScript + Tailwind dashboard
├── .env.example       Copy to .env and fill in your Gemini API key
└── BUILD-BLUEPRINT.md (one level up) full design document
```

## Local development

### Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

API docs available at `http://127.0.0.1:8000/docs` once running.

### Frontend

```bash
cd frontend
npm run dev
```

App available at `http://127.0.0.1:5173`. The Vite dev server proxies `/api` and `/ws` to the backend on port 8000.

## Environment variables

Copy `.env.example` to `.env` at the project root and set `GEMINI_API_KEY` (free tier, from https://aistudio.google.com/apikey). See the file for all other configurable values.

## Deployment target

Single AWS EC2 instance (2 vCPU / 4GB RAM / 40GB SSD): Nginx reverse-proxying a built static frontend and a systemd-managed Uvicorn process, SQLite on the local SSD. No Docker/Postgres/Redis — see the blueprint for the reasoning.
