variable "aws_region" {
  type        = string
  description = "AWS region (e.g. ap-south-1, us-east-1)."
  default     = "us-east-1"
}

variable "name_prefix" {
  type        = string
  description = "Prefix for resource names (lowercase letters, digits, hyphens only — required by ALB, RDS, ElastiCache, etc.)."
  default     = "aimos"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,30}$", var.name_prefix))
    error_message = "Use lowercase letters, digits, hyphens only; start with a letter; max 31 chars."
  }
}

variable "vpc_cidr" {
  type        = string
  default     = "10.42.0.0/16"
  description = "VPC CIDR block."
}

variable "db_name" {
  type        = string
  default     = "aimos"
  description = "Postgres database name."
}

variable "db_username" {
  type        = string
  default     = "aimos"
  description = "Postgres master username."
}

variable "db_allocated_storage" {
  type        = number
  default     = 20
  description = "RDS allocated storage (GB)."
}

variable "db_instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "RDS instance class."
}

variable "redis_node_type" {
  type        = string
  default     = "cache.t3.micro"
  description = "ElastiCache node type."
}

variable "fargate_cpu" {
  type        = number
  default     = 512
  description = "Fargate task CPU units (256, 512, 1024, ...)."
}

variable "fargate_memory" {
  type        = number
  default     = 1024
  description = "Fargate task memory (MB)."
}

variable "container_image" {
  type        = string
  nullable    = true
  default     = null
  description = "Full image URI including tag. Leave null to use the created ECR repository at :latest (push image after first apply)."
}

variable "openai_api_key" {
  type        = string
  sensitive   = true
  description = "OpenAI API key (stored in Secrets Manager, referenced by ECS tasks)."
}

variable "jwt_secret" {
  type        = string
  sensitive   = true
  description = "JWT signing secret for the API."
}

variable "additional_container_env" {
  type        = map(string)
  default     = {}
  description = "Extra environment variables for all containers (plain strings in task definition)."
}

variable "enable_deletion_protection" {
  type        = bool
  default     = false
  description = "Enable ALB deletion protection (set true in production)."
}

variable "skip_final_snapshot" {
  type        = bool
  default     = true
  description = "If true, RDS skip final snapshot on destroy (dev/staging)."
}

variable "db_backup_retention_days" {
  type        = number
  default     = 1
  description = "RDS backup retention (days); increase for production."
}

variable "db_deletion_protection" {
  type        = bool
  default     = false
  description = "Enable RDS deletion protection in production."
}
