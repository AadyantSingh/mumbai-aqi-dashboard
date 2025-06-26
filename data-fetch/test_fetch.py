import requests

API_KEY = "d6835784818013e7f627251015c30e66171334dc47c87396b9e147316bb82ec4"

url = "https://api.openaq.org/v3/latest"
headers = {
    "X-API-Key": API_KEY
}
params = {
    "coordinates": "19.0760,72.8777",  # Mumbai city center
    "radius": 25000,  # Maximum allowed radius
    "limit": 100
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    results = response.json().get('results', [])
    if results:
        for station in results:
            print(f"\n📍 Location: {station['location']} ({station['coordinates']['latitude']}, {station['coordinates']['longitude']})")
            for m in station['measurements']:
                print(f"🧪 {m['parameter']} = {m['value']} {m['unit']} (Last updated: {m['lastUpdated']})")
    else:
        print("⚠️ No measurement data found.")
else:
    print(f"❌ Failed to fetch data. Status code: {response.status_code}")
    print(response.text)
