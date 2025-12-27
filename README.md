# DevOps Learning Project

## Purpose

This project is a hands-on learning environment to progressively apply DevOps principles by evolving a simple application from local development to production-grade infrastructure.

### Step 1 - Simple Local Development & Docker

- Built a simple full-stack issue tracking application
- Implemented core domain logic (auth, projects, issues, workflows)
- Fully containerized frontend, backend, and database using Docker
- Orchestrated services locally with Docker Compose

### Step 2 — Single VM Cloud Deployment

- Deployed the containerized app to a single AWS EC2 VM via SSH  
- Manually installed and configured Docker on a fresh Linux server  
- Exposed services using cloud firewalls (Security Groups)  
- Encountered issues with ssh-key permissions
- Resolved frontend prod-only failures (build-time env vars, dev proxy assumptions)

### Step 3 — Reverse Proxy

- Went back to local, added NGINX as reverse proxy for single entry point (port 80)
- Removed Vite dev proxy - NGINX now handles all routing
- Configured location blocks to route `/` to frontend, `/api` to backend
- Fixed environment variable issues (build-time vs runtime) with Docker build args
- Implemented WebSocket support for Vite hot reload

### Step 4 — TLS & Statelessness

- Implemented HTTPS with self-signed certificates, TLS termination at NGINX only
- Configured automatic HTTP to HTTPS redirect on port 443
- Verified statelessness: backend/frontend restarts don't break user sessions (JWT-based auth)

### Step 5 - Terraform

- Defined entire infrastructure in Terraform (networks, volumes, containers, images)
- Automated image building within Terraform (no manual docker-compose build)
- Created reusable variable configuration (terraform.tfvars) for environment-specific values

### Step 6 - CI/CD with GitHub Actions & Terraform AWS

- Implemented CI pipeline with simple automated testing and Docker image builds
- Published images to GitHub Container Registry with immutable SHA tags
- Built CD pipeline for automated SSH deployment to EC2
- Imported existing EC2 infrastructure into Terraform state

### Step 7 — Kubernetes with K3s

- Migrated from Docker Compose to Kubernetes (K3s)
- Upgraded EC2 instance from t3.micro to t3.small as k3s requires more resources
- Implemented Kubernetes deployments, services, and persistent volumes
- Used Traefik Ingress for HTTP/HTTPS routing (ports 80/443) and removed NGINX
- Automated deployments with deploy.sh script
- CI/CD pipeline pushes images to ghcr.io, deploys via kubectl set image
- Maintained stateless architecture with external secrets and PVCs
