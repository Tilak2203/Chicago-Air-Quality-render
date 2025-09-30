from openaq import OpenAQ
import pandas as pd
from config import OPENAQ_API_KEY, MONGODB_URI, DEFAULT_COORDINATES, DEFAULT_RADIUS, SENSOR_IDS
import os
from datetime import datetime, timezone
from preprocess_data import *
from config import SENSOR_IDS


from pymongo import MongoClient
from openaq import OpenAQ



client_db = MongoClient(MONGODB_URI)

client_openaq = OpenAQ(api_key=OPENAQ_API_KEY)

def fetch_locations(client, coordinates, radius):
    locations = client.locations.list(coordinates=coordinates, radius=radius)
    print("Nearby locations: ")
    for loc in locations.results:
        print(f"- {loc.name} (ID: {loc.id}) at {loc.coordinates}")
    return [loc.id for loc in locations.results]

def fetch_measurements(client, sensor_ids, datetime_from, datetime_to, limit):
    all_data = {}
    
    # Fetch new data from API
    for param, sensor_id in sensor_ids.items():
        reading = client.measurements.list(
            sensors_id=sensor_id,
            limit=limit,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
        # print(reading)
        for m in reading.results:
            timestamp = m.period.datetime_from.utc
            value = m.value
            if timestamp not in all_data:
                all_data[timestamp] = {}
            all_data[timestamp][param] = value
    
    # Convert new data to DataFrame        
    new_df = pd.DataFrame.from_dict(all_data, orient='index')
    new_df.index.name = 'timestamp'
    new_df.rename(columns={
        'pm1': 'pm1 (µg/m³)',
        'pm25': 'pm25 (µg/m³)',
        'rh': 'Relative Humidity (%)',
        'temp': 'Temperature (c)',
        'pm03': 'pm03 (µg/m³)'
    }, inplace=True)
    
    new_df.reset_index(inplace=True)
    
    return new_df

    
def latest_hourly_measurement(client):
    
    location_id = 4903652
    
    response = client.locations.latest(location_id)
    
    sensor_readings = {}
    
    for item in response.results:
        # local = item.datetime['utc']
        # print(item.sensors_id, item.value, local)
        sid = item.sensors_id
        value = item.value
        sensor_readings[sid] = value
        
    utc = item.datetime["utc"]
    utc = datetime.fromisoformat(utc)
    # print(sensor_readings, utc)   
    
    pm1_id = 13477544
    pm25_id = 13477545
    rh_id = 13477546
    temp_id = 13477547
    pm03_id = 13477548 
    
    df = pd.DataFrame([{
        "timestamp": utc,
        "pm1 (µg/m³)": sensor_readings.get(pm1_id, None),
        "pm25 (µg/m³)": sensor_readings.get(pm25_id, None),
        "Relative Humidity (%)": sensor_readings.get(rh_id, None),
        "Temperature (c)": sensor_readings.get(temp_id, None),
        "pm03 (µg/m³)": sensor_readings.get(pm03_id, None),
        "hour": utc.hour,
        "day_of_week": utc.weekday(),
        "month": utc.month
    }])
    
    # print(df.head())
    # print("inside latest_hourly_measurement")
    # save_to_csv(df)
    # print("done saving to csv")
    # return df
    db = client_db["air_quality"]
    collection = db["measurements"]
    
    last_entry = collection.find_one(sort=[("timestamp", -1)])
    last_entry_db = last_entry['timestamp']
    # print(f"Last in DB:  {last_entry_db}")
    
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

    
    df = round_df_values(df, decimal_places=2)
    df = convert_to_datetime(df)
    # print(df)
    
    
    new_data = df[df['timestamp'] > last_entry_db]
    
    # print(new_data)
    
    new_data['timestamp'] = pd.to_datetime(new_data['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")

    
    if new_data.empty:
        print("No new data to update")
        return
    
    collection.insert_many(new_data.to_dict("records"))
    print(f"Inserted {len(new_data)} new rows.")
    
    

    

    

    

if __name__ == "__main__":
    client = OpenAQ(api_key=OPENAQ_API_KEY)

    # # Optional: Clean existing CSV first
    # remove_csv_duplicates()

    # Fetch new data
    datetime_to = datetime.now().strftime("%Y-%m-%d")
    df = fetch_measurements(
        client,
        SENSOR_IDS,
        datetime_from="2025-08-20",
        datetime_to="2025-08-29",
        limit=1000
    )
    
    if not df.empty:
        save_to_csv(df)
    else:
        print("No new data fetched")
    
    # latest_hourly_df = latest_hourly_measurement(client)
    
    # if not latest_hourly_df.empty:
    #     save_to_csv(latest_hourly_df)
    # else:
    #     print("No new data fetched")
    
    
    
    