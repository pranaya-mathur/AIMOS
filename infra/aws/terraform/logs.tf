resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.name_prefix}"
  retention_in_days = 14

  tags = { Name = "${var.name_prefix}-ecs-logs" }
}
