#!/bin/bash
# ActionMind AI - OKE Deployment Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE="actionmindai"
RELEASE_NAME="actionmindai"

echo -e "${GREEN}Deploying ActionMind AI to OKE...${NC}"

# Create namespace
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
helm upgrade --install "$RELEASE_NAME" ./helm/actionmindai-prod \
  --namespace "$NAMESPACE" \
  --values helm/actionmindai-prod/values-oke.yaml \
  --set dapr.enabled=false \
  --wait --timeout 10m

echo -e "${GREEN}Deployment complete!${NC}"
kubectl get pods -n "$NAMESPACE"
