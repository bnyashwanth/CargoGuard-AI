import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
import bcrypt
import time
import hashlib
from math import radians, cos, sin, asin, sqrt, atan2, degrees, pi
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import pymongo
import random 

# ---------------- 1. CONFIGURATION & MONGODB ----------------
st.set_page_config(page_title="CargoGuard AI | Ultimate", page_icon="🚢", layout="wide")

# REPLACE WITH YOUR MONGO URI
MONGO_URI = "mongodb+srv://Nexen_CargoGuard-AI:nu1CpKr813Oodezn@cluster0.phw7cso.mongodb.net/" 
DB_NAME = "CargoGuardDB"

@st.cache_resource
def init_connection():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info() 
        return client
    except:
        return None

client = init_connection()

if 'mock_db' not in st.session_state:
    st.session_state.mock_db = {
        "users": {},
        "shipments": []
    }

def get_db():
    if client:
        try: return client[DB_NAME]
        except: return None
    return None

# ---------------- 2. CONSTANTS & ZONES ----------------
PORT_DATA = {
    # 🇮🇳 INDIA
    "Mumbai Port": {"coords": (19.0760, 72.8777)},
    "JNPT Port": {"coords": (18.9499, 72.9528)},
    "Kandla Port": {"coords": (23.0339, 70.2204)},
    "Chennai Port": {"coords": (13.0827, 80.2707)},
    "Kolkata Port": {"coords": (22.5726, 88.3639)},
    "Visakhapatnam Port": {"coords": (17.6868, 83.2185)},
    "Cochin Port": {"coords": (9.9312, 76.2673)},
    "Tuticorin Port": {"coords": (8.7642, 78.1348)},
    "Paradip Port": {"coords": (20.3166, 86.6114)},
    "Mangalore Port": {"coords": (12.9141, 74.8560)},

    # 🌏 EAST & SOUTHEAST ASIA
    "Singapore": {"coords": (1.3521, 103.8198)},
    "Shanghai": {"coords": (31.2304, 121.4737)},
    "Ningbo-Zhoushan": {"coords": (29.8683, 121.5440)},
    "Shenzhen": {"coords": (22.5431, 114.0579)},
    "Hong Kong": {"coords": (22.3193, 114.1694)},
    "Busan": {"coords": (35.1796, 129.0756)},
    "Incheon": {"coords": (37.4563, 126.7052)},
    "Tokyo": {"coords": (35.6762, 139.6503)},
    "Yokohama": {"coords": (35.4437, 139.6380)},
    "Kaohsiung": {"coords": (22.6273, 120.3014)},
    "Port Klang": {"coords": (3.0033, 101.4000)},
    "Laem Chabang": {"coords": (13.0820, 100.8830)},
    "Jakarta": {"coords": (-6.2088, 106.8456)},
    "Manila": {"coords": (14.5995, 120.9842)},
    "Ho Chi Minh Port": {"coords": (10.8231, 106.6297)},

    # 🌍 MIDDLE EAST
    "Jebel Ali": {"coords": (24.9857, 55.0273)},
    "Port Rashid": {"coords": (25.2697, 55.2722)},
    "Dammam": {"coords": (26.4207, 50.0888)},
    "Salalah": {"coords": (17.0195, 54.0897)},
    "Hamad Port": {"coords": (25.0350, 51.5480)},
    "Bandar Abbas": {"coords": (27.1865, 56.2808)},

    # 🌍 EUROPE
    "Rotterdam": {"coords": (51.9225, 4.47917)},
    "Hamburg": {"coords": (53.5511, 9.9937)},
    "Antwerp": {"coords": (51.2194, 4.4025)},
    "Bremerhaven": {"coords": (53.5396, 8.5809)},
    "Valencia": {"coords": (39.4699, -0.3763)},
    "Barcelona": {"coords": (41.3851, 2.1734)},
    "Genoa": {"coords": (44.4056, 8.9463)},
    "Piraeus": {"coords": (37.9429, 23.6469)},
    "Le Havre": {"coords": (49.4944, 0.1079)},
    "Felixstowe": {"coords": (51.9634, 1.3510)},

    # 🌍 AFRICA
    "Durban": {"coords": (-29.8587, 31.0218)},
    "Cape Town": {"coords": (-33.9249, 18.4241)},
    "Mombasa": {"coords": (-4.0435, 39.6682)},
    "Dar es Salaam": {"coords": (-6.7924, 39.2083)},
    "Port Said": {"coords": (31.2653, 32.3019)},
    "Alexandria": {"coords": (31.2001, 29.9187)},
    "Lagos": {"coords": (6.5244, 3.3792)},
    "Tema": {"coords": (5.6698, -0.0166)},

    # 🌎 NORTH AMERICA
    "Los Angeles": {"coords": (33.7288, -118.2620)},
    "Long Beach": {"coords": (33.7701, -118.1937)},
    "New York": {"coords": (40.7128, -74.0060)},
    "Newark": {"coords": (40.7357, -74.1724)},
    "Savannah": {"coords": (32.0809, -81.0912)},
    "Charleston": {"coords": (32.7765, -79.9311)},
    "Houston": {"coords": (29.7604, -95.3698)},
    "Vancouver": {"coords": (49.2827, -123.1207)},
    "Prince Rupert": {"coords": (54.3150, -130.3200)},

    # 🌎 CENTRAL & SOUTH AMERICA
    "Panama Canal": {"coords": (9.1012, -79.4029)},
    "Balboa": {"coords": (8.9493, -79.5567)},
    "Manzanillo": {"coords": (19.0500, -104.3167)},
    "Cartagena": {"coords": (10.3910, -75.4794)},
    "Callao": {"coords": (-12.0566, -77.1181)},
    "Santos": {"coords": (-23.9608, -46.3336)},
    "Buenos Aires": {"coords": (-34.6037, -58.3816)},

    # 🌏 OCEANIA
    "Sydney": {"coords": (-33.8688, 151.2093)},
    "Melbourne": {"coords": (-37.8136, 144.9631)},
    "Brisbane": {"coords": (-27.4698, 153.0251)},
    "Fremantle": {"coords": (-32.0569, 115.7439)},
    "Auckland": {"coords": (-36.8485, 174.7633)},
    "Tauranga": {"coords": (-37.6878, 176.1651)}
}


