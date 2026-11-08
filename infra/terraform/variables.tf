variable "subscription_id" {
  description = "Azure subscription ID (az account show --query id -o tsv)"
  type        = string
}

variable "location" {
  description = "Azure region. Student subscriptions only allow some regions: if you get a policy error, try another one."
  type        = string
  default     = "northeurope"
}

variable "prefix" {
  description = "Short name used in every resource name (lowercase letters and digits only)"
  type        = string
  default     = "heirloom"

  validation {
    condition     = can(regex("^[a-z0-9]{3,12}$", var.prefix))
    error_message = "prefix must be 3-12 lowercase letters or digits (storage account naming rules)."
  }
}

variable "owner" {
  description = "Tag added to every resource"
  type        = string
  default     = "celia"
}

variable "db_admin_login" {
  description = "PostgreSQL administrator user"
  type        = string
  default     = "heirloomadmin"
}

variable "db_admin_password" {
  description = "PostgreSQL administrator password (8+ chars, upper, lower and digits). Set it in terraform.tfvars."
  type        = string
  sensitive   = true
}
