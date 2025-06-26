import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Sample Mumbai areas for prediction
locations = [
    "Bandra", "Dadar", "Colaba", "Andheri", "Kurla", "Borivali",
    "Powai", "Worli", "Chembur", "Ghatkopar", "Malad"
]

st.set_page_config(page_title="Forecast Insights", layout="wide")
st.title("📈 Mumbai AQI Forecast Insights")

# Fake prediction model: Replace this later with regression
def predict_pm25():
    base = random.randint(45, 90)
    return {
        "today": round(base + random.uniform(-10, 5), 1),
        "tomorrow": round(base + random.uniform(-5, 10), 1)
    }

# AQI Category based on PM2.5
def categorize(pm25):
    if pm25 <= 50:
        return "🟢 Good", "green"
    elif pm25 <= 100:
        return "🟠 Moderate", "orange"
    else:
        return "🔴 Unhealthy", "red"

# Show cards
for i in range(0, len(locations), 3):
    cols = st.columns(3)
    for j, loc in enumerate(locations[i:i+3]):
        with cols[j]:
            pred = predict_pm25()
            today_status, today_color = categorize(pred["today"])
            tomorrow_status, tomorrow_color = categorize(pred["tomorrow"])

            st.markdown(f"### 📍 {loc}")
            st.markdown(f"**Today ({datetime.now().strftime('%b %d')}):** `{pred['today']} µg/m³` — {today_status}")
            st.markdown(f"**Tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%b %d')}):** `{pred['tomorrow']} µg/m³` — {tomorrow_status}")
            st.markdown("---")
