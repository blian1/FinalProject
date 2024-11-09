# scrape_weather.py
from html.parser import HTMLParser
import requests
from datetime import datetime
import time
import re

class WeatherScraper(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.weather_data = {}
        self.current_date = None
        self.in_temp_data = False
        self.current_row = []
        self.collect_data = False

    def handle_starttag(self, tag, attrs):
        if tag == "td" or tag == "th":
            self.collect_data = True

    def handle_data(self, data):
        if self.collect_data:
            data = data.strip()
            if data:
                self.current_row.append(data)
            self.collect_data = False

    def handle_endtag(self, tag):
        if tag == "tr" and len(self.current_row) >= 4:
            if "Sum" not in self.current_row and "Avg" not in self.current_row and "Xtrm" not in self.current_row:
                try:
                    day = self.current_row[0]
                    if day.isdigit():
                        self.current_date = f"{self.year}-{self.month:02d}-{int(day):02d}"
                        max_temp = float(self.current_row[1])
                        min_temp = float(self.current_row[2])
                        mean_temp = float(self.current_row[3])

                        self.weather_data[self.current_date] = {
                            "Max": max_temp, "Min": min_temp, "Mean": mean_temp
                        }
                        print(f"Added data for {self.current_date}: {self.weather_data[self.current_date]}")
                except (ValueError, IndexError):
                    print(f"Invalid data for row: {self.current_row}")
            self.current_row = []

    def scrape_weather(self):
        today = datetime.now()
        #self.year = today.year
        #self.month = today.month

        self.year = 1996 ############# Here is a test use 1996-12 as begin date , get all data please use self.year = today.year,#self.month = today.month
        self.month = 12 ############

        while True:
            print(f"Scraping data for {self.year}-{self.month:02d}...")
            url = f"{self.base_url}&Year={self.year}&Month={self.month}"

            for attempt in range(3):  # Try up to 3 times
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    # Check the page title to verify that the data is for the requested month and year
                    title_match = re.search(r'<h1 property="name" id="wb-cont">Daily Data Report for (.*?)</h1>', response.text)
                    if title_match:
                        report_date = title_match.group(1).strip()
                        if f"{datetime(self.year, self.month, 1):%B %Y}" not in report_date:
                            print(f"No data available for {self.year}-{self.month:02d}. Stopping.")
                            return self.weather_data

                    self.feed(response.text)
                    print(f"Data successfully retrieved for {self.year}-{self.month:02d}.")
                    break
                except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                    print(f"Attempt {attempt + 1} failed for {self.year}-{self.month:02d}: {e}")
                    time.sleep(5)
            else:
                print(f"Failed to retrieve data for {self.year}-{self.month:02d} after multiple attempts. Skipping.")
                break

            # Move to the previous month
            if self.month == 1:
                self.month = 12
                self.year -= 1
            else:
                self.month -= 1

            if self.year < 1840:
                print("Reached the earliest available year. Stopping.")
                break

        return self.weather_data


if __name__ == "__main__":
    base_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Day=1"
    scraper = WeatherScraper(base_url)
    weather_data = scraper.scrape_weather()
    print(weather_data)
