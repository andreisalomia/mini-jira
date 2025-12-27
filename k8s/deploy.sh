#!/bin/bash
set -e

SHA=$1

if [ -z "$SHA" ]; then
  echo "Usage: ./deploy.sh <git-sha>"
  exit 1
fi

echo "Deploying MiniJira with SHA: $SHA"

# Load environment variables
set -a
source /home/ubuntu/minijira/.env
set +a

# Pull new images
echo "Pulling images from ghcr.io..."
docker pull ghcr.io/andreisalomia/minijira-backend:$SHA
docker pull ghcr.io/andreisalomia/minijira-frontend:$SHA
docker pull ghcr.io/andreisalomia/minijira-nginx:$SHA

# Clean up ALL old images except the one we just pulled
echo "Cleaning up old images..."
docker images ghcr.io/andreisalomia/minijira-backend --format "{{.ID}} {{.Tag}}" | grep -v $SHA | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
docker images ghcr.io/andreisalomia/minijira-frontend --format "{{.ID}} {{.Tag}}" | grep -v $SHA | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
docker images ghcr.io/andreisalomia/minijira-nginx --format "{{.ID}} {{.Tag}}" | grep -v $SHA | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true

# Update image tags in K8s deployments
echo "Updating Kubernetes deployments..."
sudo k3s kubectl set image deployment/backend backend=ghcr.io/andreisalomia/minijira-backend:$SHA -n minijira
sudo k3s kubectl set image deployment/frontend frontend=ghcr.io/andreisalomia/minijira-frontend:$SHA -n minijira

# Wait for rollout
echo "Waiting for rollout to complete..."
sudo k3s kubectl rollout status deployment/backend -n minijira --timeout=5m
sudo k3s kubectl rollout status deployment/frontend -n minijira --timeout=5m

echo "Deployment complete - SHA: $SHA"
sudo k3s kubectl get pods -n minijira