ROUTE_PROFILES = {
    "Primary": {"df": 1.0, "rf": 1.0, "color": "#00BFFF", "dash": "solid", "desc": "Standard Commercial Lane"},
    "Safer": {"df": 1.18, "rf": 0.65, "color": "#00FF7F", "dash": "dot", "desc": "Low-Risk/Patrolled Waters"},
    "Faster": {"df": 0.88, "rf": 1.35, "color": "#FF4500", "dash": "dash", "desc": "High-Speed/High-Traffic"}
}

# FEATURE: PIRATE ZONES
PIRATE_ZONES = [
    {"name": "Gulf of Aden (Piracy High Risk)", "lat": 12.5, "lon": 48.0},
    {"name": "Gulf of Guinea (Kidnapping Risk)", "lat": 3.0, "lon": 5.0},
    {"name": "Sulu Sea (Armed Robbery)", "lat": 6.0, "lon": 120.0}
]

AVG_SPEED_KMPH = 32
COST_PER_KM = 22.50
CO2_PER_KM_TONS = 0.00015 

# ---------------- 3. MATH & UTILS ----------------
def calculate_distance(coord1, coord2):
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 
    return round(c * r, 2)

def solve_great_circle_point(lat1, lon1, lat2, lon2, fraction):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))
    if d == 0: return degrees(lat1), degrees(lon1)
    A = sin((1-fraction)*d) / sin(d)
    B = sin(fraction*d) / sin(d)
    x = A*cos(lat1)*cos(lon1) + B*cos(lat2)*cos(lon2)
    y = A*cos(lat1)*sin(lon1) + B*cos(lat2)*sin(lon2)
    z = A*sin(lat1) + B*sin(lat2)
    lat3 = atan2(z, sqrt(x**2 + y**2))
    lon3 = atan2(y, x)
    return degrees(lat3), degrees(lon3)

def format_duration(days):
    total_hours = days * 24
    if total_hours < 24: return f"{int(total_hours)} hrs"
    else: return f"{int(total_hours // 24)}d {int(total_hours % 24)}h"

# FEATURE: BLOCKCHAIN HASH GENERATOR
def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# FEATURE: SIMULATED WEATHER API
def get_live_weather_sim(port_name):
    base_temps = {"Mumbai": 30, "Chennai": 32, "Rotterdam": 12, "Hamburg": 10, "Singapore": 28, "New York": 15}
    city = port_name.split(" ")[0]
    temp = base_temps.get(city, 20) + random.randint(-3, 3)
    conditions = ["Clear Sky", "Partly Cloudy", "Light Rain", "Hazy", "Windy"]
    cond = conditions[hash(city + str(datetime.now().hour)) % len(conditions)] 
    return {"temp": temp, "condition": cond}

# ---------------- 4. AUTH & DB ----------------
def hash_pass(password): return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
def check_pass(password, hashed): return bcrypt.checkpw(password.encode(), hashed)

def create_user(username, password):
    # Auto-assign name = username since we removed the name field
    name = username 
    
    db = get_db()
    hashed = hash_pass(password)
    user_data = {"username": username, "password": hashed, "name": name}
    
    # FIX: Explicitly check against None
    if db is not None:
        try:
            if db.users.find_one({"username": username}): return False
            db.users.insert_one(user_data)
            return True
        except: return False
    else:
        if username in st.session_state.mock_db["users"]: return False
        st.session_state.mock_db["users"][username] = user_data
        return True

def login_user(username, password):
    db = get_db()
    # FIX: Explicitly check against None
    if db is not None:
        try:
            user = db.users.find_one({"username": username})
            if user and check_pass(password, user['password']): return user
        except: pass
    user = st.session_state.mock_db["users"].get(username)
    if user and check_pass(password, user['password']): return user
    return None

def save_shipment(data):
    db = get_db()
    # FIX: Explicitly check against None
    if db is not None:
        try: db.shipments.insert_one(data); return
        except: pass
    if "_id" not in data: data["_id"] = f"mock_{int(time.time())}"
    st.session_state.mock_db["shipments"].append(data)

