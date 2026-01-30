variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "moshavkb-rg"
}

variable "rg_location" {
  description = "Region for Resource Group (MetaData)"
  type        = string
  default     = "Israel Central"
}

variable "location" {
  description = "Azure Region"
  type        = string
  default     = "France Central"
}

variable "openai_location" {
  description = "Region for OpenAI resources (must support the requested models)"
  type        = string
  default     = "East US 2"
}

variable "storage_location" {
  description = "Region for Storage Account"
  type        = string
  default     = "Israel Central"
}

variable "storage_account_prefix" {
  description = "Prefix for the storage account name (must be unique)"
  type        = string
  default     = "moshavkbstorage"
}

variable "container_name" {
  description = "Name of the storage container for documents"
  type        = string
  default     = "moshavkb"
}

variable "backup_container_name" {
  description = "Name of the storage container for backups"
  type        = string
  default     = "moshavkb-backups"
}

variable "tfstate_container_name" {
  description = "Name of the storage container for terraform state"
  type        = string
  default     = "tfstate"
}

variable "vm_size" {
  description = "Size of the Virtual Machine"
  type        = string
  default     = "Standard_B2pls_v2"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "adminuser"
}

variable "public_key_path" {
  description = "Path to the SSH public key file"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# --- OpenAI ---
variable "openai_sku_name" {
  description = "SKU for Azure OpenAI Service"
  type        = string
  default     = "S0"
}

variable "chat_model_name" {
  description = "Model name for Chat (e.g., gpt-4o-mini)"
  type        = string
  default     = "gpt-4o-mini"
}

variable "chat_model_version" {
  description = "Model version for Chat"
  type        = string
  default     = "2024-07-18"
}

variable "embedding_model_name" {
  description = "Model name for Embeddings"
  type        = string
  default     = "text-embedding-3-small"
}

variable "embedding_model_version" {
  description = "Model version for Embeddings"
  type        = string
  default     = "1"
}
