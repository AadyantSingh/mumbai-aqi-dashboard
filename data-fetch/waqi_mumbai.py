import requests
import csv

API_TOKEN = "edbe9b9237790529d9d47599413aa7a819bdc75c"

# List of station IDs or city names in Mumbai
# WAQI stations have numeric IDs or you can query by city name like 'kurla', 'bandra', etc.
# For demo, using city names (make sure these work with WAQI API)
locations = ["kurla", "bandra", "colaba", "powai", "thane"]

# CSV file where data will be saved
csv_file = "mumbai_aqi_data.csv"

# Define headers for CSV
headers = [
    "location",
    "aqi",
    "dominant_pollutant",
    "co",
    "dew",
    "humidity",
    "no2",
    "o3",
    "pressure",
    "pm10",
    "pm25",
    "so2",
    "temperature",
    "wind_speed",
    "wind_gust"
]

# Open CSV file and write headers
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    for loc in locations:
        url = f"https://api.waqi.info/feed/{loc}/?token={API_TOKEN}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "ok":
            d = data["data"]
            iaqi = d.get("iaqi", {})

            row = [
                d.get("city", {}).get("name", loc),
                d.get("aqi", "N/A"),
                d.get("dominentpol", "N/A"),
                iaqi.get("co", {}).get("v", "N/A"),
                iaqi.get("dew", {}).get("v", "N/A"),
                iaqi.get("h", {}).get("v", "N/A"),
                iaqi.get("no2", {}).get("v", "N/A"),
                iaqi.get("o3", {}).get("v", "N/A"),
                iaqi.get("p", {}).get("v", "N/A"),
                iaqi.get("pm10", {}).get("v", "N/A"),
                iaqi.get("pm25", {}).get("v", "N/A"),
                iaqi.get("so2", {}).get("v", "N/A"),
                iaqi.get("t", {}).get("v", "N/A"),
                iaqi.get("w", {}).get("v", "N/A"),
                iaqi.get("wg", {}).get("v", "N/A")
            ]

            writer.writerow(row)
            print(f"Saved data for {loc}")

        else:
            print(f"Failed to get data for {loc}: {data.get('data', 'No details')}")

print(f"Data saved to {csv_file}")
