# DevOps Learning Project

## Purpose
This project is a hands-on learning environment to progressively apply DevOps principles by evolving a simple application from local development to production-grade infrastructure.

## Step 1 - Simple Local Development & Docker

- Built a simple full-stack issue tracking application
- Implemented core domain logic (auth, projects, issues, workflows)
- Fully containerized frontend, backend, and database using Docker
- Orchestrated services locally with Docker Compose

## Step 2 — Single VM Cloud Deployment

- Deployed the containerized app to a single AWS EC2 VM via SSH  
- Manually installed and configured Docker on a fresh Linux server  
- Exposed services using cloud firewalls (Security Groups)  
- Encountered issues with ssh-key permissions 
- Resolved frontend prod-only failures (build-time env vars, dev proxy assumptions)

## Step 3