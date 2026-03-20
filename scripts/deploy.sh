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
    documentai.googleapis.com \
    aiplatform.googleapis.com

# 2. Build and Push Image using Cloud Build
echo "📦 Building and pushing Docker image to GCR..."
gcloud builds submit --tag "$IMAGE_TAG" .

# 3. Deploy to Cloud Run
echo "🌍 Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION"

echo "✅ Deployment Complete!"
echo "🔗 Access your app at: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)')"
