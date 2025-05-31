import os
import subprocess
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime, date
import pandas as pd
from appURLs import appURLs
import pytz
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# Timestamp and Date
mountain = pytz.timezone('US/Mountain')
timestamp = datetime.now(mountain)
current_date = timestamp.date()  # This is already a date object

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', <'ENTER DATABASE URL HERE'>)

def alter_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("""
    ALTER TABLE app_stats ADD COLUMN IF NOT EXISTS android_detailed_app_rating FLOAT;
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_app_stats(df):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    # Create table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_stats (
        id SERIAL PRIMARY KEY,
        date DATE,
        app_name TEXT,
        ios_app_rating FLOAT,
        ios_total_reviews INTEGER,
        ios_app_rank INTEGER,
        android_detailed_app_rating FLOAT,
        android_app_rating FLOAT,
        android_total_reviews INTEGER,
        overall_app_rating FLOAT,
        combined_total_reviews INTEGER,
        timestamp TIMESTAMP WITH TIME ZONE,
        UNIQUE (date, app_name),
        ios_rating_rank INTEGER,
        android_rating_rank INTEGER,
        overall_rating_rank INTEGER
    )
    """)

    # Convert DataFrame to list of tuples
    values = df.apply(lambda row: (
        row['Date'],
        row['App Name'],
        round(float(row['iOS App Rating']), 2) if pd.notnull(row['iOS App Rating']) else None,
        int(row['iOS Total Reviews']) if pd.notnull(row['iOS Total Reviews']) else None,
        int(row['iOS App Rank']) if pd.notnull(row['iOS App Rank']) else None,
        round(float(row['Android Detailed App Rating']), 13) if pd.notnull(row['Android Detailed App Rating']) else None,
        round(float(row['Android App Rating']), 1) if pd.notnull(row['Android App Rating']) else None,
        int(row['Android Total Reviews']) if pd.notnull(row['Android Total Reviews']) else None,
        round(float(row['Overall App Rating']), 2) if pd.notnull(row['Overall App Rating']) else None,
        int(row['Combined Total Reviews']) if pd.notnull(row['Combined Total Reviews']) else None,
        row['Timestamp'],
        int(row['iOS Rating Rank']) if pd.notnull(row['iOS Rating Rank']) else None,
        int(row['Android Rating Rank']) if pd.notnull(row['Android Rating Rank']) else None,
        int(row['Overall Rating Rank']) if pd.notnull(row['Overall Rating Rank']) else None
    ), axis=1).tolist()

    # Insert data
    execute_values(cur, """
    INSERT INTO app_stats (date, app_name, ios_app_rating, ios_total_reviews, ios_app_rank, 
                           android_detailed_app_rating, android_app_rating, android_total_reviews, 
                           overall_app_rating, combined_total_reviews, timestamp, ios_rating_rank, android_rating_rank, overall_rating_rank)
    VALUES %s
    ON CONFLICT (date, app_name) DO UPDATE SET
        ios_app_rating = EXCLUDED.ios_app_rating,
        ios_total_reviews = EXCLUDED.ios_total_reviews,
        ios_app_rank = EXCLUDED.ios_app_rank,
        android_detailed_app_rating = EXCLUDED.android_detailed_app_rating,
        android_app_rating = EXCLUDED.android_app_rating,
        android_total_reviews = EXCLUDED.android_total_reviews,
        overall_app_rating = EXCLUDED.overall_app_rating,
        combined_total_reviews = EXCLUDED.combined_total_reviews,
        timestamp = EXCLUDED.timestamp,
        ios_rating_rank = EXCLUDED.ios_rating_rank,
        android_rating_rank = EXCLUDED.android_rating_rank,
        overall_rating_rank = EXCLUDED.overall_rating_rank
    """, values)

    conn.commit()
    cur.close()
    conn.close()

# Call the alter_table function to ensure the column exists
alter_table()

# Scrape Android Data
data = []
# Retrieve list of Android URLs
androidURLs = [appURLs[apps]["android"] for apps in appURLs]
# Create a reverse mapping from Android URLs to the corresponding app name
androidURLNameMapping = {appURLs[app]["android"]: app for app in appURLs}
# Loop through all Android URLs
for url in androidURLs:
    result = requests.get(url)
    parse = BeautifulSoup(result.content, "lxml")
    # App Name
    appName = androidURLNameMapping.get(url)
    # Retrieve and parse JSON
    json_element = parse.find(type="application/ld+json")
    if json_element is not None:
        script = json_element.text.strip()
        dataJSON = json.loads(script)
        # Star Rating
        aggregateRating = dataJSON.get("aggregateRating")
        if aggregateRating is not None:
            starRatingDetail = aggregateRating.get("ratingValue")
            starRatingOfficial = float(aggregateRating.get("ratingValue"))
        else:
            starRatingDetail = "Not Available"
            starRatingOfficial = "Not Available"
        # Total Reviews
        if aggregateRating is not None:
            totalReviews = aggregateRating.get("ratingCount")
        else:
            totalReviews = "Not Available"
        # App Category
        appCategory = dataJSON.get("applicationCategory", "Not Available")

        # Append scraped data for each app
        data.append(
            {
                "Date": current_date,
                "App Name": appName,
                "Android Detailed App Rating": round(starRatingOfficial, 13),
                "Android Total Reviews": totalReviews,
                "Android App Category": appCategory,
                "Timestamp": timestamp,
            },
        )
    else:
        # Handle the case when the JSON element is not found
        data.append(
            {
                "Date": current_date,
                "App Name": appName,
                "Android Detailed App Rating": "Not Available",
                "Android Total Reviews": "Not Available",
                "Android App Category": "Not Available",
                "Timestamp": timestamp,
            },
        )
        continue