def get_user_shipments(username):
    db = get_db()
    # FIX: Explicitly check against None
    if db is not None:
        try: return list(db.shipments.find({"username": username}))
        except: pass
    return [s for s in st.session_state.mock_db["shipments"] if s["username"] == username]

def preload_hackathon_data(username):
    db = get_db()
    # High Risk Demo Shipment (Severe Weather)
    start_date_active = datetime.now() - timedelta(days=5)
    data_1 = {
        "_id": "hackathon_demo_1", "username": username, "origin": "Mumbai Port", "destination": "Rotterdam",
        "status": "In Transit", "start_time": start_date_active, "vessel": "Container Ship", "cargo": "Electronics",
        "risk_score": 88.5, "weather": "Severe Storms", "total_days": 22.0, "route_type": "Primary", "cost": 1500000
    }
    # Low Risk Completed Shipment
    start_date_done = datetime.now() - timedelta(days=30)
    data_2 = {
        "_id": "hackathon_demo_2", "username": username, "origin": "Shanghai", "destination": "Los Angeles",
        "status": "Delivered", "start_time": start_date_done, "vessel": "Bulk Carrier", "cargo": "Raw Materials",
        "risk_score": 15.2, "weather": "Clear", "total_days": 18.0, "route_type": "Faster", "cost": 850000
    }
    # FIX: Explicitly check against None
    if db is not None:
        try:
            if db.shipments.count_documents({"username": username}) == 0:
                del data_1['_id']; del data_2['_id']
                db.shipments.insert_many([data_1, data_2])
        except: pass
    else:
        existing_ids = [s.get('_id') for s in st.session_state.mock_db["shipments"]]
        if "hackathon_demo_1" not in existing_ids: st.session_state.mock_db["shipments"].extend([data_1, data_2])

