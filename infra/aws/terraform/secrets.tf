resource "aws_secretsmanager_secret" "app" {
  name = "${var.name_prefix}/app"
  tags = { Name = "${var.name_prefix}-app-secret" }
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL     = "postgresql://${var.db_username}:${random_password.db.result}@${aws_db_instance.main.address}:5432/${var.db_name}"
    REDIS_URL        = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
    OPENAI_API_KEY   = var.openai_api_key
    JWT_SECRET       = var.jwt_secret
  })

  depends_on = [
    aws_db_instance.main,
    aws_elasticache_replication_group.main,
  ]
}
