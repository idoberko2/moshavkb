"""
Tenant configuration helper for scripts.
Maps tenant names to their environment variable values for ChromaDB collections and Azure storage containers.
Must be called BEFORE importing src.config to ensure the correct env vars are set.
"""

import os
import argparse

TENANT_CONFIG = {
    "moshavkb": {
        "COLLECTION_NAME": "moshav_protocols",
        "AZURE_CONTAINER_NAME": "moshavkb",
    },
    "kehilatitkb": {
        "COLLECTION_NAME": "kehilatitkb_protocols",
        "AZURE_CONTAINER_NAME": "kehilatitkb",
    },
}

VALID_TENANTS = list(TENANT_CONFIG.keys())


def apply_tenant(tenant_name: str):
    """
    Sets environment variables for the specified tenant.
    Must be called BEFORE importing src.config.
    """
    if tenant_name not in TENANT_CONFIG:
        raise ValueError(f"Unknown tenant: {tenant_name}. Valid tenants: {VALID_TENANTS}")

    for env_var, value in TENANT_CONFIG[tenant_name].items():
        os.environ[env_var] = value


def add_tenant_argument(parser: argparse.ArgumentParser):
    """
    Adds a required --tenant argument to an argparse parser.
    """
    parser.add_argument(
        "--tenant",
        required=True,
        choices=VALID_TENANTS,
        help=f"Tenant to operate on. Choices: {', '.join(VALID_TENANTS)}",
    )
