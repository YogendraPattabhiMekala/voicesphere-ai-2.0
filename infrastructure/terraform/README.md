# Terraform foundation (partial; not a deployable app stack)

This Terraform slice defines a private-by-default, versioned, SSE-S3 encrypted knowledge bucket plus CloudWatch log groups. It is deliberately small and has not been applied. `terraform init`, `validate`, and cloud costs are **NOT TESTED** because Terraform/AWS access was not available and no AWS resources were authorized.

This is not the requested full ECS/Fargate, RDS, Redis, networking, TLS load balancer, or secret-manager deployment. Do not apply it expecting an application to run. Continue with reviewed modules for a VPC, ECS services (API/web/voice worker), private RDS/Redis, TLS ingress, IAM task roles, Secrets Manager, and telemetry before any environment deployment. Terraform state should use an encrypted remote backend and locking; it is not configured here.

To validate locally when Terraform is installed: `terraform init -backend=false && terraform fmt -check && terraform validate`. Applying may create billable resources; obtain explicit authorization first. Bucket names are AWS-global unique through `bucket_prefix`.
