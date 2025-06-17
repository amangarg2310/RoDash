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

# 1) Extra vertical whitespace at the very top
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# 2) Load Ro logo
logo = Image.open("ro_Logo.jpg")

# 3) Left-align the logo in a narrow column
col1, col2 = st.columns([1, 9])
with col1:
    st.image(logo, width=80)

# 4) Small spacer below the logo
st.markdown("<br>", unsafe_allow_html=True)

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

# Sections

if section == "🧠 Patient Sentiment":
    st.subheader("What patients are saying")
    feedback = [
        "Loved how easy the prescription delivery was!",
        "Felt like the wait time was too long.",
        "Super convenient! The online consult saved me time.",
        "Didn't feel the doctor listened.",
        "Love how discreet the packaging was."
    ]
    df = pd.DataFrame(feedback, columns=["Feedback"])
    df["Sentiment Score"] = [0.8, -0.4, 0.9, -0.6, 0.7]
    df["Sentiment"] = df["Sentiment Score"].apply(lambda x: "Positive" if x > 0 else "Negative")
    st.dataframe(df)

    st.subheader("Top Words from Patient Feedback")
    text = " ".join(feedback)
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

if section == "📈 Telehealth Trends":
    st.subheader("U.S. Telehealth Visit Trends")
    telehealth_data = pd.DataFrame({
        "Month": pd.date_range("2022-01-01", periods=12, freq='M'),
        "Visits (Thousands)": [50, 55, 60, 58, 61, 66, 70, 68, 72, 75, 80, 85]
    })
    fig = px.line(telehealth_data, x="Month", y="Visits (Thousands)",
                  title="Telehealth Growth Over Time", markers=True,
                  template="plotly_white", color_discrete_sequence=["#FF0050"])
    st.plotly_chart(fig, use_container_width=True)

if section == "💊 Drug Safety Events":
    st.subheader("Latest Drug Event Reports (OpenFDA)")
    query = "minoxidil"
    url = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:{query}&limit=5"
    r = requests.get(url)
    if r.status_code == 200:
        events = r.json().get("results", [])
        for e in events:
            reactions = ", ".join([r["reactionmeddrapt"] for r in e["patient"]["reaction"]])
            st.write(f"**Reported Reactions**: {reactions}")
    else:
        st.error("API limit reached or unavailable.")

if section == "🗺️ Care Access Map":
    st.subheader("🗺️ U.S. Telehealth Search Interest Heatmap")

    try:
        # 1) Import & initialize pytrends
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360)

        # 2) Build payload for “telehealth” over the past 12 months in the U.S.
        kw_list = ["telehealth"]
        pytrends.build_payload(kw_list, timeframe="today 12-m", geo="US")

        # 3) Fetch interest by state
        df_states = (
            pytrends
            .interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
            .reset_index()
            .rename(columns={
                "geoName": "state",
                "geoCode": "state_code",
                "telehealth": "interest"
            })
        )

        # 4) Plotly choropleth map
        fig = px.choropleth(
            df_states,
            locations="state_code",
            locationmode="USA-states",
            color="interest",
            scope="usa",
            color_continuous_scale="Reds",
            labels={"interest": "Search Interest"}
        )
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # 5) Top 10 cities by interest
        st.subheader("Top 10 Metro Areas by Telehealth Search Interest")
        df_cities = (
            pytrends
            .interest_by_region(resolution="CITY", inc_low_vol=True)
            .reset_index()
            .rename(columns={"geoName": "city", "telehealth": "interest"})
        )
        top_cities = df_cities.sort_values("interest", ascending=False).head(10)
        st.table(top_cities[["city", "interest"]].style.format({"interest": "{:.0f}"}))

    except Exception as e:
        st.error("🚨 Could not load dynamic telehealth data. Ensure `pytrends` is installed and your internet connection is active.")

if section == "💬 Online Patient Topics":
    st.subheader("Trending Topics Among Patients (Sample)")
    topics = {
        "Hair loss treatment": 120,
        "ED telehealth": 90,
        "Ro reviews": 75,
        "Testosterone therapy": 60,
        "Weight loss meds": 55
    }
    df = pd.DataFrame(topics.items(), columns=["Topic", "Mentions"])
    fig = px.bar(df, x="Topic", y="Mentions", title="What Patients Are Talking About",
                 template="plotly_white", color_discrete_sequence=["#FF0050"])
    st.plotly_chart(fig, use_container_width=True)
