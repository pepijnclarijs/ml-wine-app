provider "github" {
  token = var.github_token
  owner = var.github_owner
}

provider "azuread" {}

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

# Create Service Principal for GitHub Actions to interact with Azure
resource "azuread_application" "github_actions_app" {
  display_name = "GitHubActionsDeployer"
}

resource "azuread_application_password" "github_actions_app_secret" {
  application_id = azuread_application.github_actions_app.id
  display_name   = "GitHubActionsAppSecret"
  end_date       = timeadd("2025-08-04T00:00:00Z", "8760h") # 1 year
}

# Service Principal for github actions
resource "azuread_service_principal" "github_actions_sp" {
  client_id = azuread_application.github_actions_app.client_id
}

# Retrieves information about the currently authenticated Azure client
# Used for tenant ID and object ID of the user/service principal running Terraform
data "azurerm_client_config" "current" {}

# Assign container app contributor role to Service Principal
resource "azurerm_role_assignment" "github_actions_function_app_contributor" {
  scope                = azurerm_container_app.aca.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.github_actions_sp.object_id
}

# Store all credentials in a single JSON-formatted GitHub secret
resource "github_actions_secret" "azure_credentials_json" {
  repository  = var.github_repo
  secret_name = "AZURE_CREDENTIALS"
  plaintext_value = jsonencode({
    clientId       = azuread_application.github_actions_app.client_id
    clientSecret   = azuread_application_password.github_actions_app_secret.value
    tenantId       = data.azurerm_client_config.current.tenant_id
    subscriptionId = data.azurerm_client_config.current.subscription_id
  })
}
