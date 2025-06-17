import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Voice of the Patient Pulseboard", page_icon="💊")

# ---- CUSTOM STYLING FOR RO BRAND ----
st.markdown("""
    <style>
        body {
            background-color: #FAF9F6;
            color: #1C1C1C;
        }
        h1, h2, h3 {
            color: #FF0050;
            font-weight: 700;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stSidebar {
            background-color: #FFFFFF;
        }
        .css-10trblm, .st-bb {
            font-family: 'Segoe UI', sans-serif;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---- SHOW RO LOGO AT THE TOP ----
from PIL import Image
logo = Image.open("ro_Logo.jpg")
st.image(logo, width=100)

# ---- SECTION TITLES + NAVIGATION ----
section_titles = {
    "🧠 Patient Sentiment": "🧠 Patient Sentiment",
    "📈 Telehealth Trends": "📈 Telehealth Trends",
    "💊 Drug Safety Events": "💊 Drug Safety Events",
    "🗺️ Care Access Map": "🗺️ Care Access Map",
    "💬 Online Patient Topics": "💬 Online Patient Topics"
}

section = st.sidebar.radio("📊 Select Dashboard Section", list(section_titles.keys()))

st.title(section_titles.get(section, "Voice of the Patient Pulseboard"))
st.markdown("Real-time insights inspired by Ro’s mission to serve every patient across every county.")
