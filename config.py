import os
import json

# Read secrets from environment variables
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# You can still keep defaults for dev (optional) but better not commit real creds
if not OPENAQ_API_KEY:
    raise ValueError("Missing OPENAQ_API_KEY environment variable")
if not MONGODB_URI:
    raise ValueError("Missing MONGODB_URI environment variable")

# Default values (safe)
DEFAULT_COORDINATES = [41.893333, -87.634176]
DEFAULT_RADIUS = 1000

# For SENSOR_IDS, store in GitHub Secrets (as JSON string or comma-separated)
# Example: {"pm1":13477544,"pm25":13477545,"rh":13477546,"temp":13477547,"pm03":13477548}
_sensor_ids_raw = os.getenv("SENSOR_IDS")

if _sensor_ids_raw:
    try:
        SENSOR_IDS = json.loads(_sensor_ids_raw)   # expects JSON
    except Exception:
        raise ValueError("SENSOR_IDS must be valid JSON")
else:
    SENSOR_IDS = {}
