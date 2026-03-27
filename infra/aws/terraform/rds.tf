resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.name_prefix}-db-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.name_prefix}-db-subnet-group" }
}

resource "aws_db_instance" "main" {
  identifier                 = "${var.name_prefix}-postgres"
  engine                     = "postgres"
  engine_version             = "15"
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  storage_type               = "gp3"
  db_name                    = var.db_name
  username                   = var.db_username
  password                   = random_password.db.result
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  skip_final_snapshot        = var.skip_final_snapshot
  publicly_accessible        = false
  backup_retention_period    = var.db_backup_retention_days
  deletion_protection          = var.db_deletion_protection
  auto_minor_version_upgrade = true

  tags = { Name = "${var.name_prefix}-rds" }
}
