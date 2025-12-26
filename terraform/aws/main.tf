terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

# Import existing VPC
data "aws_vpc" "existing" {
  id = "vpc-02b607bed740a4f47"
}

# Import existing subnet
data "aws_subnet" "existing" {
  id = "subnet-0d0586815b1230bdc"
}

# Security Group
resource "aws_security_group" "minijira" {
  name        = "launch-wizard-1"
  description = "launch-wizard-1 created 2025-12-23T15:21:01.649Z"
  vpc_id      = data.aws_vpc.existing.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["86.127.156.120/32"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["86.127.156.120/32"]
  }

  # Frontend
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["86.127.156.120/32"]
  }

  # Backend
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["86.127.156.120/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "minijira" {
  ami           = "ami-01fd6fa49060e89a6"
  instance_type = "t3.micro"
  subnet_id     = data.aws_subnet.existing.id
  
  vpc_security_group_ids = [aws_security_group.minijira.id]

  tags = {
    Name = "ServerMiniJira"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      ami,
      user_data,
      user_data_base64
    ]
  }
}

output "instance_id" {
  value = aws_instance.minijira.id
}

output "instance_public_ip" {
  value = aws_instance.minijira.public_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.minijira.public_ip}"
}