import requests

# Replace 'your_api_token' with the token you received
API_TOKEN = 'edbe9b9237790529d9d47599413aa7a819bdc75c'
CITY = 'mumbai'
API_URL = f'https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}'

response = requests.get(API_URL)
data = response.json()

if data['status'] == 'ok':
    aqi = data['data']['aqi']
    print(f"The current AQI in {CITY.title()} is {aqi}.")
else:
    print(f"Error fetching data: {data.get('data')}")