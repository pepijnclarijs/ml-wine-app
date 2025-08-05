# Pin provider versions for reproducibility and use remote (shared) backend.
# NOTE: Variable usage is not allowed inside the terraform block. 
terraform {
  backend "azurerm" {
    resource_group_name  = "wine-rg-prod"
    storage_account_name = "tfstateprod855f1f"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.97"
    }
    github = {
      source  = "integrations/github"
      version = ">= 5.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = ">= 2.47"
    }
  }
}

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
variable "storage_account_name" {
  type = string
}

# Create environment specific variables
locals {
  image_repository = "wine-app"
  image_tag        = "${var.env}-latest"
  image_full       = "${var.docker_username}/${local.image_repository}:${local.image_tag}"
}

# Declare provider
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# Declare resources
# Add blob container for holding the trained ML models
data "azurerm_storage_account" "existing" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_storage_container" "model_blob_container" {
  name                  = "ml-models"
  storage_account_id    = data.azurerm_storage_account.existing.id
  container_access_type = "private"
}

resource "azurerm_log_analytics_workspace" "log" {
  name                = "${var.resource_group_name}-log"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  daily_quota_gb      = 0.5
}

resource "azurerm_container_app_environment" "aca_env" {
  name                       = "aca-env"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = 0
    maximum_count         = 1
  }
}

resource "azurerm_container_app" "aca" {
  name                         = var.container_app_name
  container_app_environment_id = azurerm_container_app_environment.aca_env.id
  resource_group_name          = var.resource_group_name
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
    min_replicas = 0
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

      env {
        name  = "ML_MODELS_STORAGE_CONNECTION_STRING"
        value = data.azurerm_storage_account.existing.primary_connection_string
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
