import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image

# ─── Page & Brand Setup ─────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Voice of the Patient Pulseboard",
    page_icon="💊"
)
st.markdown("""
    <style>
        body { background-color: #FAF9F6; color: #1C1C1C; }
        h1, h2, h3 { color: #FF0050; font-weight: 700; }
        .block-container { padding-top: 2rem; }
        .stSidebar { background-color: #FFFFFF; }
        .css-10trblm, .st-bb { font-family: 'Segoe UI', sans-serif; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ─── Logo Header ────────────────────────────────────────────────────────────────
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
logo = Image.open("ro_Logo.jpg")
col1, col2 = st.columns([1, 9])
with col1:
    st.image(logo, width=80)
st.markdown("<br>", unsafe_allow_html=True)

# ─── Sidebar Navigation ─────────────────────────────────────────────────────────
section_titles = {
    "🔎 Summary": "🔎 Summary Overview",
    "🧠 Patient Sentiment": "🧠 Patient Sentiment",
    "📈 Telehealth Trends": "📈 Telehealth Trends",
    "💊 Drug Safety Events": "💊 Drug Safety Events",
    "💬 Online Patient Topics": "💬 Online Patient Topics"
}
section = st.sidebar.radio(
    "📊 Select Dashboard Section",
    list(section_titles.keys())
)
st.title(section_titles[section])
st.markdown(
    "Real-time insights inspired by Ro’s mission to serve every patient across every county."
)

# ─── PRE-COMPUTE & GLOBALS ───────────────────────────────────────────────────────
# Patient Sentiment Data
feedback = [
    "Loved how easy the prescription delivery was!",
    "Felt like the wait time was too long.",
    "Super convenient! The online consult saved me time.",
    "Didn't feel the doctor listened.",
    "Love how discreet the packaging was."
]
df_sent = pd.DataFrame(feedback, columns=["Feedback"])
df_sent["Sentiment Score"] = [0.8, -0.4, 0.9, -0.6, 0.7]
avg_sentiment = df_sent["Sentiment Score"].mean()

# Telehealth mock timeseries
telehealth_data = pd.DataFrame({
    "Month": pd.date_range("2022-01-01", periods=12, freq='M'),
    "Visits (Thousands)": [50, 55, 60, 58, 61, 66, 70, 68, 72, 75, 80, 85]
})
pct_change = (
    (telehealth_data["Visits (Thousands)"].iloc[-1]
     - telehealth_data["Visits (Thousands)"].iloc[0])
    / telehealth_data["Visits (Thousands)"].iloc[0]
) * 100
latest_visits = telehealth_data["Visits (Thousands)"].iloc[-1]

# Drug Safety count
try:
    resp = requests.get(
        "https://api.fda.gov/drug/event.json"
        "?search=patient.drug.medicinalproduct:minoxidil&limit=5"
    ).json()
    num_events = len(resp.get("results", []))
except:
    num_events = None

# Online topics (sample)
topics = {
    "Hair loss treatment": 120,
    "ED telehealth": 90,
    "Ro reviews": 75,
    "Testosterone therapy": 60,
    "Weight loss meds": 55
}

# ─── SUMMARY TAB ────────────────────────────────────────────────────────────────
if section == "🔎 Summary":
    st.markdown(
        """
        <div style="
            background-color: #FFFFFF;
            border: 1px solid #DDDDDD;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        ">
        <h4>📌 Executive Summary</h4>
        <ul style="line-height:1.6;">
          <li>
            <strong>Patients aren’t just satisfied—they’re grateful.</strong><br>
            Phrases like “loved,” “easy,” and “saved me time” dominate feedback, reflecting appreciation for simplicity. A few outliers—like “didn’t feel the doctor listened”—point to an opportunity to humanize virtual care interactions.
          </li>
          <li>
            <strong>Convenience is currency.</strong><br>
            The most charged words in the word cloud (e.g., easy, delivery, convenient, saved) show value placed on frictionless access often outweighs clinical detail. Streamlining further could deepen loyalty.
          </li>
          <li>
            <strong>Telehealth is gaining real-world momentum—especially among new users.</strong><br>
            A 70% increase in virtual visits year-over-year signals more patients entering Ro digitally. Focus on onboarding flows and first-time user education is key.
          </li>
          <li>
            <strong>Ro’s medical offerings resonate—but questions linger.</strong><br>
            OpenFDA reports indicate side effects like headaches and dizziness for minoxidil. Transparency and reassurance in post-purchase messaging could reduce hesitancy.
          </li>
          <li>
            <strong>Hair loss treatment is driving curiosity.</strong><br>
            Online interest around “Hair loss treatment” outpaces all other topics. Consider educational content, video testimonials, or first-time offers to capitalize on this awareness.
          </li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ─── PATIENT SENTIMENT ───────────────────────────────────────────────────────────
if section == "🧠 Patient Sentiment":
    st.subheader("What patients are saying")
    df_display = df_sent.copy()
    df_display.index = df_display.index + 1
    st.table(df_display)

    st.subheader("Top Words from Patient Feedback")
    wc = WordCloud(width=400, height=200, background_color="white").generate(" ".join(feedback))
    fig, ax = plt.subplots(figsize=(6,3))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# ─── TELEHEALTH TRENDS ───────────────────────────────────────────────────────────
if section == "📈 Telehealth Trends":
    st.subheader("U.S. Telehealth Visit Trends")
    fig = px.line(
        telehealth_data,
        x="Month",
        y="Visits (Thousands)",
        title="Telehealth Growth Over Time",
        markers=True,
        template="plotly_white",
        color_discrete_sequence=["#FF0050"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── DRUG SAFETY EVENTS ─────────────────────────────────────────────────────────
if section == "💊 Drug Side Effect cases - Minoxidil":
    st.subheader("Latest Drug Event Reports (OpenFDA)")
    r = requests.get(
        "https://api.fda.gov/drug/event.json"
        "?search=patient.drug.medicinalproduct:minoxidil&limit=5"
    )
    if r.status_code == 200:
        for e in r.json().get("results", []):
            reactions = ", ".join(rxn["reactionmeddrapt"] for rxn in e["patient"]["reaction"])
            st.write(f"**Reported Reactions**: {reactions}")
    else:
        st.error("API limit reached or unavailable.")

# ─── ONLINE PATIENT TOPICS ───────────────────────────────────────────────────────
if section == "💬 Online Patient Topics":
    st.subheader("Trending Topics Among Patients (Sample)")
    df_topics = pd.DataFrame(list(topics.items()), columns=["Topic","Mentions"])
    fig = px.bar(
        df_topics,
        x="Topic",
        y="Mentions",
        title="What Patients Are Talking About",
        template="plotly_white",
        color_discrete_sequence=["#FF0050"]
    )
    st.plotly_chart(fig, use_container_width=True)
