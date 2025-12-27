#!/bin/bash
set -e

echo "Setting up K3s for MiniJira..."

# Load environment variables
set -a
source /home/ubuntu/minijira/.env
set +a

# Create nginx-certs secret
echo "Creating TLS certificates secret..."
sudo k3s kubectl create secret generic nginx-certs \
  --from-file=local.crt=/opt/minijira/certs/local.crt \
  --from-file=local.key=/opt/minijira/certs/local.key \
  -n minijira --dry-run=client -o yaml | sudo k3s kubectl apply -f -

# Apply all manifests
echo "Applying Kubernetes manifests..."
for file in k8s/*.yml; do
  envsubst < "$file" | sudo k3s kubectl apply -f -
done

echo "Setup complete"
sudo k3s kubectl get pods -n minijira