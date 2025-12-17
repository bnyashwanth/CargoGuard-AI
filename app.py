import streamlit as st
import pandas as pd
import pickle, sqlite3, os
import plotly.graph_objects as go
import plotly.express as px

from utils.explain import generate_explanation
from utils.recommend import recommend_action
from utils.delay import estimate_delay
from utils.map_data import PORT_COORDS
from utils.pdf_report import generate_pdf

st.set_page_config("CargoGuard AI", "🚢", layout="wide")

@st.cache_resource
def load_models():
    with open("models/pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    with open("models/risk_model.pkl", "rb") as f:
        model = pickle.load(f)
    return pipeline, model

pipeline, model = load_models()

def gauge(value, title, min_v, max_v):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range': [min_v, max_v]}}
    ))
    fig.update_layout(height=220)
    return fig

with st.sidebar:
    st.header("Shipment Inputs")
    ship_type = st.selectbox("Ship Type", ["Container Ship","Oil Tanker","Bulk Carrier","LNG Carrier"])
    origin = st.selectbox("Origin", list(PORT_COORDS.keys()))
    destination = st.selectbox("Destination", list(PORT_COORDS.keys()))
    category = st.selectbox("Cargo", ["Food","Pharma","Machinery","Crude Oil"])
    priority = st.selectbox("Priority", [1,2,3])

    distance = st.number_input("Distance (km)", 500, 20000, 9000)
    total_ports = st.number_input("Total Ports", 2, 20, 6)
    ports_crossed = st.number_input("Ports Crossed", 0, 20, 3)

    st.subheader("What-if Simulation")
    weather = st.slider("Weather", 1, 5, 3)
    congestion = st.slider("Congestion", 0.0, 1.0, 0.6)
    traffic = st.slider("Traffic", 0.0, 1.0, 0.5)
    route_risk = st.slider("Route Risk", 0.0, 1.0, 0.4)

    run = st.button("Analyze")

st.title("🚢 CargoGuard AI – Smart Maritime Risk System")

if run:
    df = pd.DataFrame([{
        "shipment_distance_km": distance,
        "route_risk_score": route_risk,
        "total_ports": total_ports,
        "ports_crossed": ports_crossed,
        "port_congestion": congestion,
        "sea_traffic_index": traffic,
        "weather_severity": weather,
        "ship_type": ship_type,
        "product_category": category,
        "origin_port": origin,
        "destination_port": destination,
        "shipment_priority": priority
    }])

    X = pipeline.transform(df)
    risk = round(model.predict(X)[0], 2)

    days, prob = estimate_delay(risk, weather, congestion, traffic)

    c1,c2,c3 = st.columns(3)
    c1.metric("Risk", f"{risk}%")
    c2.metric("Delay", f"+{days} days")
    c3.metric("Delay Probability", f"{prob}%")

    g1,g2,g3,g4 = st.columns(4)
    g1.plotly_chart(gauge(weather,"Weather",1,5),True)
    g2.plotly_chart(gauge(congestion*100,"Congestion",0,100),True)
    g3.plotly_chart(gauge(traffic*100,"Traffic",0,100),True)
    g4.plotly_chart(gauge(risk,"Risk",0,100),True)

    st.subheader("🤖 AI Explanation")
    st.info(generate_explanation(risk, weather, congestion, traffic))

    action = recommend_action(risk)
    st.subheader("🧠 Recommended Action")
    st.success(action)

    st.subheader("🧭 Route Map")
    lat = [PORT_COORDS[origin][0], PORT_COORDS[destination][0]]
    lon = [PORT_COORDS[origin][1], PORT_COORDS[destination][1]]
    map_df = pd.DataFrame({"lat":lat,"lon":lon})
    st.map(map_df)

    progress = min(ports_crossed/total_ports,1)
    st.progress(progress)
    st.write(f"Progress: {int(progress*100)}%")

    if st.button("📄 Download PDF Report"):
        file = generate_pdf(df.iloc[0].to_dict(), risk, action)
        with open(file,"rb") as f:
            st.download_button("Download Report", f, file_name=file)

st.caption("Made with ❤️ using Streamlit")
st.caption("Done by Team KYPRO ⭐ · All Rights Reserved")
