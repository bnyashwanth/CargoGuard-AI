import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go

st.set_page_config(
    page_title="Maritime Risk AI",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 1. Global Font Reduction */
    html, body, [class*="css"] {
        font-size: 14px; 
    }
    
    /* 2. Compact Metric Cards */
    div[data-testid="stMetric"], .stMetric {
        background-color: #F0F2F6;
        border: 1px solid #D6D6D6;
        padding: 8px 10px; /* Reduced padding */
        border-radius: 8px;
        color: black;
    }
    
    /* Metric Label (e.g. "Risk Score") */
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important; /* Smaller label */
        color: #444 !important;
    }
    
    /* Metric Value (e.g. "73%") */
    div[data-testid="stMetricValue"] {
        font-size: 20px !important; /* Smaller number */
        color: #000 !important;
        font-weight: 700;
    }
    
    /* 3. Compact Sidebar */
    [data-testid="stSidebar"] {
        font-size: 12px;
    }
    
    /* Headers */
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 18px !important; }
    
    /* Plotly Background Removal */
    .js-plotly-plot .plotly .main-svg {
        background: rgba(0,0,0,0) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_components():
    with open("pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    with open("risk_model.pkl", "rb") as f:
        model = pickle.load(f)
    return pipeline, model

try:
    pipeline, model = load_components()
except FileNotFoundError:
    st.error("❌ Critical Error: .pkl files not found.")
    st.stop()

def analyze_delay_factors(risk, weather, congestion, traffic):
    days = 0
    reasons = []
    
    if weather >= 4:
        days += 2
        reasons.append("Weather")
    if congestion > 0.7:
        days += 1
        reasons.append("Congestion")
    if traffic > 0.8:
        days += 1
        reasons.append("Traffic")
    if risk > 60:
        days += 2
        reasons.append("Risk")
        
    if days == 0: return 0, 10.0, "None"
    prob = min(risk + (days * 10), 99.9)
    return days, prob, ", ".join(reasons)

def create_gauge(value, title, min_v=0, max_v=100):
    """Creates a Compact Gauge Chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'color': 'black', 'size': 14}}, # Smaller Title
        number = {'font': {'color': 'black', 'size': 16}}, # Smaller Number
        gauge = {
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "black", 'thickness': 0.2}, 
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 1,
            'bordercolor': "#666",
            'steps': [
                {'range': [min_v, max_v*0.33], 'color': '#00CC96'},
                {'range': [max_v*0.33, max_v*0.66], 'color': '#FFA15A'},
                {'range': [max_v*0.66, max_v], 'color': '#EF553B'}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "black"},
        height=160, # Reduced Height
        margin=dict(l=15, r=15, t=30, b=15)
    )
    return fig

with st.sidebar:
    st.header("📝 Enter the required deatails")
    
    ship_type = st.selectbox("Ship Type", ['Reefer Ship', 'Bulk Carrier', 'General Cargo Ship', 'LNG Carrier', 'Chemical Tanker', 'Oil Tanker', 'Container Ship', 'Ro-Ro Ship'])
    origin_port = st.selectbox("Origin Port", ['Mumbai Port', 'JNPT Port', 'Kandla Port', 'Chennai Port', 'Kochi Port', 'Paradip Port', 'Tuticorin Port', 'Vizag Port'])
    destination_port = st.selectbox("Destination Port", ['Mumbai Port', 'Kochi Port', 'Vizag Port', 'Tuticorin Port', 'Kandla Port', 'Paradip Port', 'JNPT Port', 'Chennai Port'])
    product_category = st.selectbox("Category", ['Food', 'Automobile', 'Pharma', 'Machinery', 'FMCG', 'Chemicals', 'Electronics', 'Crude Oil'])
    shipment_priority = st.selectbox("Priority", [1, 2, 3])

    st.markdown("---")
    shipment_distance_km = st.number_input("Distance (km)", 100.0, 20000.0, 8500.0)
    total_ports = st.number_input("Total Ports", 2, 50, 6)
    ports_crossed = st.number_input("Ports Crossed", 0, 50, 3)

    st.markdown("### 📡 Sensors")
    weather_severity = st.slider("Weather (1-5)", 1, 5, 3)
    port_congestion = st.slider("Congestion (0-1)", 0.0, 1.0, 0.65)
    sea_traffic_index = st.slider("Traffic (0-1)", 0.0, 1.0, 0.50)
    route_risk_score = st.slider("Route Risk (0-1)", 0.0, 1.0, 0.45)

    btn = st.button("🚀 Analyze", type="primary")

st.title("🚢 Cargo Guard AI")

if btn:

    u_input = pd.DataFrame({
        "shipment_distance_km": [shipment_distance_km], "route_risk_score": [route_risk_score],
        "total_ports": [total_ports], "ports_crossed": [ports_crossed],
        "port_congestion": [port_congestion], "sea_traffic_index": [sea_traffic_index],
        "weather_severity": [weather_severity], "ship_type": [ship_type],
        "product_category": [product_category], "origin_port": [origin_port],
        "destination_port": [destination_port], "shipment_priority": [shipment_priority]
    })
    
    try:
        user_fea = pipeline.transform(u_input)
        risk_score = round(model.predict(user_fea)[0], 2)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    est_days, prob, reason = analyze_delay_factors(risk_score, weather_severity, port_congestion, sea_traffic_index)

    if risk_score <= 30: status_msg = "✅ Safe"
    elif risk_score <= 60: status_msg = "⚠️ Caution"
    else: status_msg = "🚨 Critical"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risk Score", f"{risk_score}%")
    c2.metric("Status", status_msg)
    c3.metric("Delay", f"+{est_days} Days")
    c4.metric("Delay Prob", f"{prob}%")
    
    st.divider()

    d1, d2 = st.columns([1, 2])
    with d1: st.info(f"**Cause:** {reason}")
    with d2:
        if est_days > 0: st.warning(f"⚠️ {est_days} day delay expected.")
        else: st.success("✅ On Schedule.")

    st.divider()

    st.caption("Live Factors")
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.plotly_chart(create_gauge(weather_severity, "Weather", 1, 5), use_container_width=True)
    with g2: st.plotly_chart(create_gauge(port_congestion*100, "Congestion", 0, 100), use_container_width=True)
    with g3: st.plotly_chart(create_gauge(sea_traffic_index*100, "Traffic", 0, 100), use_container_width=True)
    with g4: st.plotly_chart(create_gauge(route_risk_score*100, "Risk", 0, 100), use_container_width=True)

    st.divider()
    pct = min(ports_crossed / total_ports, 1.0)
    st.caption(f"Tracker: {origin_port} -> {destination_port}")
    st.progress(pct)
    st.text(f"Progress: {int(pct*100)}%")

else:
    st.info("👈 Set config in sidebar.")
st.markdown("Made with ❤️ using Streamlit")
st.markdown("Done by Team KYPRO ⭐. All Rights Reserved")