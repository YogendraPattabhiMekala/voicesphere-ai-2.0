# Project progress

## Follow-up: persistent browser navigation fix
- Root cause: the dashboard held `page` only in local React state, while sidebar/quick-action buttons called `setPage`; every path remained `/`, so refresh reset the page to Overview.
- Added Next.js App Router path `/` plus `/ai-agents`, `/voice-playground`, `/customers`, `/orders`, `/support-tickets`, `/audit-log`. The active section derives from `usePathname`; UI navigation uses `router.push`, preserving browser history.
- Added Playwright coverage for direct access + reload on all seven sections, sidebar selection, and Back/Forward. Browser suite: 2 passed.

## Phase 0 — Architecture: COMPLETE (scope accurately reduced to executable MVP)
- Defined modular monolith, tenant boundary, relational core, mock/live boundary, architecture/data diagrams.

## Phase 1 — Foundation: IMPLEMENTED; verification in progress
- FastAPI, SQLAlchemy models, password auth, membership-derived tenant scope, core customer/order/ticket/agent APIs, seed data, Next.js console, Docker/CI configs, Alembic setup.

## Phase 2 — Real-time voice: PARTIAL / BLOCKED for live audio
- Implemented optional LiveKit scoped session JWT with `voicesphere-support` agent dispatch, browser WebRTC connection/microphone enable/stop, and a LiveKit Agents worker using pinned Deepgram/OpenAI/Cartesia/Silero plugins with VAD. Mock mode explicitly says it has no media. Code compiles/imports; live provider session remains BLOCKED/NOT TESTED without credentials and a LiveKit server. Worker business tools are not connected.

## Phase 3 — Business tools: PARTIAL
- Verify customer, gated order lookup, create ticket, customer/order/ticket lists implemented against database. Appointment and idempotency store not implemented.

## Phase 4 — RAG: NOT IMPLEMENTED
- No document ingestion, embeddings, pgvector, hybrid search, citations, or eval runtime.

## Phase 5 — Handoff: NOT IMPLEMENTED

## Phase 6 — Dashboard: PARTIAL
- Overview, agent list/create/publish, playground mock session, customer/order/ticket/audit data pages. Many requested admin pages and true analytics are not built.

## Phase 7 — Security/reliability: PARTIAL
- Auth, role gates, tenant isolation tests, short-lived verification token, audit events. No OIDC, rate limiting, production secret manager, RLS, tracing, resilience controls.

## Phase 8 — DevOps: PARTIAL / NOT TESTED
- Compose, Dockerfiles, CI, Terraform stub included. Docker not installed; AWS not deployed; Terraform not applied.

## Phase 9 — Verification (current evidence)
- `pytest -q`: PASS, 8 passed, 0 failed (one upstream Starlette deprecation warning).
- `ruff check apps/api/voicesphere tests`: PASS.
- `npm run lint`: PASS (`tsc --noEmit`).
- `npm run build`: PASS on Node 20.20.2; npm gave engine warnings because Node >=22.22 is the documented supported runtime.
- `python -m py_compile services/voice-agent/agent.py`: PASS; worker dependencies installed and provider plugin imports checked.
- Alembic `upgrade head` and idempotent synthetic seed: PASS.
- Local API and frontend started; API health/login/dashboard through Next proxy returned 200.
- Live provider call, Docker/Compose, PostgreSQL, Terraform/AWS, Playwright/k6: NOT TESTED or BLOCKED. See readiness report.

## Phase 10 — Release
- `VoiceSphere-AI-2.0.zip` is packaged with source, docs, lockfiles, migration, tests, CI, and `.env.example`; packaging excludes `.env`, local DB, node_modules, `.next`, caches, and virtual environments.
- Archive content check: 57 files; lockfile/migration/env template included; `.env` absent.
- This is a runnable portfolio MVP, not a fully featured or production-ready contact-center product.
