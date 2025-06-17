import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError

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
    "🗺️ Care Access Map": "🗺️ Care Access Map",
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

# ─── PRE-COMPUTE DATA FOR SUMMARY ───────────────────────────────────────────────
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

try:
    resp = requests.get(
        "https://api.fda.gov/drug/event.json"
        "?search=patient.drug.medicinalproduct:minoxidil&limit=5"
    ).json()
    num_events = len(resp.get("results", []))
except:
    num_events = None

# State abbreviation mapping
us_state_abbrev = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC',
    'Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL',
    'Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA',
    'Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN',
    'Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',
    'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
    'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
    'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
    'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
}

# Fallback for state map
fallback_value = int(latest_visits)
static_states = pd.DataFrame({
    "state": list(us_state_abbrev.keys()),
    "interest": [fallback_value] * len(us_state_abbrev)
})
static_states["code"] = static_states["state"].map(us_state_abbrev)

# Fallback for DMA table
static_dmas = pd.DataFrame({
    "Metro": ["N/A"] * 10,
    "Interest": [0] * 10
})

# ─── SUMMARY TAB ────────────────────────────────────────────────────────────────
if section == "🔎 Summary":
    # You can replace the HTML below with your own text & analysis
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
        <p>
          Welcome to the high-level overview. Here you can drop in your own analysis and findings for
          stakeholders—no code needed. For example:
        </p>
        <ul>
          <li>Overall patient sentiment remains positive, with an average score of 0.28.</li>
          <li>Telehealth adoption grew ~70% year-over-year, now at 85K visits/month.</li>
          <li>We observed 5 recent OpenFDA reports on the sample drug minoxidil.</li>
          <li>Search interest by state and metro is currently being updated—please check back later.</li>
          <li>Key online conversations center around “Hair loss treatment.”</li>
        </ul>
        <p style="font-style:italic; margin-top:10px;">
          *Customize this box with any narrative, context, or executive commentary you’d like.*
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Stop here—no metrics or charts in the Summary tab
    st.stop()

# ─── PATIENT SENTIMENT ───────────────────────────────────────────────────────────
if section == "🧠 Patient Sentiment":
    st.subheader("What patients are saying")
    df_display = df_sent.copy()
    df_display.index = df_display.index + 1
    st.table(df_display)

    st.subheader("Top Words from Patient Feedback")
    text = " ".join(feedback)
    wc = WordCloud(width=400, height=200, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(6, 3))
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
if section == "💊 Drug Safety Events":
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

# ─── CARE ACCESS MAP ─────────────────────────────────────────────────────────────
if section == "🗺️ Care Access Map":
    st.subheader("🗺️ Telehealth Search Interest by State (Last 12 Months)")
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(["telehealth"], timeframe="today 12-m", geo="US")
        df_states = (
            pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)
            .reset_index()
            .rename(columns={"geoName": "state", "telehealth": "interest"})
        )
        df_states["code"] = df_states["state"].map(us_state_abbrev)
        df_states = df_states.dropna(subset=["code"])
    except (TooManyRequestsError, KeyError):
        st.warning("⚠️ Live Trends unavailable — showing static fallback.")
        df_states = static_states.copy()

    fig = px.choropleth(
        df_states,
        locations="code",
        locationmode="USA-states",
        color="interest",
        scope="usa",
        color_continuous_scale="Reds",
        labels={"interest": "Search Intensity"}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Metros by Telehealth Search Interest (DMA)")
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(["telehealth"], timeframe="today 12-m", geo="US")
        df_dmas_live = (
            pytrends.interest_by_region(resolution="DMA", inc_low_vol=True)
            .reset_index()
            .rename(columns={"geoName": "Metro", "telehealth": "Interest"})
        )
        df_dmas_live = df_dmas_live[df_dmas_live["Interest"] > 0]
        top10 = (
            df_dmas_live
            .sort_values("Interest", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
    except (TooManyRequestsError, KeyError):
        st.warning("⚠️ Metro-level live data unavailable — showing static fallback.")
        top10 = static_dmas.copy()

    top10.index = top10.index + 1
    st.table(top10)

# ─── ONLINE PATIENT TOPICS ───────────────────────────────────────────────────────
if section == "💬 Online Patient Topics":
    st.subheader("Trending Topics Among Patients (Sample)")
    df_topics = pd.DataFrame(topics.items(), columns=["Topic", "Mentions"])
    fig = px.bar(
        df_topics,
        x="Topic",
        y="Mentions",
        title="What Patients Are Talking About",
        template="plotly_white",
        color_discrete_sequence=["#FF0050"]
    )
    st.plotly_chart(fig, use_container_width=True)
