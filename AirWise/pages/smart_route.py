import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import polyline
import numpy as np

# ====== CONFIG ======
ORS_API_KEY = "5b3ce3597851110001cf62489476576b460f4003a08c26489ec7631e"
OPENAQ_API_URL = "https://api.openaq.org/v2/latest"
MUMBAI_BOUNDS = [[18.89, 72.77], [19.35, 72.98]]  # Bounding box for Mumbai

st.set_page_config(page_title="Smart Route", layout="wide")
st.title("🧠 Smart AQI Route Finder")

# ====== INPUT FIELDS ======
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("📍 Start Location", "Dadar Station, Mumbai")
with col2:
    destination = st.text_input("🏁 End Location", "Bandra Kurla Complex, Mumbai")

mode = st.selectbox("🚶 Choose Travel Mode", ["driving-car", "foot-walking"])

# ====== GEOCODING ======
@st.cache_data(show_spinner=False)
def geocode(place):
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/search?q={place}&format=json&limit=1&countrycodes=in")
        data = res.json()
        if data:
            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
            return lat, lon
    except:
        return None
    return None

# ====== AQI FETCHING ======
def get_aqi(lat, lon):
    try:
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": 5000,
            "limit": 1,
            "parameter": "pm25"
        }
        res = requests.get(OPENAQ_API_URL, params=params)
        data = res.json()
        if data["results"]:
            return data["results"][0]["measurements"][0]["value"]
    except:
        return None
    return None

# ====== ROUTE CALCULATION ======
def get_route(start, end, mode):
    url = f"https://api.openrouteservice.org/v2/directions/{mode}/geojson"
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [[start[1], start[0]], [end[1], end[0]]]
    }
    res = requests.post(url, headers=headers, json=body)
    return res.json()

# ====== ROUTE AQI & COLOR ======
def analyze_route(route_coords):
    sampled = route_coords[::max(1, len(route_coords) // 10)]
    aqis = []
    for lat, lon in sampled:
        aqi = get_aqi(lat, lon)
        if aqi is not None:
            aqis.append(aqi)
    if aqis:
        avg_aqi = round(np.mean(aqis), 1)
        if avg_aqi <= 50:
            color = "green"
        elif avg_aqi <= 100:
            color = "orange"
        else:
            color = "red"
        return avg_aqi, color
    return None, "gray"

# ====== MAIN BUTTON ======
if st.button("🧭 Find Smartest Route"):
    start_coords = geocode(origin)
    end_coords = geocode(destination)

    if not start_coords or not end_coords:
        st.error("❌ Could not locate one or both places. Try typing better or clicking the map.")
    else:
        try:
            route = get_route(start_coords, end_coords, mode)
            coords = [(pt[1], pt[0]) for pt in route["features"][0]["geometry"]["coordinates"]]
            duration_sec = route["features"][0]["properties"]["summary"]["duration"]

            avg_aqi, color = analyze_route(coords)

            fmap = folium.Map(location=start_coords, zoom_start=13, tiles="CartoDB positron")
            folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color="green")).add_to(fmap)
            folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color="red")).add_to(fmap)
            folium.PolyLine(coords, color=color, weight=6).add_to(fmap)

            st_folium(fmap, width=1100, height=600)

            mins = int(duration_sec // 60)
            st.success(f"✅ Route found: ~{mins} minutes | Avg AQI: {avg_aqi if avg_aqi else 'Unknown'}")

        except Exception as e:
            st.error("Something went wrong while fetching the route.")
            st.exception(e)
