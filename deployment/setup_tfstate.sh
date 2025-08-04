#!/bin/bash

set -euo pipefail  # So that silent errors are avoided

# === Validate user input ===
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <environment>"
  echo "Example: $0 dev"
  exit 1
fi

ENV="$1"

# Validate ENV value
if [[ ! "$ENV" =~ ^(dev|test|acc|prod)$ ]]; then
  echo "Invalid environment: $ENV"
  echo "Must be one of: dev, test, acc, prod"
  exit 1
fi

# === Config ===
RESOURCE_GROUP="wine-rg-$ENV"
STORAGE_ACCOUNT="tfstate${ENV}$(date +%s | sha256sum | head -c 6)"  # Must be globally unique
CONTAINER_NAME="tfstate"

# === Create resources ===
echo "🔧 Creating resource group: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location westeurope

echo "Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location westeurope \
  --sku Standard_LRS \
  --encryption-services blob \
  --kind StorageV2

echo "🪣 Creating blob container: $CONTAINER_NAME"
az storage container create \
  --name "$CONTAINER_NAME" \
  --account-name "$STORAGE_ACCOUNT"

# === Output ===
cat <<EOF

Terraform backend storage created successfully!
Use this in your backend config:

terraform {
  backend "azurerm" {
    resource_group_name  = "$RESOURCE_GROUP"
    storage_account_name = "$STORAGE_ACCOUNT"
    container_name       = "$CONTAINER_NAME"
    key                  = "terraform.tfstate"
  }
}

EOF
