# Heirloom infrastructure on Azure:
#   - resource group
#   - Azure Database for PostgreSQL (flexible server) + the "heirloom" database   ← the managed resource the API uses
#   - storage account with the static website turned on                           ← hosts the frontend
# The Container App (API) is created afterwards with the Azure CLI, using the database URL from the outputs.

terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      # The Container App and its environment are created with the CLI inside this group:
      # let "terraform destroy" remove them too, so cleaning up is a single command.
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.subscription_id
}

# Storage account and Postgres server names are global in Azure: a random suffix avoids clashes.
resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

locals {
  suffix = random_string.suffix.result
  tags   = { app = "heirloom", owner = var.owner }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.prefix}"
  location = var.location
  tags     = local.tags
}

# ---------- PostgreSQL ----------

resource "azurerm_postgresql_flexible_server" "db" {
  name                          = "psql-${var.prefix}-${local.suffix}"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  version                       = "16"
  sku_name                      = "B_Standard_B1ms" # smallest burstable size: enough for a demo, cheapest option
  storage_mb                    = 32768
  backup_retention_days         = 7
  public_network_access_enabled = true # simple setup; see README "Production" for private networking
  administrator_login           = var.db_admin_login
  administrator_password        = var.db_admin_password # from terraform.tfvars, never committed
  tags                          = local.tags

  lifecycle {
    ignore_changes = [zone] # Azure picks an availability zone; don't fight it on later plans
  }
}

resource "azurerm_postgresql_flexible_server_database" "heirloom" {
  name      = "heirloom"
  server_id = azurerm_postgresql_flexible_server.db.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# 0.0.0.0 - 0.0.0.0 is Azure's special rule for "allow Azure services" (the Container App's outbound IPs).
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.db.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# ---------- Frontend hosting ----------

resource "azurerm_storage_account" "web" {
  name                     = "st${var.prefix}${local.suffix}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_storage_account_static_website" "web" {
  storage_account_id = azurerm_storage_account.web.id
  index_document     = "index.html"
  error_404_document = "index.html"
}
