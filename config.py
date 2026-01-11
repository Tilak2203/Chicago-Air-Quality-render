import os

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "Update this with your actual OPENAQ API")

MONGODB_URI = os.getenv("MONGODB_URI", "Update this with your actual db URI")

DEFAULT_COORDINATES = [41.893333, -87.634176]

DEFAULT_RADIUS = 1000 

SENSOR_IDS = {
    "pm1": 13477544,
    "pm25": 13477545,
    "rh": 13477546,
    "temp": 13477547,
    "pm03": 13477548,
}

# # config.py
# import os
# import json

# # MongoDB and API key
# MONGODB_URI = os.environ.get("MONGODB_URI")
# OPENAQ_API_KEY = os.environ.get("OPENAQ_API_KEY")

# # Default values
# DEFAULT_COORDINATES = json.loads(os.environ.get("DEFAULT_COORDINATES", "[41.893333, -87.634176]"))
# DEFAULT_RADIUS = int(os.environ.get("DEFAULT_RADIUS", "1000"))

# # Sensor IDs (stored as JSON in env variable)
# SENSOR_IDS = json.loads(os.environ.get("SENSOR_IDS", "{}"))


