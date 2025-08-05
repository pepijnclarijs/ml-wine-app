provider "github" {
  token = var.github_token
  owner = var.github_owner
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