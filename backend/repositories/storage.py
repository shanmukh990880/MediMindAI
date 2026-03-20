import datetime
from google.cloud import storage
import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)

class CloudStorageRepository:
    def __init__(self):
        try:
            self.client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
            self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME) if settings.GCS_BUCKET_NAME else None
        except Exception as e:
            logger.warning(f"Could not initialize GCS Client: {e}")
            self.bucket = None

    async def upload_pdf(self, file_content: bytes, destination_blob_name: str) -> str:
        """Uploads a file to the bucket and returns the GCS URI."""
        if not self.bucket:
            logger.warning("GCS_BUCKET_NAME not set or auth failed. Skipping upload.")
            return ""

        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(file_content, content_type="application/pdf")
        
        uri = f"gs://{settings.GCS_BUCKET_NAME}/{destination_blob_name}"
        logger.info(f"File successfully uploaded to {uri}")
        return uri

    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 15) -> str:
        """Generates a signed URL for reading the PDF directly from frontend."""
        if not self.bucket:
            return ""
            
        try:
            blob = self.bucket.blob(blob_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=expiration_minutes),
                method="GET",
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            return ""
