# GitHub readiness report

**Assessment: portfolio MVP / partially GitHub-ready; not a complete enterprise contact-center release.** The core source, local setup, migrations, seed data, tests, lockfiles, and CI workflows are present. No repository was pushed and no cloud resources were created.

## Verification status
- **PASS** — FastAPI application imports and starts; local health endpoint responded 200.
- **PASS** — Alembic initial migration applied and seed script is idempotent.
- **PASS** — Automated backend suite: 8 passed, 0 failed; includes tenant scope, verification, order gating, ticket/agent, mock session, LiveKit token/dispatch claims.
- **PASS** — Playwright browser navigation suite: 2 tests passed; all seven sections verified by direct URL and reload, sidebar navigation, and browser Back/Forward.
- **PASS** — Ruff lint: all checks passed.
- **PASS** — Frontend TypeScript check (`npm run lint`) passed.
- **PASS** — Next production build passed on the available Node 20.20.2 runtime. npm warned that the project/dependency requires Node >=22.22; use Node 22.22+ for supported installs/CI.
- **PASS** — LiveKit Agents worker source compiles and its pinned plugins import after installation.
- **PASS** — Local Next-to-FastAPI rewrite proxy login and dashboard requests returned 200.
- **BLOCKED / NOT TESTED** — Real microphone-to-agent conversation, STT/LLM/TTS response, interruption behavior, and provider latency: requires working LiveKit and Deepgram/OpenAI/Cartesia credentials. The local mock is not voice evidence.
- **NOT TESTED** — PostgreSQL runtime, Docker/Compose (Docker CLI unavailable), Terraform/AWS (Terraform CLI unavailable; no paid resources authorized), k6, RAG, human agent room transfer, and production CI on GitHub.

## Implemented controls and gaps
Argon2 password hashes, signed expiring bearer tokens, membership-derived tenant scope, role checks, verification-gated order endpoint, short-lived verification token, and audit records are implemented. Demo authentication still uses localStorage and is not OIDC. The live voice worker intentionally has no business tools, so it cannot look up customer orders, create tickets, or claim verification/handoff.

**Do not describe this as production-ready or compliant.** Review `docs/KNOWN_LIMITATIONS.md` and `docs/SECURITY.md` before publishing.
