resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.name_prefix}-redis-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.name_prefix}-redis-subnet-group" }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id             = "${var.name_prefix}-redis"
  replication_group_description    = "AIMOS Redis for Celery"
  engine                           = "redis"
  engine_version                   = "7.0"
  node_type                        = var.redis_node_type
  port                           = 6379
  num_cache_clusters             = 1
  automatic_failover_enabled     = false
  subnet_group_name              = aws_elasticache_subnet_group.main.name
  security_group_ids             = [aws_security_group.redis.id]
  at_rest_encryption_enabled     = true
  transit_encryption_enabled     = false
  snapshot_retention_limit       = 0

  tags = { Name = "${var.name_prefix}-redis" }
}
