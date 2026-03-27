# AIMOS on AWS (Terraform)

This stack creates:

- **VPC** — two AZs, public subnets (ALB + NAT) and private subnets (ECS, RDS, Redis).
- **RDS** — PostgreSQL 15 (`db.t3.micro` by default).
- **ElastiCache** — Redis 7 for Celery (`cache.t3.micro` by default).
- **ECR** — container registry for the AIMOS image.
- **ECS Fargate** — three services: **api** (behind ALB), **worker**, **beat** (same image, different commands).
- **ALB** — HTTP `:80` → API `:8000`, health check `GET /health/live`.
- **Secrets Manager** — one JSON secret with `DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `JWT_SECRET` (injected into tasks).

Stripe, Meta, WhatsApp, media keys, etc. are **not** in Terraform by default; add them via `additional_container_env` in `terraform.tfvars` or extend the secret / task definitions.

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.5
- AWS account + [configured credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) (`aws configure` or env vars)
- Docker (to build and push the image to ECR)

## Configure

```bash
cd infra/aws/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: openai_api_key, jwt_secret, aws_region, etc.
```

Do **not** commit `terraform.tfvars` (it is gitignored).

## One-command deploy (repo root)

From the **repository root** (after `terraform.tfvars` exists and AWS CLI + Docker work):

```bash
chmod +x scripts/deploy_aws.sh
./scripts/deploy_aws.sh
```

This runs `terraform apply`, builds and pushes **`linux/amd64`** to ECR (for Fargate), then forces new deployments for **api**, **worker**, and **beat**. It prints **`alb_http_url`** and the ECR image URI.

If the **first** `terraform apply` fails because ECS cannot pull an image yet, run **`./scripts/deploy_aws.sh` again** after the first successful push (or push manually, then `aws ecs update-service --force-new-deployment`).

## First-time deploy (recommended order)

1. **Plan and apply** (creates ECR among other resources):

   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

   On the first apply, ECS may fail to stabilize until an image exists in ECR. That is expected.

2. **Log in to ECR** (replace region and account id from `aws sts get-caller-identity`):

   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
   ```

3. **Build and push** from the **repository root** (where the `Dockerfile` lives):

   ```bash
   docker build -t aimos:latest .
   docker tag aimos:latest $(terraform output -raw ecr_repository_url):latest
   docker push $(terraform output -raw ecr_repository_url):latest
   ```

4. **Force new ECS deployment** so tasks pull the new image:

   ```bash
   aws ecs update-service --cluster $(terraform output -raw ecs_cluster_name) --service <name_prefix>-api --force-new-deployment
   aws ecs update-service --cluster $(terraform output -raw ecs_cluster_name) --service <name_prefix>-worker --force-new-deployment
   aws ecs update-service --cluster $(terraform output -raw ecs_cluster_name) --service <name_prefix>-beat --force-new-deployment
   ```

   Replace `<name_prefix>` with your `name_prefix` variable (default `aimos`).

5. **Smoke test:** open `http://$(terraform output -raw alb_dns_name)/docs` (or `/health/live`).

## Outputs

- `alb_dns_name` — public URL (HTTP only until you add ACM + HTTPS listener).
- `ecr_repository_url` — push target for the image.
- `ecs_cluster_name` — for `aws ecs` CLI commands.
- `secrets_manager_secret_name` — edit in console if you rotate keys without Terraform.

## Destroy

```bash
terraform destroy
```

If RDS `skip_final_snapshot` is `false`, destroy may create a final snapshot. ElastiCache and RDS deletion order is handled by Terraform; empty ECR repos may need manual cleanup if destroy fails on dependencies.

## Production notes

- Turn on **ALB HTTPS** (ACM certificate + `aws_lb_listener` on 443) and redirect HTTP → HTTPS.
- Set `db_deletion_protection`, `skip_final_snapshot = false`, larger instance classes, multi-AZ RDS, Redis replicas, and `enable_deletion_protection` on the ALB.
- Add **WAF** on the ALB, **VPC Flow Logs**, and **least-privilege** IAM for the task role if the app calls AWS APIs.
- Pin **Terraform** and provider versions in `versions.tf` for repeatable applies.
