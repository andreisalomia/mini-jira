#!/bin/bash
set -e

echo "Deploying simple monitoring stack..."

# Create namespace
sudo k3s kubectl apply -f 00-namespace.yml

# Deploy Prometheus
sudo k3s kubectl apply -f 03-prometheus.yml
echo "Waiting for Prometheus..."
sudo k3s kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=120s

# Deploy Grafana
sudo k3s kubectl apply -f 04-grafana.yml
echo "Waiting for Grafana..."
sudo k3s kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=120s

echo ""
echo "Monitoring stack deployed!"
echo ""