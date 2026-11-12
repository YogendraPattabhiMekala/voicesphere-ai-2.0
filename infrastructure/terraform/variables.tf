variable "aws_region" {
  description = "AWS region for the un-applied storage/observability foundation."
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Short project label used in resource tags and the S3 prefix."
  type        = string
  default     = "voicesphere"
}

variable "environment" {
  description = "Environment label. Use non-production for portfolio demonstrations."
  type        = string
  default     = "demo"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,16}$", var.environment))
    error_message = "Environment must be 2-16 lowercase letters, digits, or hyphens."
  }
}

variable "log_retention_days" {
  description = "CloudWatch log retention."
  type        = number
  default     = 30
}
