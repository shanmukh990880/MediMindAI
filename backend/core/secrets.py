from google.cloud import secretmanager
import os
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Fetches a secret from Google Secret Manager.
    Falls back to environment variable if Secret Manager is not configured locally.
    """
    env_val = os.environ.get(secret_id)
    if env_val:
        return env_val

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.warning(f"GOOGLE_CLOUD_PROJECT not set, cannot fetch secret {secret_id} from GCP.")
        return ""

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"Successfully retrieved secret {secret_id} from Secret Manager.")
        return secret_value
    except Exception as e:
        logger.error(f"Failed to access secret {secret_id}: {e}")
        return ""