# ---------------- 5. REPORT GENERATION ----------------
def generate_pro_report(voyage_data, risk_score, status_text, financials, iot_data, chain_hash):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- HEADER ---
    p.setFillColor(colors.HexColor("#001f3f"))
    p.rect(0, height-100, width, 100, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 26)
    p.drawString(40, height-50, "CARGOGUARD AI")
    p.setFont("Helvetica", 10)
    p.drawString(40, height-70, "INTELLIGENT MARITIME RISK & LOGISTICS ANALYSIS")
    
    # --- 1. VOYAGE SPECIFICATIONS (Left Column) ---
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height-140, "VOYAGE SPECIFICATIONS")
    
    y_pos = height - 160
    p.setFont("Helvetica", 10)
    for key, value in voyage_data.items():
        p.drawString(40, y_pos, f"{key}:")
        p.drawString(160, y_pos, str(value))
        y_pos -= 20
        
    # --- 2. FINANCIAL & ENVIRONMENTAL (Right Column) ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(320, height-140, "LOGISTICS METRICS")
    
    y_pos_right = height - 160
    p.setFont("Helvetica", 10)
    for key, value in financials.items():
        p.drawString(320, y_pos_right, f"{key}:")
        p.drawString(420, y_pos_right, str(value))
        y_pos_right -= 20

    # --- LINE SEPARATOR ---
    p.setStrokeColor(colors.lightgrey)
    p.line(40, y_pos - 20, width-40, y_pos - 20)
    current_y = y_pos - 50

    # --- 3. IOT TELEMETRY & BLOCKCHAIN ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, current_y, "DIGITAL TWIN & LEDGER VERIFICATION")
    
    p.setFont("Helvetica", 10)
    p.drawString(40, current_y - 25, f"Live Container Temp: {iot_data['temp']}")
    p.drawString(40, current_y - 45, f"Reefer Status: {iot_data['status']}")
    
    p.drawString(320, current_y - 25, "Latest Ledger Hash (Immutable):")
    p.setFont("Courier", 8)
    p.drawString(320, current_y - 45, chain_hash[:35] + "...")

    # --- 4. FINAL SECURITY ASSESSMENT (Footer Box) ---
    # Determine box color based on risk
    box_color = colors.HexColor("#c0392b") if risk_score > 70 else colors.HexColor("#f39c12") if risk_score > 35 else colors.HexColor("#27ae60")
    
    p.setFillColor(box_color)
    p.roundRect(40, current_y - 130, 530, 60, 8, stroke=0, fill=1)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, current_y - 105, "FINAL SECURITY ASSESSMENT")
    p.setFont("Helvetica", 12)
    p.drawString(60, current_y - 122, f"Risk Probability: {risk_score}%  |  Status: {status_text}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# ---------------- 6. CHARTS & STYLES ----------------
def create_gauge_chart(value, label, color_theme):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, title={'text': label, 'font': {'size': 20, 'color': 'white'}},
        gauge={'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "gray"},
               'bar': {'color': "white"}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "gray",
               'steps': [{'range': [0, 35], 'color': "#27ae60"}, {'range': [35, 70], 'color': "#f39c12"}, {'range': [70, 100], 'color': "#c0392b"}]}
    ))
    fig.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1c24; color: white; border: 1px solid #2d2e35; }
    .metric-card { background-color: #1a1c24; border: 1px solid #2d2e35; border-radius: 8px; padding: 15px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-value { font-size: 24px; font-weight: 700; color: #ffffff; }
    .metric-label { font-size: 12px; color: #a0a0a0; text-transform: uppercase; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .status-box { padding: 20px; border-radius: 10px; margin-bottom: 25px; text-align: center; font-weight: 800; font-size: 18px; letter-spacing: 1px; }
    .ai-insight { background-color: #1e293b; border-left: 4px solid #00BFFF; padding: 15px; border-radius: 4px; margin-top: 20px; font-size: 14px; color: #e2e8f0; }
    .blockchain-box { font-family: 'Courier New', monospace; font-size: 12px; color: #00FF7F; background: #000; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #0e1117; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #1a1c24; border-bottom: 2px solid #00BFFF; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 7. MAIN LOGIC ----------------

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Login"
if 'selected_shipment' not in st.session_state: st.session_state.selected_shipment = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

# --- A. LOGIN PAGE ---
# --- A. LOGIN PAGE ---
# --- A. LOGIN PAGE ---
if st.session_state.page == "Login":
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🚢 CargoGuard AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Enterprise Logistics Intelligence</p>", unsafe_allow_html=True)
        
        # Connection Status Check
        if client is None:
            st.warning("⚠️ Database not connected. Using offline mode.")

        tab1, tab2 = st.tabs(["Login", "Register"])
        
        # --- LOGIN TAB (Inside Form) ---
        with tab1:
            with st.form("login_form"):
                l_user = st.text_input("Username", key="l_u")
                l_pass = st.text_input("Password", type="password", key="l_p")
                # The script won't reload until this button is clicked
                login_submitted = st.form_submit_button("Log In", use_container_width=True)
                
                if login_submitted:
                    user = login_user(l_user, l_pass)
                    if user:
                        st.session_state.user = user
                        preload_hackathon_data(l_user) 
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    else: 
                        st.error("Invalid credentials")

        # --- REGISTER TAB (Inside Form) ---
        with tab2:
            with st.form("register_form"):
                st.write("Create a New Account")
                r_user = st.text_input("Choose Username")
                r_pass = st.text_input("Choose Password", type="password")
                # The script won't reload until this button is clicked
                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if reg_submitted:
                    if r_user and r_pass:
                        if create_user(r_user, r_pass): 
                            st.success("Account created! Please log in.")
                        else: 
                            st.error("Username already exists or DB Error.")
                    else:
                        st.error("Please fill in both fields.")
# --- B. APP AREA ---
elif st.session_state.user:
    # SIDEBAR WITH AI CHAT
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2942/2942544.png", width=60)
        st.write(f"Welcome, **{st.session_state.user['name']}**")
        st.divider()
        if st.button("📊 Fleet Dashboard", use_container_width=True): st.session_state.page = "Dashboard"; st.rerun()
        if st.button("➕ New Shipment", use_container_width=True): st.session_state.page = "New"; st.rerun()
        
        st.divider()
        st.caption("🤖 Logistics Assistant")
        user_query = st.text_input("Ask AI...", placeholder="Where is my ship?")
        if user_query:
            st.session_state.chat_history.append(f"You: {user_query}")
            # Simple Rule-Based AI
            if "where" in user_query.lower(): response = "AI: Tracking 2 active vessels in transit."
            elif "risk" in user_query.lower(): response = "AI: Alert! High risk detected near Gulf of Aden."
            else: response = "AI: I am calculating route parameters..."
            st.session_state.chat_history.append(response)
        
        for msg in st.session_state.chat_history[-4:]:
            st.caption(msg)
            
        st.divider()
        if st.button("Log Out"): st.session_state.user = None; st.session_state.page = "Login"; st.rerun()

    # --- C. DASHBOARD ---
    if st.session_state.page == "Dashboard":
        st.title("📊 Fleet Overview")
        shipments = get_user_shipments(st.session_state.user['username'])
        if not shipments: st.info("No active shipments found.")
        else:
            active_count = sum(1 for s in shipments if s['status'] == 'In Transit')
            total_cost = sum(s.get('cost', 0) for s in shipments)
            c1, c2, c3 = st.columns(3)
            c1.metric("Active Vessels", active_count)
            c2.metric("Total Logistics Spend", f"₹{total_cost:,.0f}")
            c3.metric("Fleet Health", "98.2%")
            st.subheader("Live Tracking Feed")
            
            for i, s in enumerate(shipments):
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
                    start = s['start_time']; now = datetime.now(); duration = timedelta(days=s['total_days'])
                    elapsed = now - start
                    progress = 1.0 if s['status'] == "Delivered" else min(1.0, elapsed / duration)
                    status_color = "#27ae60" if s['status'] == "Delivered" else "#f39c12"
                    disp_id = str(s.get('_id', f'DEMO-{i}'))[-6:]
                    
                    with col1: st.write(f"**{s['origin']} ➝ {s['destination']}**"); st.caption(f"ID: {disp_id}")
                    with col2: st.write(f"📅 Start: {start.strftime('%d %b')}"); st.caption(f"Vessel: {s['vessel']}")
                    with col3: st.write(f"Risk: {s.get('risk_score', 0)}%")
                    with col4: st.markdown(f"<span class='status-badge' style='background:{status_color};color:{'white' if status_color=='#27ae60' else 'black'};'>{s['status']}</span>", unsafe_allow_html=True); st.progress(progress)
                    with col5:
                        if st.button("📡 Track Live", key=f"btn_{i}_{disp_id}"):
                            st.session_state.selected_shipment = s
                            st.session_state.active_route = s.get('route_type', 'Primary')
                            st.session_state.page = "Tracking"
                            st.rerun()
                    st.divider()

    # --- D. TRACKING (FEATURE RICH) ---
    elif st.session_state.page == "Tracking":
        s = st.session_state.selected_shipment
        if not s: st.session_state.page = "Dashboard"; st.rerun()
        if st.button("← Back to Fleet"): st.session_state.page = "Dashboard"; st.rerun()

        st.title(f"📡 Mission Control: {s['origin']} ➝ {s['destination']}")
        
        # Recalculate Logic
        base_dist = calculate_distance(PORT_DATA[s['origin']]['coords'], PORT_DATA[s['destination']]['coords'])
        risk_score = s['risk_score'] 
        computed_data = []
        for name, profile in ROUTE_PROFILES.items():
            actual_dist = base_dist * profile['df']
            rf_mult = profile.get('rf', 1.0)
            adj_risk = min(99.9, round(risk_score * rf_mult, 2))
            total_duration = ((actual_dist / AVG_SPEED_KMPH) / 24) + ((adj_risk / 100) * 4)
            cost = actual_dist * COST_PER_KM
            # FEATURE: CO2 & INSURANCE
            co2 = actual_dist * CO2_PER_KM_TONS
            insurance = (cost * 0.01) + (adj_risk * 1500) 
            computed_data.append({
                "Route": name, "Distance (km)": int(actual_dist), "Risk (%)": adj_risk,
                "Duration Str": format_duration(total_duration), "Cost (INR)": int(cost),
                "CO2 (Tons)": round(co2, 1), "Insurance ($)": int(insurance), "Type": profile['desc']
            })
        results_df = pd.DataFrame(computed_data)
        
        # Tabs
        tabs = st.tabs(["🛡 Risk Command", "🌍 Global 3D Tracking", "📈 Comparative Matrix", "🌡️ IoT Digital Twin", "🔗 Blockchain Ledger"])
        
        # TAB 1: RISK COMMAND
        # TAB 1: RISK COMMAND
        with tabs[0]:
            # --- 1. Calculate Risk Status ---
            active_row = results_df[results_df.Route == st.session_state.active_route].iloc[0]
            curr_risk = active_row["Risk (%)"]
            stat_msg, stat_col = ("OPERATIONAL", "#27ae60") if curr_risk < 35 else ("CAUTION", "#f39c12") if curr_risk < 70 else ("CRITICAL - HIGH RISK", "#c0392b")
            
            # --- 2. Display Status Header ---
            st.markdown(f'<div class="status-box" style="background-color: {stat_col}22; border: 2px solid {stat_col}; color: {stat_col};">{stat_msg}</div>', unsafe_allow_html=True)
            
            # --- 3. Main Layout ---
            col_left, col_right = st.columns([1.2, 2])
            
            with col_left:
                st.plotly_chart(create_gauge_chart(curr_risk, "Risk Index", stat_col), use_container_width=True)
                
                # Weather Simulation
                weather_data = get_live_weather_sim(s['origin'])
                st.markdown(f"""<div class="ai-insight"><strong>🤖 AI Brief:</strong> Live weather: <b>{weather_data['condition']} ({weather_data['temp']}°C)</b>. Risk impacts analyzed.</div>""", unsafe_allow_html=True)
                
                # Alert Button
                if curr_risk > 40 and s['status'] == 'In Transit':
                    if st.button("🚨 Broadcast Encrypted Alert", use_container_width=True, type="primary"):
                         st.success("SATCOM Alert Sent to Captain.")

            with col_right:
                # Metrics Grid (Financials & CO2)
                m1, m2 = st.columns(2)
                with m1: st.markdown(f"""<div class="metric-card"><div class="metric-label">💰 Cost</div><div class="metric-value">₹{active_row['Cost (INR)']:,}</div></div>""", unsafe_allow_html=True)
                with m2: st.markdown(f"""<div class="metric-card"><div class="metric-label">⏱️ Duration</div><div class="metric-value">{active_row['Duration Str']}</div></div>""", unsafe_allow_html=True)
                st.write("")
                m3, m4 = st.columns(2)
                with m3: st.markdown(f"""<div class="metric-card"><div class="metric-label">🌿 Est. CO2</div><div class="metric-value">{active_row['CO2 (Tons)']} t</div></div>""", unsafe_allow_html=True)
                with m4: st.markdown(f"""<div class="metric-card"><div class="metric-label">⚓ Stops</div><div class="metric-value">{int(s.get('total_days', 20)/5)}</div></div>""", unsafe_allow_html=True)
                
                st.write("---")
                
                # --- 4. PREPARE DATA FOR REPORT ---
                # A. Basic Voyage Data
                est_arrival = s['start_time'] + timedelta(days=s['total_days'])
                voyage_data = {
                    "Tracking ID": str(s.get('_id', 'N/A'))[-6:],
                    "Origin Port": s['origin'],
                    "Destination Port": s['destination'],
                    "Ship Type": s['vessel'],
                    "Cargo Type": s['cargo'],
                    "Selected Route": s.get('route_type', 'Primary'),
                    "Total Distance": f"{active_row['Distance (km)']} km",
                    "Est. Arrival": est_arrival.strftime("%Y-%m-%d"),
                }
                
                # B. Financials (from screenshots: Decision Matrix data)
                financial_data = {
                    "Total Cost": f"INR {active_row['Cost (INR)']:,}",
                    "Insurance Prem": f"$ {active_row['Insurance ($)']:,}",
                    "Carbon Footprint": f"{active_row['CO2 (Tons)']} Tons",
                    "Transit Stops": f"{int(s.get('total_days', 20)/5)} Ports"
                }

                # C. IoT Data (Simulating the tab data for the report)
                base_temp_rpt = -18 if s['cargo'] == "Perishables" else 22
                cur_temp_rpt = base_temp_rpt + np.random.normal(0, 0.5)
                iot_data_rpt = {
                    "temp": f"{cur_temp_rpt:.1f}°C",
                    "status": "STABLE" if abs(cur_temp_rpt - base_temp_rpt) < 2 else "WARNING"
                }

                # D. Blockchain Data (Simulating the latest hash)
                mock_hash = hashlib.sha256(f"{s['_id']}{datetime.now()}".encode()).hexdigest()

                # --- 5. GENERATE & DOWNLOAD ---
                pdf_buffer = generate_pro_report(
                    voyage_data, 
                    curr_risk, 
                    stat_msg, 
                    financial_data, 
                    iot_data_rpt, 
                    mock_hash
                )

                st.download_button(
                    label="📄 Download Full Mission Report",
                    data=pdf_buffer,
                    file_name=f"CargoGuard_Mission_Report_{s.get('_id', 'draft')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        # TAB 2: GLOBE
        # TAB 2: GLOBE
        with tabs[1]:
            st.subheader(f"🌍 Live 3D Tracking: {s['origin']} ➝ {s['destination']}")

            # --- 1. ADVANCED ROUTING ENGINE (Hardcoded for Demo Perfection) ---
            # --- 1. ENTERPRISE ROUTING ENGINE (Valid for ALL Ports) ---
            def get_advanced_route(origin_name, dest_name, route_type):
                # 1. Get Coordinates from your PORT_DATA dictionary
                o_lat, o_lon = PORT_DATA[origin_name]['coords']
                d_lat, d_lon = PORT_DATA[dest_name]['coords']
                
                waypoints = [(o_lat, o_lon)]

                # --- A. DEFINE CHOKE POINTS (The "Gates" of the Ocean) ---
                # These are the critical lat/lon points ships MUST pass through
                WP_SUEZ = [(12.5, 43.5), (29.9, 32.5), (36.0, -5.5)] # Red Sea -> Med -> Gibraltar
                WP_PANAMA = [(9.0, -79.5)] # Panama Canal
                WP_MALACCA = [(5.5, 95.0), (1.2, 103.8)] # Singapore Strait
                WP_CAPE_GOOD_HOPE = [(-35.0, 20.0)] # Tip of Africa

                # --- B. DEMO OVERRIDES (Keep these perfect for your pitch!) ---
                # These match your exact requirements for the Hackathon demo scenarios
                if "Mumbai" in origin_name and "Rotterdam" in dest_name:
                    if route_type == "Primary": return [(18.9, 72.9), (14.0, 60.0), (12.5, 43.5), (29.9, 32.5), (36.0, -5.5), (49.0, -5.0), (51.9, 4.0)]
                    elif route_type == "Safer": return [(18.9, 72.9), (18.0, 65.0), (12.2, 44.0), (29.9, 32.6), (36.1, -5.4), (49.5, -6.0), (51.9, 4.0)]
                    elif route_type == "Faster": return [(18.9, 72.9), (13.5, 55.0), (11.8, 44.0), (29.9, 32.4), (35.9, -5.4), (48.8, -4.8), (51.9, 4.0)]
                elif "Mumbai" in origin_name and "Brisbane" in dest_name:
                    if route_type == "Primary": return [(18.9, 72.9), (5.5, 95.0), (1.2, 103.8), (-5.0, 115.0), (-10.5, 140.0), (-27.0, 153.5)]
                    elif route_type == "Faster": return [(18.9, 72.9), (0.0, 85.0), (-6.0, 105.0), (-9.0, 126.0), (-27.0, 153.5)]
                    elif route_type == "Safer": return [(18.9, 72.9), (2.0, 78.0), (1.2, 103.8), (-12.0, 125.0), (-27.0, 153.5)]

                # --- C. SMART DETECTION LOGIC (For any other random port pair) ---
                
                # 1. SUEZ ROUTE DETECTION (Europe <-> Asia/Oceania/East Africa)
                # Logic: One port is in Europe (Lat > 30, Lon -20 to 40) AND other is Asia/Aus (Lon > 60)
                is_europe = (o_lat > 30 and -20 < o_lon < 40) or (d_lat > 30 and -20 < d_lon < 40)
                is_asia_east = (o_lon > 60) or (d_lon > 60)
                
                if is_europe and is_asia_east:
                    # Force route through Suez
                    waypoints.extend(WP_SUEZ)
                    # If going far East (China/Japan), add Malacca too to avoid cutting through India/Thailand land
                    if (o_lon > 100 or d_lon > 100):
                        waypoints.extend(WP_MALACCA)

                # 2. PANAMA ROUTE DETECTION (Atlantic <-> Pacific)
                # Logic: One port is Atlantic (Lon > -100 and < 20) AND other is Pacific (Lon < -100 or > 120)
                # Ex: New York (-74) to Tokyo (139) or Los Angeles (-118)
                is_atlantic = (-100 < o_lon < 20) or (-100 < d_lon < 20)
                is_pacific_dest = (o_lon < -100 or o_lon > 120) or (d_lon < -100 or d_lon > 120)

                if is_atlantic and is_pacific_dest:
                    waypoints.extend(WP_PANAMA)

                # 3. ATLANTIC CROSSING (Americas <-> Europe/Africa)
                # Simple Midpoint Curve so lines don't look flat
                elif (o_lon < -30 and d_lon > -30) or (o_lon > -30 and d_lon < -30):
                    mid_lat = (o_lat + d_lat) / 2
                    # Bias: Curve slightly North for "Great Circle" effect
                    waypoints.append((mid_lat + 10, -35.0))

                # --- D. APPLY OFFSETS FOR "3 ALTERNATE ROUTES" ---
                # This ensures your 3 lines don't overlap, even on generic routes
                final_path = []
                lat_offset = 0
                if route_type == "Safer": lat_offset = 2.0  # Shift North/Up for visibility
                if route_type == "Faster": lat_offset = -2.0 # Shift South/Down for visibility

                for pt in waypoints:
                    final_path.append((pt[0] + lat_offset, pt[1]))

                final_path.append((d_lat, d_lon))
                return final_path

            # --- 2. LOGIC TO TRACK SHIP POSITION ---
            # We treat the route as a set of connected lines
            active_path_pts = get_advanced_route(s['origin'], s['destination'], st.session_state.active_route)
            
            # Simple interpolation for the ship icon based on time
            # 0% = Start, 100% = End. We find which segment the ship is on.
            total_segments = len(active_path_pts) - 1
            start_time = s['start_time']; now = datetime.now()
            
            if s['status'] == 'Delivered': 
                prog = 1.0; label_status = "Arrived"
            elif start_time > now: 
                prog = 0.0; label_status = "Scheduled"
            else:
                elapsed = (now - start_time).total_seconds() / 86400
                prog = min(0.99, elapsed / s['total_days'])
                label_status = "In Transit"

            # Find specific lat/lon
            seg_index = int(prog * total_segments)
            seg_percent = (prog * total_segments) - seg_index
            
            p1 = active_path_pts[seg_index]
            p2 = active_path_pts[min(seg_index + 1, total_segments)]
            
            # Linear interpolation for ship marker
            curr_lat = p1[0] + (p2[0] - p1[0]) * seg_percent
            curr_lon = p1[1] + (p2[1] - p1[1]) * seg_percent

            # --- 3. PLOTTING ---
            fig = go.Figure()

            # A. Draw All 3 Routes (Curved & Separated)
            for r_name, profile in ROUTE_PROFILES.items():
                pts = get_advanced_route(s['origin'], s['destination'], r_name)
                lats, lons = zip(*pts)
                
                # We use 'spline' line_shape to smooth the hardcoded points!
                fig.add_trace(go.Scattergeo(
                    lat=lats, lon=lons, mode='lines',
                    line=dict(width=3 if r_name == st.session_state.active_route else 2, 
                              color=profile['color'], dash=profile['dash']),
                    name=f"{r_name} Route",
                    opacity=1.0 if r_name == st.session_state.active_route else 0.5
                ))

            # B. Ports
            o_c = PORT_DATA[s['origin']]['coords']
            d_c = PORT_DATA[s['destination']]['coords']
            fig.add_trace(go.Scattergeo(
                lat=[o_c[0], d_c[0]], lon=[o_c[1], d_c[1]],
                mode='markers+text', text=[s['origin'], s['destination']],
                marker=dict(size=12, color='#39FF14', symbol='diamond'),
                textposition="bottom center", name="Ports"
            ))

            # C. The Ship
            fig.add_trace(go.Scattergeo(
                lat=[curr_lat], lon=[curr_lon],
                mode='markers+text', text=[f"🚢 {label_status}"],
                textposition="top center",
                marker=dict(size=22, color='white', symbol='circle', line=dict(width=3, color='cyan')),
                name="Vessel"
            ))
            
            # D. Zones (Context)
            for zone in PIRATE_ZONES:
                 fig.add_trace(go.Scattergeo(lat=[zone["lat"]], lon=[zone["lon"]], mode='markers', marker=dict(size=20, color='red', opacity=0.3), name=f"⚠️ {zone['name']}", hoverinfo="name"))

            fig.update_layout(
                height=600, margin={"r":0,"t":0,"l":0,"b":0}, 
                paper_bgcolor="#0e1117", 
                geo=dict(
                    projection_type="orthographic", 
                    showland=True, landcolor="#1e293b", 
                    showocean=True, oceancolor="#0f172a", 
                    showcountries=True, countrycolor="#334155",
                    center=dict(lat=curr_lat, lon=curr_lon),
                    projection_rotation=dict(lon=curr_lon, lat=curr_lat)
                ),
                font=dict(color='white'),
                legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        # TAB 3: MATRIX
        with tabs[2]:
            st.subheader("📊 Decision Matrix")
            display_cols = ['Route', 'Risk (%)', 'Duration Str', 'Cost (INR)', 'Insurance ($)', 'CO2 (Tons)', 'Type']
            def style_risk(v): return f'color: {"#27ae60" if v < 40 else "#f39c12" if v < 70 else "#c0392b"}; font-weight: bold'
            st.dataframe(results_df[display_cols].style.map(style_risk, subset=['Risk (%)']).format({"Cost (INR)": "₹{:,.0f}", "Insurance ($)": "${:,.0f}", "Risk (%)": "{:.1f}%"}), use_container_width=True, hide_index=True)
            st.write("---")
            st.session_state.active_route = st.radio("Select Strategy:", results_df["Route"].tolist(), horizontal=True, index=results_df["Route"].tolist().index(st.session_state.active_route) if st.session_state.active_route in results_df["Route"].tolist() else 0)

        # TAB 4: IOT TWIN (NEW)
        with tabs[3]:
            st.subheader("🌡️ Reefer Container Telemetry")
            c1, c2 = st.columns([3, 1])
            with c1:
                # Simulate data
                days_elapsed = int((datetime.now() - s['start_time']).total_seconds() / 86400) + 1
                data_points = max(10, days_elapsed * 6)
                base_temp = -18 if s['cargo'] == "Perishables" else 22
                temps = [base_temp + np.random.normal(0, 0.5) for _ in range(data_points)]
                times = [s['start_time'] + timedelta(hours=4*i) for i in range(data_points)]
                
                fig_iot = go.Figure()
                fig_iot.add_trace(go.Scatter(x=times, y=temps, mode='lines', line=dict(color='#00BFFF', width=2), fill='tozeroy', name="Temp"))
                fig_iot.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'))
                st.plotly_chart(fig_iot, use_container_width=True)
            with c2:
                curr_t = temps[-1]
                st.metric("Live Temp", f"{curr_t:.1f}°C", delta=f"{curr_t - temps[-2]:.1f}")
                status = "STABLE" if curr_t < base_temp + 2 else "WARNING"
                color = "green" if status == "STABLE" else "red"
                st.markdown(f"<div style='background:{color};padding:10px;border-radius:5px;text-align:center;'>{status}</div>", unsafe_allow_html=True)

        # TAB 5: BLOCKCHAIN (NEW)
        with tabs[4]:
            st.subheader("🔗 Proof of Transit Ledger (Immutable)")
            events = [
                f"Cargo Loaded at {s['origin']} | {s['start_time'].strftime('%Y-%m-%d %H:%M')}",
                f"Customs Clearance Verified | ID: {str(s.get('_id'))[-4:]}",
                f"IoT Sensor Activation | {s['start_time'].strftime('%Y-%m-%d %H:%M')}",
                f"Risk Analysis Computation | Risk Score: {risk_score}",
                f"Current Status: {s['status']} | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ]
            for evt in events:
                block_hash = generate_hash(evt)
                st.markdown(f"**Event:** {evt}")
                st.markdown(f"<div class='blockchain-box'>HASH: {block_hash}</div>", unsafe_allow_html=True)
                st.write("---")

    # --- E. NEW SHIPMENT ---
    elif st.session_state.page == "New":
        st.title("➕ Plan New Shipment")
        if st.button("← Back"): st.session_state.page = "Dashboard"; st.rerun()
        with st.expander("🚢 Voyage Parameters", expanded=True):
            vessel = st.selectbox("Vessel Type", ['Container Ship', 'Bulk Carrier', 'Oil Tanker'])
            cargo = st.selectbox("Cargo", ['Electronics', 'Industrial', 'Chemicals'])
            origin = st.selectbox("Origin", list(PORT_DATA.keys()))
            dest = st.selectbox("Destination", list(PORT_DATA.keys()), index=1)
            weight = st.number_input("Weight (Tons)", 100, 50000, 5000)
            
        if st.button("🚀 Analyze & Save Shipment"):
            if origin == dest: st.error("Origin and Destination cannot be same")
            else:
                with st.spinner("Calculating..."):
                    dist = calculate_distance(PORT_DATA[origin]['coords'], PORT_DATA[dest]['coords'])
                    risk = 35.5 
                    cost = dist * 22.5
                    new_data = {
                        "username": st.session_state.user['username'], "origin": origin, "destination": dest,
                        "status": "In Transit", "start_time": datetime.now(), "vessel": vessel, "cargo": cargo,
                        "risk_score": risk, "weather": "Clear", "total_days": (dist/AVG_SPEED_KMPH)/24,
                        "route_type": "Primary", "cost": cost
                    }
                    save_shipment(new_data)
                    st.success("Shipment dispatched! Redirecting...")
                    time.sleep(1)
                    st.session_state.page = "Dashboard"
                    st.rerun()