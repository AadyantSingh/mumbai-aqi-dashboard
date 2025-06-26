import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="AirWise", layout="centered")

st.title("🌬️ Welcome to AirWise")

st.markdown("""
AirWise helps you find the healthiest route across Mumbai using live AQI data, predictive AI, and smart routing.

Choose a page from the left:
- **Smart Route**: Plan a route and see AQI along the way
- **Dashboard**: Explore Mumbai’s AQI history
- **Forecast Insights**: Predict upcoming AQI levels
- **About**: Learn more about the project
""")
