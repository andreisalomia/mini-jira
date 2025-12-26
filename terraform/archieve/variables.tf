variable "postgres_user" {
  type        = string
}

variable "postgres_password" {
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  type        = string
}

variable "secret_key" {
  type        = string
  sensitive   = true
}

variable "flask_env" {
  type        = string
}

variable "cors_origins" {
  type        = string
}

variable "vite_api_url" {
  type        = string
}

variable "ec2_ip" {
  type        = string
}
