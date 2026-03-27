output "alb_dns_name" {
  description = "Public ALB DNS name (HTTP :80 → API :8000)."
  value       = aws_lb.main.dns_name
}

output "alb_http_url" {
  description = "ALB base URL for Bubble / clients (HTTP)."
  value       = "http://${aws_lb.main.dns_name}"
}

output "name_prefix" {
  description = "Prefix used for ECS service names (e.g. aimos-api)."
  value       = var.name_prefix
}

output "aws_region" {
  description = "Deployed region."
  value       = var.aws_region
}

output "ecr_repository_url" {
  description = "Push the AIMOS image here, tag :latest (or set container_image)."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "ECS cluster name."
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC id."
}

output "secrets_manager_secret_name" {
  value       = aws_secretsmanager_secret.app.name
  description = "App secret (DATABASE_URL, REDIS_URL, OPENAI_API_KEY, JWT_SECRET)."
}
