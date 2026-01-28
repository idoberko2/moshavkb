terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.rg_location
}

# --- Storage ---
resource "azurerm_storage_account" "sa" {
  name                     = "${var.storage_account_prefix}${random_id.random.hex}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.storage_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "sc" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "sc_backup" {
  name                  = var.backup_container_name
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "sc_tfstate" {
  name                  = var.tfstate_container_name
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "random_id" "random" {
  byte_length = 4
  keepers = {
    rotate = "5"
  }
}

# --- Azure OpenAI ---
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.resource_group_name}-openai-${random_id.random.hex}"
  location            = var.openai_location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = var.openai_sku_name
  custom_subdomain_name = "${var.resource_group_name}-openai-${random_id.random.hex}"
}

resource "azurerm_cognitive_deployment" "chat" {
  name                 = "${var.chat_model_name}-deployment"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = var.chat_model_name
    version = var.chat_model_version
  }
  scale {
    type = "GlobalStandard"
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "${var.embedding_model_name}-deployment"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = var.embedding_model_name
    version = var.embedding_model_version
  }
  scale {
    type = "GlobalStandard"
  }
}


# --- Networking ---
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.resource_group_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "pip" {
  name                = "${var.resource_group_name}-ip"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard" 
}

resource "azurerm_network_security_group" "nsg" {
  name                = "${var.resource_group_name}-nsg"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*" 
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "nic" {
  name                = "${var.resource_group_name}-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "nic_nsg" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# --- Virtual Machine ---
resource "azurerm_linux_virtual_machine" "vm" {
  name                = "${var.resource_group_name}-vm"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  size                = var.vm_size
  admin_username      = var.admin_username
  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts" 
    version   = "latest"
  }

  # Cloud-Init to Install Docker and Inject Credentials
  custom_data = base64encode(<<EOF
#!/bin/bash
# Install Docker
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Setup App directory
mkdir -p /home/${var.admin_username}/moshavkb

# Inject Credentials into .env file
cat <<EOT >> /home/${var.admin_username}/moshavkb/.env
# Azure Storage Credentials
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=${azurerm_storage_account.sa.name};AccountKey=${azurerm_storage_account.sa.primary_access_key};EndpointSuffix=core.windows.net"
AZURE_CONTAINER_NAME="${azurerm_storage_container.sc.name}"
AZURE_BACKUP_CONTAINER_NAME="${azurerm_storage_container.sc_backup.name}"

# Azure OpenAI Credentials
AZURE_OPENAI_API_KEY="${azurerm_cognitive_account.openai.primary_access_key}"
AZURE_OPENAI_ENDPOINT="${azurerm_cognitive_account.openai.endpoint}"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"
AZURE_DEPLOYMENT_NAME="${azurerm_cognitive_deployment.chat.name}"
AZURE_EMBEDDING_DEPLOYMENT_NAME="${azurerm_cognitive_deployment.embedding.name}"

# Providers
LLM_PROVIDER="azure"
STORAGE_PROVIDER="azure"
EOT

# Set Permissions
chown ${var.admin_username}:${var.admin_username} /home/${var.admin_username}/moshavkb/.env
chmod 600 /home/${var.admin_username}/moshavkb/.env

echo "Deployment credentials injected to /home/${var.admin_username}/moshavkb/.env"
EOF
)
}

output "public_ip" {
  value = azurerm_public_ip.pip.ip_address
}

output "storage_account_name" {
  value = azurerm_storage_account.sa.name
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}
