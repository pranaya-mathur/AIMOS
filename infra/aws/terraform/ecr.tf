resource "aws_ecr_repository" "app" {
  name                 = "${var.name_prefix}/app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = { Name = "${var.name_prefix}-ecr" }
}
