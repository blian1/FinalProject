"""
Group No: 05
Group Memners: Boyuan Lian, Maninderjit Singh, Henil Patel
Date: 2024-11-09
"""

import sqlite3
from dbcm import DBCM
from scrape_weather import WeatherScraper
from datetime import datetime, timedelta

class DBOperations:
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name

    def initialize_db(self):
        """Initialize the database, creating the required table if it doesn't exist."""
        with DBCM(self.db_name) as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sample_date TEXT NOT NULL,
                        location TEXT NOT NULL,
                        max_temp REAL,
                        min_temp REAL,
                        avg_temp REAL
                    );
                """)
            except sqlite3.Error as e:
                print(f"Error initializing database: {e}")

    def save_data(self, data):
        """Save weather data entries to the Database."""
        with DBCM(self.db_name) as cursor:
            try:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather (
                        sample_date TEXT NOT NULL,
                        location TEXT NOT NULL,
                        max_temp REAL,
                        min_temp REAL,
                        avg_temp REAL,
                        PRIMARY KEY (sample_date, location)
                    );
                """)

                cursor.executemany("""
                    INSERT OR IGNORE INTO weather (sample_date, location, max_temp, min_temp, avg_temp)
                    VALUES (?, ?, ?, ?, ?);
                """, data)

            except sqlite3.Error as e:
                print(f"Error saving data: {e}")


    def fetch_data(self):
        """Fetch all weather data from the database."""
        with DBCM(self.db_name) as cursor:
            try:
                cursor.execute("SELECT sample_date, location, max_temp, min_temp, avg_temp FROM weather;")
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return []


    def purge_data(self):
        """Purge all data from the database."""
        with DBCM(self.db_name) as cursor:
            try:
                cursor.execute("DELETE FROM weather;")
            except sqlite3.Error as e:
                print(f"Error purging data: {e}")

    def fetch_latest_date(self):
        """Fetch the latest date from the database."""
        with DBCM(self.db_name) as cursor:
            try:
                cursor.execute("SELECT MAX(sample_date) FROM weather;")
                result = cursor.fetchone()
                if result and result[0]:  # Ensure result is not None
                    # Convert the string to datetime.date
                    return datetime.strptime(result[0], "%Y-%m-%d").date()
                return None
            except sqlite3.Error as e:
                print(f"Error fetching latest date: {e}")
                return None




if __name__ == "__main__":
    """ Code to integrate Weather Scraper and DB Operations """
    base_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Day=1"
    scraper = WeatherScraper(base_url)
    db_operations = DBOperations()

    db_operations.initialize_db()

    # Scraping weather data
    weather = scraper.scrape_weather()

    # Prepare data for saving into the database
    weather_data = []
    for date, temps in weather.items():
        # Append date, city (hardcoded as "Winnipeg"), and the temperature data
        weather_data.append((date, "Winnipeg", temps["Max"], temps["Min"], temps["Mean"]))

    # Save data to the database
    db_operations.save_data(weather_data)

    # To see output
    data = db_operations.fetch_data()
    for row in data:
        print(row)
