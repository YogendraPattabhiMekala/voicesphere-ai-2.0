# VoiceSphere AI 2.0
[![CI](https://github.com/YogendraPattabhiMekala/voicesphere-ai-2.0/actions/workflows/ci.yml/badge.svg)](https://github.com/YogendraPattabhiMekala/voicesphere-ai-2.0/actions/workflows/ci.yml)
A multi-tenant contact-center engineering portfolio project for fictional retailer **Northstar Retail**. This repository currently delivers a runnable API + web console with tenant-aware customer/order/ticket workflows, agent configuration, session issuance, an explicit mock voice mode, and a separate LiveKit Agents worker using Deepgram, OpenAI, Cartesia, and Silero plugins. The API can issue scoped LiveKit tokens with agent dispatch, and the browser has an opt-in microphone/media connection path. The provider-backed end-to-end call has not been exercised; local default mode is intentionally mock.

> **Status:** foundation and business-tool MVP. Not production-ready; see [known limitations](docs/KNOWN_LIMITATIONS.md) and [progress](PROJECT_PROGRESS.md). No real customer records or credentials belong here.

## Quick start (Python + Node)
1. Copy `.env.example` to `.env` and set a long random `APP_SECRET_KEY`.
2. API: `cd apps/api && python -m venv .venv` then activate and `pip install -r requirements.txt`; run `alembic upgrade head`, `python -m voicesphere.seed`, then `uvicorn voicesphere.main:app --reload --port 8000`.
3. Web: `cd apps/web && npm ci && npm run dev`. Visit http://localhost:3000.
4. Demo sign-in: `admin@northstar.test` / `DemoPassword123!` (seed-only). API docs at http://localhost:8000/docs.

For Docker: `docker compose up --build` (Docker Desktop required). The local SQLite path is the default for zero-setup development; `DATABASE_URL` can point to PostgreSQL. PostgreSQL + pgvector deployment profile and provider credentials are not required for the offline demo.

## Honest feature status
- Implemented: API auth, role checks, tenant-scoped data access, seed records, customer verification, orders, tickets, agents, audit events, session-token endpoint (mock or LiveKit credentials), basic dashboard, tests.
- Implemented but not live-tested: LiveKit browser transport/session token and a Deepgram/OpenAI/Cartesia/Silero voice worker. Credentials and a LiveKit server are needed to run it. Its business tools are intentionally disabled.
- Not implemented: production OIDC, pgvector ingestion and RAG, Redis/Celery workflows, actual human-agent room handoff, billing-grade usage metering, full ECS/RDS AWS stack. AWS and Docker were not tested. No audio is recorded by the mock.
- Never paste secrets into source control. See `docs/LOCAL_SETUP.md` and `docs/KNOWN_LIMITATIONS.md`.

## Dashboard URLs
The sidebar uses Next.js routes so browser navigation is persistent: `/` (Overview), `/ai-agents`, `/voice-playground`, `/customers`, `/orders`, `/support-tickets`, and `/audit-log`. Direct entry, refresh, and Back/Forward are covered by Playwright browser tests.

## Project map
See `docs/ARCHITECTURE.md`. `PROJECT_PROGRESS.md` contains actual build/test evidence. Contributions welcome; CI does not need production secrets.
## System Architecture

Explore the high-level architecture and real-time voice conversation flow of VoiceSphere AI 2.0.

[View Architecture Diagrams](docs/VOICE_ARCHITECTURE.md)
