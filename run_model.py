import streamlit as st
import pandas as pd
import pickle

# --- 1. CONFIGURATION (Must be the first command) ---
st.set_page_config(
    page_title="Maritime Risk Predictor",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LOAD MODEL ---
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
    st.error("Error: .pkl files not found. Run train_model.py first.")
    st.stop()

# --- 3. UI LAYOUT ---
st.title("🚢 Maritime Shipment Risk Predictor")
st.markdown("### Enter shipment details to predict anomaly risk")

with st.form("prediction_form"):
    st.write("#### 📋 Shipment Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Numeric Inputs
        shipment_distance_km = st.number_input("Distance (km)", min_value=0.0, step=10.0)
        route_risk_score = st.slider("Route Risk Score", 0.0, 1.0, step=0.01)
        total_ports = st.number_input("Total Ports", min_value=1, step=1)
        ports_crossed = st.number_input("Ports Crossed", min_value=0, step=1)
        port_congestion = st.slider("Port Congestion Level", 0.0, 1.0, step=0.01)

    with col2:
        sea_traffic_index = st.slider("Sea Traffic Index", 0.0, 1.0, step=0.01)
        weather_severity = st.slider("Weather Severity (1-5)", 1, 5, step=1)
        shipment_priority = st.selectbox("Shipment Priority", [1, 2, 3], help="1=Low, 3=High")

    st.write("#### 📦 Categorical Details")
    col3, col4 = st.columns(2)

    with col3:
        # DROPDOWNS: Replace these lists with your actual CSV data
        ship_type = st.selectbox(
            "Ship Type", 
            ["Container Ship", "Bulk Carrier", "Tanker", "Ro-Ro", "General Cargo"]
        )
        
        product_category = st.selectbox(
            "Product Category", 
            ["Electronics", "Machinery", "Textiles", "Chemicals", "Food", "Automotive"]
        )

    with col4:
        origin_port = st.selectbox(
            "Origin Port", 
            ["Shanghai", "Singapore", "Ningbo", "Busan", "Rotterdam", "Mumbai"]
        )
        
        destination_port = st.selectbox(
            "Destination Port", 
            ["Rotterdam", "Antwerp", "Los Angeles", "Hamburg", "New York", "Chennai"]
        )

    # Submit Button
    submit_btn = st.form_submit_button("🚀 Analyze Risk")

# --- 4. PREDICTION LOGIC ---
if submit_btn:
    # Prepare input dict
    u_input = {
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
    }

    user_df = pd.DataFrame(u_input)

    try:
        user_fea = pipeline.transform(user_df)
        pred = model.predict(user_fea)[0]
        risk_score = round(pred, 2)

        st.divider()
        st.subheader(f"Risk Assessment: {risk_score}%")
        
        if risk_score <= 30:
            st.success("✅ Safe (Low Risk) - No Delay Expected")
        elif risk_score <= 60:
            st.warning("⚠️ Suspicious (Medium Risk) - Possible Delay")
        else:
            st.error("🚨 High Risk (Anomaly Detected) - Delay Likely")

    except Exception as e:
        st.error(f"Prediction Error: {e}")