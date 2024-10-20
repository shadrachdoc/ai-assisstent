# Migration Plan: Nexus Data to AKS with Azure Disk Backup

This migration plan outlines the steps required to back up Nexus data from a Docker container, store the backup in Azure Blob storage, and deploy Nexus on AKS (Azure Kubernetes Service) using Persistent Volume (PV) for data storage.

---

## Step 1: Create Disk for Backup

First, create an Azure Disk that will be used for storing the Nexus backup data.

```bash
az disk create \
  --resource-group 1-79e457a3-playground-sandbox \
  --name nexusdata \
  --size-gb 5 \
  --sku Standard_LRS

## Step 2: Backup Nexus Data Inside Docker Container
Next, use Docker to back up the Nexus data from the running Nexus container. Replace <nexus_container_id> with the actual ID of your running Nexus container.

```bash
docker run --rm --volumes-from <nexus_container_id> -v $(pwd):/backup alpine \
  tar czvf /backup/nexus-data-backup.tar.gz /nexus-data
