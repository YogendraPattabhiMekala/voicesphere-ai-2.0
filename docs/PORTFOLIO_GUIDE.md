# Portfolio walkthrough

1. Explain the control plane/media plane split and why the current UI labels sessions as mock.
2. Start API, seed Northstar's fictitious tenant, and sign in to the dashboard.
3. Inspect the tenant-filtered customer/order lists and synthetic metric counts.
4. Demonstrate verification: `POST /api/tools/verify-customer` using jordan.lee@example.test / 4821, then retrieve `NS-10482` with the short-lived verification token.
5. Create a ticket and a draft agent; publish an agent. Show audit events and role guards.
6. Discuss boundary: do not claim two-way voice/RAG/handoff is complete. Outline follow-on steps: LiveKit worker pipeline; provider-backed streaming; RAG with pgvector and citations; OIDC; Postgres RLS; tests and telemetry.

Interview topics: JWT/membership tenant resolution, password hashing, request validation, transactions, why short-lived verification token, direct WebRTC transport, and clear mock/live distinction. Keep the synthetic-data warning visible.
