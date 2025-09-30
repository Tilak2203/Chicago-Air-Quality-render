import requests
import pandas as pd
from pymongo import MongoClient
from config import MONGODB_URI
from openaq import OpenAQ
from fetch_data import fetch_measurements, save_to_csv, latest_hourly_measurement

from config import OPENAQ_API_KEY, SENSOR_IDS
from datetime import datetime, timezone, timedelta
from preprocess_data import *

import schedule
import time


client_db = MongoClient(MONGODB_URI)

client_openaq = OpenAQ(api_key=OPENAQ_API_KEY)

def update_horly_features(df):
    
    csv_path = "../data/main_readings.csv"
    
    db = client_db["air_quality"]
    collection = db["measurements"]

    
    last_entry = collection.find_one(sort=[("timestamp", -1)])
    last_entry_db = last_entry['timestamp']
    # print(last_entry_db)
    
    df = pd.read_csv(csv_path)
    # df['timestamp'] = pd.to_datetime(df['timestamp'])
    # print(df['timestamp'].max())
    
    
    new_data = df[df['timestamp'] > last_entry_db]
    # print(new_data)
    
    if new_data.empty:
        print("No new data to update")
        return
    
    collection.insert_many(new_data.to_dict("records"))
    print(f"Inserted {len(new_data)} new rows.")
        


def update_and_push_data():
    db = client_db["air_quality"]
    collection = db["measurements"]

    last_entry = collection.find_one(sort=[("timestamp", -1)])
    # print(last_entry)
    datetime_from = last_entry['timestamp']
    
    
    if isinstance(datetime_from, str):
        datetime_from = datetime.fromisoformat(datetime_from)
        
    # datetime_from = datetime_from.date()
    datetime_from = "2025-09-29"
    print("last ts in db: ", datetime_from) 
    # datetime_to = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    datetime_to = "2025-10-01"
    print("current time: ", datetime_to)
    

    latest = fetch_measurements(
            client_openaq,
            SENSOR_IDS,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            limit=1000
        )   
    
    
    
    try:
        client_db.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

        
    if not latest.empty:
        save_to_csv(latest)
    else:
        print("No new data fetched")
    
    # latest = round_df_values(latest, decimal_places=2)
    # latest = convert_to_datetime(latest)
    # latest['timestamp'] = pd.to_datetime(latest['timestamp']).dt.tz_localize(None)

    
   
    # print(latest.tail())
    # data_dict = latest.to_dict("records")
    # print(data_dict[-1])
    

    # result = collection.insert_many(data_dict)
    # print(f"Inserted {len(result.inserted_ids)} documents into air_quality.measurements")

def update_push_latest():
    csv_path = "../data/main_readings.csv"

    db = client_db["air_quality"]
    collection = db["measurements"]

    # Get last timestamp in DB
    last_entry = collection.find_one(sort=[("timestamp", -1)])
    last_entry_db = last_entry['timestamp'] if last_entry else None

    # Read CSV (keep everything as-is)
    df = pd.read_csv(csv_path)

    # Get last timestamp from CSV
    last_entry_csv = df['timestamp'].max()

    print(f"Last in DB:  {last_entry_db}")
    print(f"Last in CSV: {last_entry_csv}")

    last_entry_db = pd.to_datetime(last_entry_db)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if last_entry_db is None:
        # If DB is empty → insert everything
        to_insert = df
    else:
        # Filter only rows newer than DB timestamp
        to_insert = df[df['timestamp'] > last_entry_db]

    if to_insert.empty:
        print("MongoDB already up-to-date. No new rows to insert.")
        return

    to_insert['timestamp'] = to_insert['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")

    collection.insert_many(to_insert.to_dict("records"))
    print(f"Inserted {len(to_insert)} new rows into MongoDB.")


def job():
    print("Scheduled job running...")
    latest_hourly_measurement(client_openaq)
    # hourly_df = latest_hourly_measurement(client_openaq)
    # print(hourly_df.tail(1))
    # update_horly_features(hourly_df)
    

    
if __name__ == "__main__":
    # update_and_push_data() #update by date range
    # update_push_latest()  #update by latest csv
    # hourly_df = latest_hourly_measurement(client_openaq) #get latest hourly data
    # print(hourly_df.head())
    # update_horly_features(hourly_df)
    
    job()
    schedule.every().hour.at(":25").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
    
    # print("Scheduled job running...")
    # latest_hourly_measurement(client_openaq)
    