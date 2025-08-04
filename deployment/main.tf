# Declare variables
variable "azure_subscription_id" {
  type = string
}
variable "resource_group_name" {
  type = string
}
variable "location" {
  type = string
}
variable "github_token" {
  type      = string
  sensitive = true
}
variable "github_owner" {
  type = string
}
variable "github_repo" {
  type = string
}
variable "docker_token" {
  type      = string
  sensitive = true
}
variable "docker_username" {
  type = string
}
variable "container_app_name" {
  type = string
}
variable "env" {
  type = string
}

# Create environment specific variables
locals {
  resource_group_name_full = "${var.resource_group_name}-${var.env}"
  image_repository         = "wine-app"
  image_tag                = "${var.env}-latest"
  image_full               = "${var.docker_username}/${local.image_repository}:${local.image_tag}"
}

# Pin provider versions for reproducibility
terraform {
  backend "azurerm" {
    resource_group_name  = var.resource_group_name
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "${var.env}.terraform.tfstate" # e.g., dev.terraform.tfstate
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.86"
    }
    github = {
      source  = "integrations/github"
      version = ">= 5.0"
    }
  }
}

# Declare providers
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

provider "github" {
  token = var.github_token
  owner = var.github_owner
}

# Declare resources
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name_full
  location = var.location
}

resource "azurerm_log_analytics_workspace" "log" {
  name                = "${azurerm_resource_group.main.name}-log"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "aca_env" {
  name                       = "aca-env"
  location                   = var.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id
}

resource "azurerm_container_app" "aca" {
  name                         = var.container_app_name
  container_app_environment_id = azurerm_container_app_environment.aca_env.id
  resource_group_name          = azurerm_resource_group.main.name
  location                     = var.location
  revision_mode                = "Single"

  secret {
    name  = "dockerhub-token"
    value = var.docker_token
  }

  registry {
    server               = "index.docker.io"
    username             = var.docker_username
    password_secret_name = "dockerhub-token"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = var.container_app_name
      image  = local.image_full
      cpu    = 0.5
      memory = "1.0Gi"

      # Adding some environment variables that might be useful.
      env {
        name  = "APP_VERSION"
        value = local.image_tag
      }

      env {
        name  = "ENV"
        value = var.env
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}

# Push docker variables to github for CI/CD via GH actions
resource "github_actions_secret" "docker_username" {
  repository      = var.github_repo
  secret_name     = "DOCKER_USERNAME"
  plaintext_value = var.docker_username
}

resource "github_actions_secret" "docker_token" {
  repository      = var.github_repo
  secret_name     = "DOCKER_TOKEN"
  plaintext_value = var.docker_token
}

resource "github_actions_secret" "app_version" {
  repository      = var.github_repo
  secret_name     = "APP_VERSION"
  plaintext_value = local.image_tag
}

resource "github_actions_secret" "docker_registry" {
  repository      = var.github_repo
  secret_name     = "DOCKER_REGISTRY"
  plaintext_value = "index.docker.io"
}
