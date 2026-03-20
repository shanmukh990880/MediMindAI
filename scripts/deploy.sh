#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="medibrief-ai"
REGION="us-central1"
# Artifact Registry is the modern replacement for GCR
REPOSITORY="medibrief-repo"
IMAGE_TAG="${REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME"

echo "🚀 Starting Deployment of MediBrief AI to Google Cloud Run..."

# 1. Enable APIs
echo "🔧 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com \
    documentai.googleapis.com \
    aiplatform.googleapis.com \
    cloudtrace.googleapis.com \
    clouderrorreporting.googleapis.com
echo "✓ GCP APIs Enabled."

# 2. Setup Artifact Registry
echo "📦 Verifying Artifact Registry: ${REPOSITORY}..."
if ! gcloud artifacts repositories describe "${REPOSITORY}" --location="${REGION}" > /dev/null 2>&1; then
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create "${REPOSITORY}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Docker repository for MediBrief AI"
else
    echo "✓ Repository already exists."
fi

# 3. Setup Service Account (Least Privilege)
SA_NAME="medibrief-runner"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "👤 Verifying Service Account: ${SA_NAME}..."
if ! gcloud iam service-accounts describe "${SA_EMAIL}" > /dev/null 2>&1; then
    gcloud iam service-accounts create "${SA_NAME}" --display-name="MediBrief AI Runner"
    
    # Assign Roles
    ROLES=("roles/storage.objectAdmin" "roles/aiplatform.user" "roles/documentai.apiUser" "roles/logging.logWriter" "roles/cloudtrace.agent" "roles/errorreporting.writer" "roles/secretmanager.secretAccessor")
    for ROLE in "${ROLES[@]}"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="$ROLE" > /dev/null
    done
    echo "✓ Service Account created with granular roles."
else
    echo "✓ Service Account already exists."
fi

# 4. Setup GCS Bucket
BUCKET_NAME="${PROJECT_ID}-medibrief-uploads"
echo "🪣 Verifying GCS Bucket: ${BUCKET_NAME}..."
if ! gsutil ls "gs://${BUCKET_NAME}" > /dev/null 2>&1; then
    echo "Creating GCS Bucket: ${BUCKET_NAME}"
    gsutil mb -l "${REGION}" "gs://${BUCKET_NAME}"
    
    # Set auto-delete lifecycle policy (1 day) to save costs and enhance privacy
    echo '{"rule": [{"action": {"type": "Delete"}, "condition": {"age": 1}}]}' > lifecycle.json
    gsutil lifecycle set lifecycle.json "gs://${BUCKET_NAME}"
    rm lifecycle.json
    echo "✓ Bucket created with 1-day auto-delete policy."
else
    echo "✓ Bucket already exists."
fi

# 3. Build and Push Image using Cloud Build
echo "📦 Building and pushing Docker image to GCR..."
gcloud builds submit --tag "$IMAGE_TAG" .

# 4. Deploy to Cloud Run
echo "🌍 Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --service-account "${SA_EMAIL}" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GCS_BUCKET_NAME=$BUCKET_NAME"

echo "✅ Deployment Complete!"
echo "🔗 Access your app at: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)')"
