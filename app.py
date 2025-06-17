import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Voice of the Patient Pulseboard", page_icon="💊")

# Apply Ro theme styling
st.markdown("""
    <style>
        .main {
            background-color: #F6F6F6;
        }
        h1, h2, h3 {
            color: #FF0050;
        }
        .st-bb {
            background-color: #2D2D2D;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💊 Voice of the Patient Pulseboard")
st.markdown("Real-time insights inspired by Ro's mission to serve every patient across every county.")

section = st.sidebar.radio("Select Dashboard Section", [
    "🧠 Patient Sentiment",
    "📈 Telehealth Trends",
    "💊 Drug Safety Events",
    "🗺️ Care Access Map",
    "💬 Online Patient Topics"
])
