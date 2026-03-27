#!/usr/bin/env bash
# Build → push ECR → terraform apply → force ECS rollout (needs aws cli, docker, terraform).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA="${ROOT}/infra/aws/terraform"

cd "$INFRA"
if [[ ! -f terraform.tfvars ]]; then
  echo "ERROR: Copy terraform.tfvars.example to terraform.tfvars and fill values." >&2
  exit 1
fi

echo "=== terraform init ==="
terraform init -input=false

echo "=== terraform apply (infra + ECS) ==="
terraform apply -input=false -auto-approve

REGION="$(terraform output -raw aws_region)"
REPO="$(terraform output -raw ecr_repository_url)"
CLUSTER="$(terraform output -raw ecs_cluster_name)"
PREFIX="$(terraform output -raw name_prefix)"
REGISTRY="${REPO%%/*}"

echo "=== ECR login (${REGISTRY}) ==="
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"

cd "$ROOT"
echo "=== docker build & push (${REPO}:latest) ==="
if docker buildx version >/dev/null 2>&1; then
  docker buildx build --platform linux/amd64 -t "${REPO}:latest" --push .
else
  docker build -t "${REPO}:latest" .
  docker push "${REPO}:latest"
fi

echo "=== ECS force new deployment ==="
for SVC in "${PREFIX}-api" "${PREFIX}-worker" "${PREFIX}-beat"; do
  aws ecs update-service --cluster "$CLUSTER" --service "$SVC" --force-new-deployment --region "$REGION" >/dev/null
  echo "  updated: $SVC"
done

ALB_URL="$(cd "$INFRA" && terraform output -raw alb_http_url)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ALB URL:    ${ALB_URL}"
echo " Docs:      ${ALB_URL}/docs"
echo " ECR:       ${REPO}:latest"
echo " Region:    ${REGION}"
echo " Set Bubble: CORS_ORIGINS + PUBLIC_API_BASE_URL=${ALB_URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
