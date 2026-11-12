# Known limitations

- LiveKit token generation (with dispatch metadata), a browser microphone/LiveKit media path, and a separate LiveKit Agents worker integrating Deepgram STT, OpenAI LLM, Cartesia TTS, and Silero VAD are implemented. Provider-backed end-to-end conversations, interruptions, live transcript display, provider timeouts, and response latency have not been tested because no credentials/server were available. Mock session records only by default.
- Auth is demo password login, not OIDC; access token is stored in browser localStorage.
- SQLite is the tested development database; PostgreSQL configuration exists but was not exercised. pgvector/RAG ingestion is absent.
- No Redis, Celery, handoff queue, appointments, version-history snapshots, or automated transcript summaries.
- Dashboard sections show API-backed records for implemented routes; analytics, users/team, uploads, handoff, and detailed conversation pages are not implemented and are not represented as working.
- No API rate limiting, formal idempotency store, distributed tracing/metrics, recording/consent system, retention automation, or regulatory audit.
- Docker unavailable in the environment; compose and AWS Terraform not executed.
- No Playwright/k6 E2E tests. Frontend UI build depends on Node version compatibility; check final verification report.
