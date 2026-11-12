# Security notes

Implemented for this demo: Argon2 password hashes via `pwdlib`, expiring HS256 bearer JWTs, server-side membership lookup, role gates on writes, org-scoped SQL queries, short-lived signed customer verification token, schema validation, and audit entries for verification/ticket/agent actions. Passwords and API keys are never returned by API.

Limitations: demo bearer tokens are kept by browser localStorage (XSS risk); use OIDC + secure HttpOnly cookies for production. The demo secret fallback is unsafe and must be replaced. Login has no rate limiter/lockout, no CSRF because bearer auth is used, no formal data retention implementation, TLS depends on deployment ingress, and tenant isolation is application-level only. Recording is absent and disabled. Do not claim PCI, SOC 2, HIPAA, or other compliance. Use synthetic data only.

For production: secret manager, TLS-only ingress, OIDC, rate limits, audit integrity/retention, RLS, upload scanning, private object storage, threat model, pen test, data processing review, and customer consent controls.
