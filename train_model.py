import pandas as pd
import pickle
import os

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "ship_details.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.lower().str.strip()

# ---------------- ANOMALY DETECTION ----------------
num_anomaly = ["port_congestion", "sea_traffic_index", "weather_severity"]

scaler = StandardScaler()
scaled = scaler.fit_transform(df[num_anomaly])

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(scaled)

scores = iso.decision_function(scaled)
df["anomaly_percent"] = (
    1 - (scores - scores.min()) / (scores.max() - scores.min())
) * 100
df["anomaly_percent"] = df["anomaly_percent"].round(2)

# ---------------- FEATURE PIPELINE ----------------
num_features = [
    "shipment_distance_km",
    "route_risk_score",
    "total_ports",
    "ports_crossed",
    "port_congestion",
    "sea_traffic_index",
    "weather_severity"
]

cat_features = [
    "ship_type",
    "product_category",
    "origin_port",
    "destination_port",
    "shipment_priority"
]

num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

pipeline = ColumnTransformer([
    ("num", num_pipe, num_features),
    ("cat", cat_pipe, cat_features)
])

X = pipeline.fit_transform(df[num_features + cat_features])
y = df["anomaly_percent"]

# ---------------- MODEL ----------------
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

# ---------------- SAVE MODELS ----------------
with open(os.path.join(MODEL_DIR, "pipeline.pkl"), "wb") as f:
    pickle.dump(pipeline, f)

with open(os.path.join(MODEL_DIR, "risk_model.pkl"), "wb") as f:
    pickle.dump(model, f)

print("✅ Training complete. Models saved to /models")
