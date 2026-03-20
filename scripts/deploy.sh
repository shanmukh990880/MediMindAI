#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="medibrief-ai"
REGION="us-central1"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting Deployment of MediBrief AI to Google Cloud Run..."

# 1. Enable APIs
echo "🔧 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com \
    documentai.googleapis.com \
    aiplatform.googleapis.com
echo "✓ GCP APIs Enabled."

# 2. Setup GCS Bucket for PDF Storage
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
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GCS_BUCKET_NAME=$BUCKET_NAME"

echo "✅ Deployment Complete!"
echo "🔗 Access your app at: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)')"
