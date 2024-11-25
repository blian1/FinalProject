"""
Group No: 05
Group Members: Boyuan Lian, Maninderjit Singh, Henil Patel
Date: 2024-11-15
"""

from scrape_weather import WeatherScraper
from db_operations import DBOperations
from plot_operations import plot_boxplot, plot_lineplot
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta



class WeatherProcessor:
    def __init__(self):
        self.base_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Day=1"
        self.scraper = WeatherScraper(self.base_url)
        self.db = DBOperations()

    def display_menu(self):
        print("\n====== Weather Data Processing Application ======")
        print("1. Download Full Weather Data")
        print("2. Update Weather Data in Database")
        print("3. Generate Box Plot (Enter Year Range)")
        print("4. Generate Line Plot (Enter Specific Year and Month)")
        print("5. Exit")
        return input("Enter your choice: ")

    def download_full_data(self):
      """Download full weather data and export it as an Excel file."""

      try:
          # Fetch all data from the database
          data = self.db.fetch_data()
          if data:
              print("Fetching data from the database...")
              # Format the data for export
              df = pd.DataFrame(data, columns=["Date", "Location", "Max Temp", "Min Temp", "Mean Temp"])
          else:
              print("Database is empty. Scraping full weather data...")
              # Scrape data if the database is empty
              start_Date = datetime(2024, 1, 1)
              end_Date = datetime(2024, 12, 31)
              weather_data = self.scraper.scrape_weather()
              formatted_data = [
                  (date, "Winnipeg", temps["Max"], temps["Min"], temps["Mean"])
                  for date, temps in weather_data.items()
              ]
              # Save the scraped data to the database
              self.db.initialize_db()
              self.db.save_data(formatted_data)
              # Format the data for export
              df = pd.DataFrame(formatted_data, columns=["Date", "Location", "Max Temp", "Min Temp", "Mean Temp"])

          # Save the data as an Excel file
          output_file = "Weather_Data.xlsx"
          df.to_excel(output_file, index=False, engine="openpyxl")
          print(f"Weather data exported to {output_file}.")
      except Exception as e:
          print(f"An error occurred while processing data: {e}")


    def update_data(self):
        """
        Check the database for the latest weather data and update it with new entries
        if data for recent dates is missing.
        """
        try:
            print("Checking and updating weather data in the database...")
            self.db.initialize_db()

            # Fetch the latest date from the database
            latest_date = self.db.fetch_latest_date()
            today = datetime.now().date()

            # Ensure latest_date is a datetime.date object
            if latest_date:
                if isinstance(latest_date, str):
                    latest_date = datetime.strptime(latest_date, "%Y-%m-%d").date()
                if latest_date >= today - timedelta(days=1):
                    print("Database is already up to date. No update required.")
                    return
                # Set start_date to the day after the latest date in the database
                start_date = latest_date + timedelta(days=1)
            else:
                print("Database is empty. Starting from the earliest available data.")
                start_date = today  # Start from today if the database is empty

            # Fetch new weather data from start_date to today
            new_weather_data = self.scraper.update_weather_data(start_date=start_date, end_date=today)

            # Ensure all keys in new_weather_data are converted to datetime.date
            formatted_data = []
            for date, temps in new_weather_data.items():
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                elif isinstance(date, datetime):
                    date_obj = date.date()
                else:
                    date_obj = date  # Assume already datetime.date

                formatted_data.append(
                    (date_obj.strftime("%Y-%m-%d"), "Winnipeg", temps["Max"], temps["Min"], temps["Mean"])
                )

            # Save the new data to the database
            self.db.save_data(formatted_data)
            print("Database updated successfully!")
        except Exception as e:
            print(f"An error occurred while updating data: {e}")









    def generate_boxplot(self):
        """Generate a box plot for the specified year range."""
        try:
            start_year = int(input("Enter start year: "))
            end_year = int(input("Enter end year: "))
            if start_year > end_year:
                print("Start year cannot be greater than end year. Please try again.")
                return

            data = self.db.fetch_data()
            weather_data = self.format_data_for_plotting(data)
            plot_boxplot(weather_data, start_year, end_year)
        except Exception as e:
            print(f"An error occurred while generating the box plot: {e}")

    def generate_lineplot(self):
        """Generate a line plot for a specific year and month."""
        try:
            year = int(input("Enter year: "))
            month = int(input("Enter month (1-12): "))
            if not (1 <= month <= 12):
                print("Invalid month. Please enter a number between 1 and 12.")
                return

            data = self.db.fetch_data()
            weather_data = self.format_data_for_plotting(data)
            plot_lineplot(weather_data, year, month)
        except Exception as e:
            print(f"An error occurred while generating the line plot: {e}")

    def format_data_for_plotting(self, data):
        """Format database data into a nested dictionary structure for plotting."""
        from collections import defaultdict
        weather_data = defaultdict(lambda: defaultdict(list))
        for sample_date, location, max_temp, min_temp, avg_temp in data:
            try:
                year, month, _ = map(int, sample_date.split('-'))
                weather_data[year][month].append(avg_temp)
            except ValueError:
                continue
        return weather_data

    def run(self):
        """Run the weather processing application."""
        print("Weather Processor started.")
        while True:
            print("\n====== Weather Data Processing Application ======")
            print("1. Download Full Weather Data")
            print("2. Update Weather Data in Database")
            print("3. Generate Box Plot (Enter Year Range)")
            print("4. Generate Line Plot (Enter Specific Year and Month)")
            print("5. Exit")
            print("10. Purge Database")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.download_full_data()
            elif choice == "2":
                self.update_data()
            elif choice == "3":
                self.generate_boxplot()
            elif choice == "4":
                self.generate_lineplot()
            elif choice == "10":
                self.purge_database()
            elif choice == "5":
                print("Thank you for using the Weather Data Processing Application. Goodbye!")
                break
            else:
                print("Invalid input. Please try again.")


    def purge_database(self):
        """Clear all data from the database."""
        try:
            self.db.purge_data()
            print("Database purged successfully!")
        except Exception as e:
            print(f"An error occurred while purging the database: {e}")


if __name__ == "__main__":
    try:
        processor = WeatherProcessor()
        processor.run()
    except Exception as e:
        print(f"An error occurred: {e}")
