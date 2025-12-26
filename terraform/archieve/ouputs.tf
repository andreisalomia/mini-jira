output "app_url" {
  description = "Application URL"
  value = "https://localhost"
}

output "containers" {
  description = "Created containers"
  value = {
    postgres = docker_container.postgres.name
    backend  = docker_container.backend.name
    frontend = docker_container.frontend.name
    nginx = docker_container.nginx.name
  }
}

output "network" {
  description = "Docker network"
  value = docker_network.app_network.name
}

output "volume" {
  description = "Database volume"
  value = docker_volume.postgres_data.name
}