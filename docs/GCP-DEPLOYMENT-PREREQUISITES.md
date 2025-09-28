# GCP Deployment Prerequisites

Before running the Terraform deployment, you need to manually create some resources that require higher-level permissions.

## Required Manual Setup

### 1. Create Artifact Registry Repository

Since the service account doesn't have permission to create Artifact Registry repositories, create it manually:

```bash
# Set your project ID
export PROJECT_ID="marine-potion-470417-c7"
export REGION="us-west1"
export REPO_NAME="duckdb-analytics"

# Create the repository
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for DuckDB Analytics containers" \
    --project=$PROJECT_ID
```

### 2. Required Service Account Permissions

The service account used in GitHub Actions needs these IAM roles:

```bash
# Get your service account email
export SA_EMAIL="your-service-account@$PROJECT_ID.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.writer"
```

### 3. Enable Required APIs

Enable the necessary Google Cloud APIs:

```bash
gcloud services enable run.googleapis.com \
    storage.googleapis.com \
    artifactregistry.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    --project=$PROJECT_ID
```

## GitHub Secrets Configuration

In your GitHub repository, set these secrets:

1. **GCP_SA_KEY**: The JSON key for your service account
2. **GCP_PROJECT_ID**: Your Google Cloud project ID (marine-potion-470417-c7)

## Verification

After setup, verify the repository exists:

```bash
gcloud artifacts repositories list --location=$REGION --project=$PROJECT_ID
```

You should see your `duckdb-analytics` repository listed.

## Troubleshooting

### Permission Denied Errors
- Ensure your service account has all the required roles listed above
- Check that all APIs are enabled
- Verify the service account key is correctly set in GitHub secrets

### Repository Not Found
- Make sure you created the Artifact Registry repository with the correct name
- Verify the region matches what's configured in your Terraform variables (us-west1)

### Service Account Name Length
The Terraform has been updated to use shorter service account names to comply with the 30-character limit.