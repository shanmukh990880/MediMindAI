import logging
import json
import traceback
from datetime import datetime

class GCPJSONFormatter(logging.Formatter):
    """Formats logs as JSON for Google Cloud Logging, masking PII."""
    
    def format(self, record):
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "logger": record.name
        }
        
        # Very basic PII masking logic
        msg_lower = log_entry["message"].lower()
        if "patient" in msg_lower or "ssn" in msg_lower or "dob" in msg_lower:
            log_entry["message"] = f"[REDACTED PII] Original length: {len(log_entry['message'])}"

        if record.exc_info:
            log_entry["exception"] = "".join(traceback.format_exception(*record.exc_info))
            
        return json.dumps(log_entry)

def setup_cloud_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(GCPJSONFormatter())
    
    # Optional: adjust logging levels
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)
    return root_logger
