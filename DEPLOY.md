# Deployment Guide

This guide describes how to deploy the MoshavKB bots to a production VPS using Docker Compose.

## Prerequisites

1.  **VPS**: A server running Ubuntu LTS (or similar) with at least 2GB RAM.
2.  **S3 Bucket**: A managed S3 bucket (AWS, DigitalOcean, Cloudflare R2) and credentials.
3.  **GitHub Token**: If the repository is private, you might need a PAT, but the image is public if configured so on GHCR.

## Initial Setup on VPS

1.  **Install Docker & Docker Compose**:
    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

2.  **Prepare Directory**:
    ```bash
    mkdir -p ~/moshavkb/data
    cd ~/moshavkb
    ```

3.  **Files**: Copy the following files to `~/moshavkb`:
    - `docker-compose.prod.yml`
    - `.env` (Create this manually with production secrets)

4.  **Configure Environment**:
    Create `.env` with:
    ```env
    OPENAI_API_KEY=...
    TELEGRAM_QUERY_BOT_TOKEN=...
    TELEGRAM_INGESTION_BOT_TOKEN=...
    OPIK_API_KEY=...
    OPIK_WORKSPACE=...
    OPIK_PROJECT_NAME=...
    QUERY_ALLOWED_USERS=...
    QUERY_ALLOWED_GROUPS=...
    INGEST_ALLOWED_USERS=...
    INGEST_ALLOWED_GROUPS=...
    
    # S3 CONFIG
    S3_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com # or other provider
    S3_ACCESS_KEY_ID=...
    S3_SECRET_ACCESS_KEY=...
    S3_BUCKET_NAME=...
    S3_BACKUP_BUCKET_NAME=...
    S3_REGION_NAME=...
    ```

## Running the Application

1.  **Start Services**:
    ```bash
    docker compose -f docker-compose.prod.yml up -d
    ```

2.  **View Logs**:
    ```bash
    docker compose -f docker-compose.prod.yml logs -f
    ```

## Updates

To update the application to the latest version (after the GitHub Action has successfully run):

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Backup (Cron Setup)

To enable nightly backups of the ChromaDB vector store to S3:

1.  Edit Crontab:
    ```bash
    crontab -e
    ```

2.  Add the following line (adjust paths):
    ```cron
    0 3 * * * cd /home/ubuntu/moshavkb && docker compose -f docker-compose.prod.yml run --rm ingest-bot python scripts/backup_to_s3.py >> /var/log/moshavkb_backup.log 2>&1
    ```

## Disaster Recovery

If the VPS data is lost:

1.  Re-provision VPS and follow "Initial Setup".
2.  **Restore Data**:
    - Download the latest backup from S3 to the VPS.
    - Extract it to `~/moshavkb/data/chroma_db`.
    - `tar -xzvf chroma_backup_YYYYMMDD_HHMMSS.tar.gz -C ~/moshavkb/data/chroma_db`
3.  Start the application.

## Using Deployment Scripts (Recommended)

Three helper scripts are available in `deployment_scripts/` for easy management. Copy this folder to your VPS.

### Deploy / Update
To deploy a specific version (matching a GitHub Release tag):
```bash
./deployment_scripts/deploy.sh 1.0.0
```

### Backup
To manually trigger a backup to S3:
```bash
./deployment_scripts/backup_chroma.sh
```

### Restore
To restore from a backup file:
```bash
./deployment_scripts/restore_chroma.sh chroma_backup_20260128_120000.tar.gz
```

## Manual Operations

## Restoration (Manual)

To restore the vector database from a specific backup file:

1.  Find the backup filename in your S3 bucket (e.g., `chroma_backup_20260128_065504.tar.gz`).
2.  Stop the services (recommended to avoid locking):
    ```bash
    docker compose -f docker-compose.prod.yml stop
    ```
3.  Run the restore script:
    ```bash
    docker compose -f docker-compose.prod.yml run --rm ingest-bot python scripts/restore_from_s3.py chroma_backup_YYYYMMDD_HHMMSS.tar.gz
    ```
4.  Start the services:
    ```bash
    docker compose -f docker-compose.prod.yml up -d
    ```
