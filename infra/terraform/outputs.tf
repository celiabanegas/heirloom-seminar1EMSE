output "resource_group" {
  value = azurerm_resource_group.main.name
}

output "location" {
  value = azurerm_resource_group.main.location
}

output "postgres_host" {
  value = azurerm_postgresql_flexible_server.db.fqdn
}

# Goes into the Container App as a secret. Print it with: terraform output -raw database_url
output "database_url" {
  value = format(
    "postgresql://%s:%s@%s:5432/%s?sslmode=require",
    var.db_admin_login,
    urlencode(var.db_admin_password),
    azurerm_postgresql_flexible_server.db.fqdn,
    azurerm_postgresql_flexible_server_database.heirloom.name,
  )
  sensitive = true
}

output "storage_account_name" {
  value = azurerm_storage_account.web.name
}

output "website_url" {
  value = azurerm_storage_account.web.primary_web_endpoint
}
