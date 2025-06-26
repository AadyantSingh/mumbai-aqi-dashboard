#.venv\Scripts\activate
#streamlit run AirWise/pages/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_folium import st_folium
import folium
from datetime import datetime

# ------------------ Config ------------------ #

st.set_page_config(page_title="Mumbai AQI Dashboard", layout="wide")

API_TOKEN = "edbe9b9237790529d9d47599413aa7a819bdc75c"

station_coords = {
    "Worli": [18.9985, 72.8174],
    "Vile Parle": [19.1000, 72.8500],
    "Sion": [19.0426, 72.8615],
    "Kurla": [19.0734, 72.8810],
    "T2 Airport": [19.0896, 72.8656],
    "Andheri": [19.1197, 72.8460],
}

df = pd.read_csv("AirWise/mumbai_merged_clean.csv", parse_dates=["date"])

def clean_pm25(val):
    if isinstance(val, str) and " " in val:
        nums = [float(x) for x in val.strip().split() if x.replace('.', '', 1).isdigit()]
        return sum(nums) / len(nums) if nums else None
    try:
        return float(val)
    except:
        return None

df["pm25"] = df["pm25"].apply(clean_pm25)


df.columns = [col.strip().lower() for col in df.columns]

# ------------------ Live AQI Section ------------------ #

def fetch_live_aqi(city, token):
    API_URL = f"https://api.waqi.info/feed/{city}/?token={token}"
    response = requests.get(API_URL)
    data = response.json()
    if data["status"] == "ok":
        return data["data"]["aqi"]
    return None

def get_aqi_color_and_label(aqi):
    if aqi is None:
        return ("Unavailable", "#B0BEC5")
    elif aqi <= 50:
        return ("🟢 Good", "#4CAF50")
    elif aqi <= 100:
        return ("🟡 Moderate", "#FFEB3B")
    elif aqi <= 150:
        return ("🟠 Unhealthy for Sensitive Groups", "#FF9800")
    elif aqi <= 200:
        return ("🔴 Unhealthy", "#F44336")
    elif aqi <= 300:
        return ("🟣 Very Unhealthy", "#9C27B0")
    else:
        return ("⚫ Hazardous", "#5D4037")

aqi = fetch_live_aqi("mumbai", API_TOKEN)
aqilabel, bg_color = get_aqi_color_and_label(aqi)

