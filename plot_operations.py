"""
Group No: 05
Group Memners: Boyuan Lian, Maninderjit Singh, Henil Patel
Date: 2024-11-09
"""

import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
from dbcm import DBCM

def plot_boxplot(weather_data, start_year, end_year):
    """
    Plots a box plot showing the distribution of mean temperatures for each month.
    """
    monthly_data = [[] for month in range(12)]

    for year, months in weather_data.items():
        if start_year <= year <= end_year:
            for month, temperatures in months.items():
                for temp in temperatures:
                    monthly_data[month - 1].append(temp)

    plt.figure(figsize=(10, 6))
    plt.boxplot(monthly_data, patch_artist=True)
    plt.xlabel("Month")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Monthly Temperature Distribution ({start_year} to {end_year})")
    plt.show()


def plot_lineplot(weather_data, year, month):
   """ Plots a line plot for the mean daily temperatures of a specific month and year. """
   daily_temps = []
   days = []

   for given_year in weather_data:
       if given_year == year:
           if month in weather_data[given_year]:
               for day in range(1, len(weather_data[year][month]) + 1):
                   formatted_date = f"{year}-{month:02d}-{day:02d}"
                   days.append(formatted_date)
                   daily_temps.append(weather_data[year][month][day-1])

   plt.plot(days, daily_temps, 'b-')
   plt.grid(True, color='grey', linestyle='-')
   plt.xlabel("Date")
   plt.ylabel("Avg Daily Temperature")
   plt.title("Daily Avg Temperatures")
   plt.xticks(rotation=45)
   plt.show()


if __name__ == "__main__":
    with DBCM("weather_data.db") as cursor:
      cursor.execute("SELECT  sample_date,  avg_temp FROM weather;")
      rows =  cursor.fetchall()

    weather_data = defaultdict(lambda: defaultdict(list))
    for sample_date, avg_temp in rows:
        try:
          year, month, day = map(int, sample_date.split('-'))
          weather_data[year][month].append(float(avg_temp))
        except (ValueError, TypeError):
                    continue

    plot_boxplot(weather_data, 2000, 2017)

    plot_lineplot(weather_data, 2020, 3)
