import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from utils.pdf_report import generate_pdf
from utils.routes import ROUTE_PROFILES

# ---------------- CONFIG ----------------
AVG_SPEED_KMPH = 30
COST_PER_KM = 20

st.set_page_config(
    page_title="CargoGuard AI",
    page_icon="🚢",
    layout="wide"
)

# ---------------- PORT COORDS ----------------
PORT_COORDS = {
    "Mumbai Port": (19.0760, 72.8777),
    "JNPT Port": (18.9499, 72.9528),
    "Kandla Port": (23.0339, 70.2204),
    "Chennai Port": (13.0827, 80.2707),
    "Kochi Port": (9.9312, 76.2673),
    "Paradip Port": (20.3166, 86.6114),
    "Tuticorin Port": (8.7642, 78.1348),
    "Vizag Port": (17.6868, 83.2185)
}

# ---------------- LOAD ML ----------------
@st.cache_resource
def load_model():
    with open("models/pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    with open("models/risk_model.pkl", "rb") as f:
        model = pickle.load(f)
    return pipeline, model

pipeline, model = load_model()

# ---------------- SIDEBAR ----------------
st.sidebar.header("📝 Shipment Details")

ship_type = st.sidebar.selectbox(
    "Ship Type",
    ['Reefer Ship','Bulk Carrier','General Cargo Ship','LNG Carrier',
     'Chemical Tanker','Oil Tanker','Container Ship','Ro-Ro Ship']
)

origin_port = st.sidebar.selectbox("Origin Port", list(PORT_COORDS.keys()))
destination_port = st.sidebar.selectbox("Destination Port", list(PORT_COORDS.keys()))

product_category = st.sidebar.selectbox(
    "Cargo Category",
    ['Food','Automobile','Pharma','Machinery','FMCG',
     'Chemicals','Electronics','Crude Oil']
)

shipment_priority = st.sidebar.selectbox("Priority", [1, 2, 3])

shipment_distance_km = st.sidebar.number_input(
    "Distance (km)", 100.0, 20000.0, 8500.0
)

total_ports = st.sidebar.number_input("Total Ports", 2, 50, 6)
ports_crossed = st.sidebar.number_input("Ports Crossed", 0, 50, 3)

weather_severity = st.sidebar.slider("Weather (1–5)", 1, 5, 3)
port_congestion = st.sidebar.slider("Congestion (0–1)", 0.0, 1.0, 0.6)
sea_traffic_index = st.sidebar.slider("Traffic (0–1)", 0.0, 1.0, 0.5)
route_risk_score = st.sidebar.slider("Route Risk (0–1)", 0.0, 1.0, 0.4)

departure_time = st.sidebar.datetime_input(
    "Departure Date & Time", datetime.now()
)

analyze = st.sidebar.button("🚀 Analyze")

# ---------------- MAIN ----------------
st.title("🚢 CargoGuard AI Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Risk Dashboard",
    "🔀 Route Comparison",
    "📄 Reports",
    "🌍 Global Route Map"
])

if analyze:
    # -------- ML INPUT --------
    X = pd.DataFrame({
        "shipment_distance_km": [shipment_distance_km],
        "route_risk_score": [route_risk_score],
        "total_ports": [total_ports],
        "ports_crossed": [ports_crossed],
        "port_congestion": [port_congestion],
        "sea_traffic_index": [sea_traffic_index],
        "weather_severity": [weather_severity],
        "ship_type": [ship_type],
        "product_category": [product_category],
        "origin_port": [origin_port],
        "destination_port": [destination_port],
        "shipment_priority": [shipment_priority]
    })

    features = pipeline.transform(X)
    base_risk = round(model.predict(features)[0], 2)

    progress = min(ports_crossed / total_ports, 1.0)

    # -------- ROUTES COMPUTATION --------
    routes = []
    for name, cfg in ROUTE_PROFILES.items():
        dist = shipment_distance_km * cfg["distance_factor"]
        risk = min(100, round(base_risk * cfg["risk_factor"], 2))
        delay = round((risk / 100) * 4, 1)

        travel_hours = dist / AVG_SPEED_KMPH
        eta = departure_time + timedelta(
            hours=travel_hours + delay * 24
        )

        cost = int(dist * COST_PER_KM)

        routes.append({
            "Route": name,
            "Distance (km)": int(dist),
            "Risk (%)": risk,
            "Delay (days)": delay,
            "ETA": eta.strftime("%Y-%m-%d %H:%M"),
            "Cost (₹)": cost
        })

    routes_df = pd.DataFrame(routes)

    # ================= TAB 1 =================
    with tab1:
        primary = routes_df[routes_df.Route == "Primary"].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Risk Score", f"{primary['Risk (%)']}%")
        c2.metric("Expected Delay", f"{primary['Delay (days)']} days")
        c3.metric("ETA", primary["ETA"])
        c4.metric("Cost", f"₹{primary['Cost (₹)']:,}")

        st.progress(progress)
        st.caption(f"{int(progress*100)}% completed")

    # ================= TAB 2 =================
    with tab2:
        st.subheader("Alternative Routes")
        st.dataframe(routes_df, use_container_width=True)

        safest = routes_df.sort_values("Risk (%)").iloc[0]["Route"]
        fastest = routes_df.sort_values("Delay (days)").iloc[0]["Route"]
        cheapest = routes_df.sort_values("Cost (₹)").iloc[0]["Route"]

        st.info(f"🛡️ Safest: {safest} | ⚡ Fastest: {fastest} | 💰 Cheapest: {cheapest}")

        selected_route = st.radio(
            "Select route to visualize",
            routes_df["Route"].tolist(),
            horizontal=True
        )

    # ================= TAB 3 =================
    with tab3:
        report = {
            "Origin": origin_port,
            "Destination": destination_port,
            "Ship Type": ship_type,
            "Cargo": product_category,
            "Priority": shipment_priority,
            "Base Risk (%)": base_risk
        }

        pdf_buffer = generate_pdf(report)

        st.download_button(
            "📄 Download PDF Report",
            data=pdf_buffer,
            file_name="shipment_risk_report.pdf",
            mime="application/pdf"
        )

    # ================= TAB 4 =================
    with tab4:
        o_lat, o_lon = PORT_COORDS[origin_port]
        d_lat, d_lon = PORT_COORDS[destination_port]

        t = np.linspace(0, 1, 60)
        lats = o_lat + (d_lat - o_lat) * t
        lons = o_lon + (d_lon - o_lon) * t

        idx = int(progress * (len(lats) - 1))

        fig = go.Figure()

        for name, cfg in ROUTE_PROFILES.items():
            fig.add_trace(go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(
                    width=3 if name == selected_route else 2,
                    color=cfg["color"],
                    dash=cfg["dash"]
                ),
                name=name
            ))

        fig.add_trace(go.Scattergeo(
            lat=[lats[idx]],
            lon=[lons[idx]],
            mode="markers+text",
            marker=dict(size=14, color="red"),
            text=[f"🚢 {selected_route}"],
            name="Ship"
        ))

        fig.update_layout(
            geo=dict(
                projection_type="natural earth",
                showcountries=True,
                showocean=True,
                oceancolor="#0b3d91",
                landcolor="#1c1c1c"
            ),
            height=550
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Fill details and click Analyze")

st.caption("CargoGuard AI • Final Hackathon Build")