st.markdown(
    f"""
    <div style='text-align: center; padding: 1.2rem; background-color: {bg_color}; border-radius: 10px; color: black;'>
        <h2>🌍 Live AQI in Mumbai</h2>
        <h1>{aqi if aqi else 'Unavailable'}</h1>
        <h4>{aqilabel}</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Sidebar Filters ------------------ #

st.sidebar.header("Filter Data")

pollutants = ["pm25", "pm10", "no2", "co", "so2", "o3"]
selected_pollutants = st.sidebar.multiselect("Select pollutants", pollutants, default=["pm25", "pm10"])

min_date, max_date = df["date"].min(), df["date"].max()
default_range = [max_date - pd.Timedelta(days=7), max_date]
date_range = st.sidebar.date_input("Select date range", default_range, min_value=min_date, max_value=max_date)

show_holidays_only = st.sidebar.checkbox("Show only holiday periods")
compare_mode = st.sidebar.checkbox("Compare Stations")

festival_windows = {
    "Diwali 2023": ("2023-11-08", "2023-11-14"),
    "Holi 2023": ("2023-03-04", "2023-03-10"),
    "Eid al-Fitr 2023": ("2023-04-20", "2023-04-23"),
    "Eid al-Adha 2023": ("2023-06-28", "2023-06-30"),
    "Christmas 2023": ("2023-12-23", "2023-12-26"),
    "Ganesh Chaturthi 2023": ("2023-09-18", "2023-09-20"),
    "Navratri 2023": ("2023-10-15", "2023-10-24"),
    "Independence Day": ("2023-08-14", "2023-08-16"),
    "Republic Day": ("2023-01-25", "2023-01-27"),
}

# ------------------ Map and Interaction ------------------ #

st.markdown("### 🗺️ Click on a Station on the Map")

m = folium.Map(location=[19.0760, 72.8777], zoom_start=11)
for location, coords in station_coords.items():
    folium.Marker(location=coords, popup=location, tooltip=location).add_to(m)

map_data = st_folium(m, height=480, width=None)
clicked_location = map_data.get("last_object_clicked_tooltip") if map_data else "Worli"
if not clicked_location:
    clicked_location = "Worli"

# ------------------ Data Filtering ------------------ #

if show_holidays_only:
    all_ranges = [pd.date_range(start, end) for start, end in festival_windows.values()]
    all_dates = pd.to_datetime([d for r in all_ranges for d in r])
    filtered_df = df[df["date"].isin(all_dates)]
    start_date = all_dates.min()
    end_date = all_dates.max()
else:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

# ------------------ Station Compare or Default ------------------ #

if compare_mode:
    st.header("📊 Compare Stations")
    locations_to_compare = st.multiselect("Select locations to compare", list(station_coords.keys()), default=["Worli", "Sion"])
    for loc in locations_to_compare:
        sub_df = filtered_df[filtered_df["location"] == loc]
        for pollutant in selected_pollutants:
            st.subheader(f"{pollutant.upper()} at {loc}")
            fig = px.line(sub_df, x="date", y=pollutant, title=f"{pollutant.upper()} in {loc}")
            st.plotly_chart(fig, use_container_width=True)
else:
    filtered_df = filtered_df[filtered_df["location"] == clicked_location]

    # ------------------ Summary Bar ------------------ #

    st.markdown("### 📊 Summary")

    total_days = filtered_df["date"].nunique() if not filtered_df.empty else 0
    pm25_cleaned = pd.to_numeric(filtered_df["pm25"], errors="coerce")
    avg_aqi = round(pm25_cleaned.mean(), 2) if not pm25_cleaned.dropna().empty else "N/A"
    date_range_text = f"{start_date.date()} to {end_date.date()}"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; background-color: #000000; padding: 1rem 0; border-radius: 10px; margin-bottom: 20px;">
            <div><strong>📍 Station:</strong><br>{clicked_location}</div>
            <div><strong>📅 Date Range:</strong><br>{date_range_text}</div>
            <div><strong>📈 Days of Data:</strong><br>{total_days}</div>
            <div><strong>💨 Avg. PM2.5:</strong><br>{avg_aqi} µg/m³</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------ Pollutant Charts ------------------ #

    st.markdown(f"### 📍 Selected Location: {clicked_location}")

    if filtered_df.empty:
        st.error("No data available for this location and date range.")
    else:
        for pollutant in selected_pollutants:
            st.subheader(f"💨 {pollutant.upper()} Concentration Over Time")
            fig = px.line(filtered_df, x="date", y=pollutant, labels={"date": "Date", pollutant: f"{pollutant.upper()} (µg/m³)"})
            fig.update_layout(xaxis_tickformat="%d/%m", hovermode="x unified", yaxis_title=f"{pollutant.upper()} (µg/m³)")
            st.plotly_chart(fig, use_container_width=True)

        # Insight Summary
        if show_holidays_only:
            st.info(f"📌 During holiday periods, average PM2.5 at {clicked_location} was {avg_aqi} µg/m³.")
        else:
            monthly_avg = df[(df["location"] == clicked_location)]["pm25"].mean()
            ratio = round(avg_aqi / monthly_avg, 2) if monthly_avg else "N/A"
            st.info(f"📌 Between {date_range_text}, {clicked_location} averaged {avg_aqi} µg/m³ PM2.5 — {ratio}x the monthly average.")

    # ------------------ CSV Export ------------------ #

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data as CSV", data=csv, file_name="filtered_aqi_data.csv", mime='text/csv')

# ------------------ Footer ------------------ #

st.markdown("---")
st.markdown("**Sources**: Data from [OpenAQ](https://openaq.org), CPCB | Visuals via Plotly & Folium")
