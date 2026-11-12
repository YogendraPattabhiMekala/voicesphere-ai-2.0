# Deployment

Docker Compose describes an API and Next app for local use. Docker was unavailable in the build environment, so the compose build and health check are **NOT TESTED**. Terraform contains an unapplied partial foundation for a private encrypted/versioned S3 knowledge bucket and CloudWatch log groups; it is not a deployable app stack. No paid cloud resources were created. See `infrastructure/terraform/README.md` for missing ECS/RDS/Redis/network/TLS/secrets work. AWS deployment is **NOT TESTED**.

Before cloud deployment: use managed PostgreSQL, private networking, secrets manager, TLS ALB, distinct task roles, durable backups, image scanning, least-privilege S3, and verified LiveKit/provider egress. No `terraform apply` has been run.
