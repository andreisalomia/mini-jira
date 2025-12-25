terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

provider "docker" {}

# Network
resource "docker_network" "app_network" {
  name = "minijira_network"
}

# Use existing volume (preserve data)
resource "docker_volume" "postgres_data" {
  name = "minijira_postgres_data"
}

# Build backend image
resource "docker_image" "backend" {
  name = "mini-jira-backend:latest"
  build {
    context = abspath("${path.module}/../backend")
    dockerfile = "Dockerfile"
    build_args = {}
  }
}

# Build frontend image
resource "docker_image" "frontend" {
  name = "mini-jira-frontend:latest"
  build {
    context = abspath("${path.module}/../frontend")
    dockerfile = "Dockerfile"
    build_args = {
      VITE_API_URL = var.vite_api_url
    }
  }
}

# Postgres
resource "docker_container" "postgres" {
  name = "minijira-postgres"
  image = "postgres:14-alpine"
  
  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}"
  ]
  
  networks_advanced {
    name = docker_network.app_network.name
  }
  
  volumes {
    volume_name = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  
  healthcheck {
    test = ["CMD-SHELL", "pg_isready -U ${var.postgres_user}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }
}

# Backend
resource "docker_container" "backend" {
  name  = "minijira-backend"
  image = docker_image.backend.name
  
  env = [
    "DATABASE_URL=postgresql://${var.postgres_user}:${var.postgres_password}@minijira-postgres:5432/${var.postgres_db}",
    "SECRET_KEY=${var.secret_key}",
    "FLASK_ENV=${var.flask_env}",
    "CORS_ORIGINS=${var.cors_origins}"
  ]

  command = [
    "sh",
    "-c",
    "./wait_for_db.sh && flask db upgrade && python seed.py && python run.py"
  ]
  
  networks_advanced {
    name = docker_network.app_network.name
  }
  
  depends_on = [docker_container.postgres]
}

# Frontend
resource "docker_container" "frontend" {
  name  = "minijira-frontend"
  image = docker_image.frontend.name
  
  networks_advanced {
    name = docker_network.app_network.name
  }
}

# NGINX
resource "docker_container" "nginx" {
  name  = "minijira-nginx"
  image = "nginx:alpine"
  
  networks_advanced {
    name = docker_network.app_network.name
  }
  
  ports {
    internal = 80
    external = 80
  }
  
  ports {
    internal = 443
    external = 443
  }
  
  volumes {
    host_path = abspath("${path.module}/../nginx/nginx.conf")
    container_path = "/etc/nginx/nginx.conf"
    read_only = true
  }
  
  volumes {
    host_path = abspath("${path.module}/../certs")
    container_path = "/etc/nginx/certs"
    read_only = true
  }
  
  depends_on = [docker_container.backend, docker_container.frontend]
}