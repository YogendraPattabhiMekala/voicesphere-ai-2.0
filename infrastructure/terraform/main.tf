resource "aws_s3_bucket" "knowledge_documents" {
  bucket_prefix = "${var.project_name}-${var.environment}-knowledge-"
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "knowledge_documents" {
  bucket                  = aws_s3_bucket.knowledge_documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "knowledge_documents" {
  bucket = aws_s3_bucket.knowledge_documents.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "knowledge_documents" {
  bucket = aws_s3_bucket.knowledge_documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "knowledge_documents" {
  bucket = aws_s3_bucket.knowledge_documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/${var.project_name}/${var.environment}/api"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "voice_worker" {
  name              = "/${var.project_name}/${var.environment}/voice-worker"
  retention_in_days = var.log_retention_days
}