# Convert to Dataframe
dataAndroid = pd.DataFrame(data)

# Scrape iOS Data
data = []
# Retrieve list of iOS URLs
iosURLS = [appURLs[apps]["ios"] for apps in appURLs]
# Create a reverse mapping from iOS URLs to the corresponding app name
iosURLNameMapping = {appURLs[app]["ios"]: app for app in appURLs}
# Loop through all iOS URLs
for url in iosURLS:
    result = requests.get(url)
    parse = BeautifulSoup(result.content, "lxml")
    # App Name
    appName = iosURLNameMapping.get(url)
    # Retrieve and parse JSON
    json_element = parse.find(type="application/ld+json")
    if json_element is not None:
        script = json_element.text.strip()
        dataJSON = json.loads(script)
        # Star Rating
        aggregateRating = dataJSON.get("aggregateRating")
        if aggregateRating is not None:
            starRatingOfficial = aggregateRating.get("ratingValue")
        else:
            starRatingOfficial = "Not Available"
        # Total Reviews
        if aggregateRating is not None:
            totalReviews = aggregateRating.get("reviewCount")
        else:
            totalReviews = "Not Available"
        # App Store Category Rank
        rank_element = parse.find("a", {"class": "inline-list__item"})
        rank = None
        if rank_element is not None:
            rank_text = rank_element.text.strip().split()[0]
            rank = int(rank_text.replace(",", "").replace("#", ""))
        # App Category
        appCategory = dataJSON.get("applicationCategory", "Not Available")
        # Append scraped data for each app
        data.append(
            {
                "Date": current_date,
                "App Name": appName,
                "iOS App Rating": starRatingOfficial,
                "iOS Total Reviews": totalReviews,
                "iOS App Rank": rank,
                "iOS App Category": appCategory,
                "Timestamp": timestamp,
            },
        )
    else:
        # Handle the case when the JSON element is not found
        data.append(
            {
                "Date": current_date,
                "App Name": appName,
                "iOS App Rating": "Not Available",
                "iOS Total Reviews": "Not Available",
                "iOS App Rank": "Not Available",
                "iOS App Category": "Not Available",
                "Timestamp": timestamp,
            },
        )
        continue

# Convert to Dataframe
dataIos = pd.DataFrame(data)

# Merge and process data
dataAndroidTemp = dataAndroid.copy()
dataAndroidTemp["App Name"] = dataIos["App Name"]
combinedData = pd.merge(dataIos, dataAndroidTemp, on="App Name", how="inner")

combinedData = combinedData.drop(
    [
        "Timestamp_x",
        "Date_y",
        "Android App Category",
        "iOS App Category",
    ],
    axis=1,
)

combinedData = combinedData.rename(
    columns={"Timestamp_y": "Timestamp", "Date_x": "Date"}
)

combinedData['iOS App Rating'] = pd.to_numeric(combinedData['iOS App Rating'], errors='coerce')
combinedData['Android Detailed App Rating'] = pd.to_numeric(combinedData['Android Detailed App Rating'], errors='coerce')
# Create new column android_app_rating by rounding android_detailed_app_rating to one decimal place
combinedData['Android App Rating'] = pd.to_numeric(combinedData['Android Detailed App Rating'].round(1)).fillna(0).astype(float)
combinedData['Overall App Rating'] = pd.to_numeric(combinedData[['iOS App Rating', 'Android App Rating']].mean(axis=1).round(2)).fillna(0).astype(float)

combinedData['Android Total Reviews'] = pd.to_numeric(combinedData['Android Total Reviews'], errors='coerce').fillna(0).astype(int)
combinedData['iOS Total Reviews'] = pd.to_numeric(combinedData['iOS Total Reviews'], errors='coerce').fillna(0).astype(int)
combinedData['Combined Total Reviews'] = combinedData['Android Total Reviews'] + combinedData['iOS Total Reviews']

combinedData['Overall Rating Rank'] = combinedData['Overall App Rating'].rank(ascending=False, method='min').astype(int)
combinedData['iOS Rating Rank'] = combinedData['iOS App Rating'].rank(ascending=False, method='min').astype(int)
combinedData['Android Rating Rank'] = combinedData['Android App Rating'].rank(ascending=False, method='min').astype(int)

# The following line is no longer needed as we're using a date object from the start
# combinedData['Date'] = pd.to_datetime(combinedData['Date']).dt.date

# Insert data into PostgreSQL
insert_app_stats(combinedData)

# You can still keep the JSON export if needed
combinedData.to_json("dataDetailed.json", orient='records')

print("Data scraping and database insertion completed successfully.")