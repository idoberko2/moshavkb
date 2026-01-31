# Deployment Guide

1. Run `terraform apply`
2. Run `scp -i ~/.ssh/id_rsa.pub docker-compose.prod.yml shekef@[IP_ADDRESS]:~/moshavkb`
3. Run `scp -i ~/.ssh/id_rsa.pub deployment_scripts/deploy.sh shekef@[IP_ADDRESS]:~/moshavkb`
4. Run `scp -i ~/.ssh/id_rsa.pub deployment_scripts/backup_chroma.sh shekef@[IP_ADDRESS]:~/moshavkb`
5. Run `scp -i ~/.ssh/id_rsa.pub deployment_scripts/restore_chroma.sh shekef@[IP_ADDRESS]:~/moshavkb`
6. SSH into the VM and edit the .env file to set the correct values for:
    1. TELEGRAM_INGESTION_BOT_TOKEN=
    2. TELEGRAM_QUERY_BOT_TOKEN=
    3. OPIK_API_KEY=
    4. OPIK_WORKSPACE=
    5. OPIK_PROJECT_NAME=
    6. QUERY_ALLOWED_USERS=
    7. QUERY_ALLOWED_GROUPS=
    8. INGEST_ALLOWED_USERS=
    9. INGEST_ALLOWED_GROUPS=
7. Run `./deploy.sh` with the latest version tag
8. Setup cron jobs for backup and restore
    1. Run `crontab -e`
    2. Add the following lines:
        0 0 * * * cd ~/moshavkb && ./backup_chroma.sh >> ~/cron_backup.log 2>&1
