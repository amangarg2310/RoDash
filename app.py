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

# State-to-code map
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

# Static fallback for map/table
fallback_value = int(latest_visits)
static_states = pd.DataFrame({
    "state": list(us_state_abbrev.keys()),
    "interest": [fallback_value]*len(us_state_abbrev)
})
static_states["code"] = static_states["state"].map(us_state_abbrev)
static_dmas = pd.DataFrame({
    "Metro": ["N/A"]*10,
    "Interest": [0]*10
})

# Online topics — **defined at top** so never NameError
topics = {
    "Hair loss treatment": 120,
    "ED telehealth": 90,
    "Ro reviews": 75,
    "Testosterone therapy": 60,
    "Weight loss meds": 55
}

# ─── SUMMARY TAB ────────────────────────────────────────────────────────────────
if section == "🔎 Summary":
    # Executive Summary — replace the text below with your own analysis!
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
        <ul>
          <li>Overall sentiment remains strong (avg score 0.28).</li>
          <li>Telehealth visits up ~70% year-over-year to 85K/mo.</li>
          <li>5 recent OpenFDA reports for minoxidil.</li>
          <li>Live state/metro search data updating soon.</li>
          <li>Top online topic: “Hair loss treatment.”</li>
        </ul>
        <p style="font-style:italic;">
          *Edit this text block with your own commentary.*  
        </p>
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
        pytrends
        .interest_by_region(resolution="REGION", inc_low_vol=True)
        .reset_index()
        .rename(columns={"geoName": "state", "telehealth": "interest"})
    )

    df_states["code"] = df_states["state"].map(us_state_abbrev)
    df_states = df_states.dropna(subset=["code"])

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

except Exception as e:
    st.warning("⚠️ Live Trends unavailable — showing static fallback.")
    fallback_states = pd.DataFrame({
        "state": list(us_state_abbrev.keys()),
        "interest": [85 for _ in range(len(us_state_abbrev))],
        "code": list(us_state_abbrev.values())
    })
    fig = px.choropleth(
        fallback_states,
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
    df_dmas = (
        pytrends
        .interest_by_region(resolution="DMA", inc_low_vol=True)
        .reset_index()
        .rename(columns={"geoName": "Metro", "telehealth": "Interest"})
    )
    top10 = df_dmas[df_dmas["Interest"] > 0].sort_values("Interest", ascending=False).head(10)
    top10.index = top10.index + 1
    st.table(top10)

except Exception:
    st.warning("⚠️ Metro data unavailable — showing static fallback.")
    st.table(pd.DataFrame({
        "Metro": ["N/A"] * 10,
        "Interest": [0] * 10
    }, index=range(1, 11)))

    top10.index = top10.index + 1
    st.table(top10)

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
