# import os

# OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "06319710ff4c0ef3acbd8058a8f529333d856419ab6819f22ccf04d002fe0430")

# MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://tilak:tilak@airquality.tcaneue.mongodb.net/?retryWrites=true&w=majority&appName=AirQuality")

# DEFAULT_COORDINATES = [41.893333, -87.634176]

# DEFAULT_RADIUS = 1000 

# SENSOR_IDS = {
#     "pm1": 13477544,
#     "pm25": 13477545,
#     "rh": 13477546,
#     "temp": 13477547,
#     "pm03": 13477548,
# }

# config.py
import os
from ast import literal_eval

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb+srv://tilak:tilak@airquality.tcaneue.mongodb.net/?retryWrites=true&w=majority&appName=AirQuality")
OPENAQ_API_KEY = os.environ.get("OPENAQ_API_KEY", "06319710ff4c0ef3acbd8058a8f529333d856419ab6819f22ccf04d002fe0430")
# store SENSOR_IDS as comma-separated string in secrets; split to list here:
SENSOR_IDS = os.environ.get("SENSOR_IDS", "")
if SENSOR_IDS:
    # either comma separated or a JSON list string; try both
    try:
        SENSOR_IDS = literal_eval(SENSOR_IDS) if (SENSOR_IDS.strip().startswith('[')) else [s.strip() for s in SENSOR_IDS.split(',')]
    except Exception:
        SENSOR_IDS = [s.strip() for s in SENSOR_IDS.split(',')]
else:
    SENSOR_IDS = []

