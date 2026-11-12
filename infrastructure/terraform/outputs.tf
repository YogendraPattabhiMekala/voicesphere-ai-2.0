output "knowledge_bucket_name" {
  description = "Private encrypted/versioned bucket for future tenant-scoped knowledge documents."
  value       = aws_s3_bucket.knowledge_documents.bucket
}

output "api_log_group_name" {
  value = aws_cloudwatch_log_group.api.name
}

output "voice_worker_log_group_name" {
  value = aws_cloudwatch_log_group.voice_worker.name
}
