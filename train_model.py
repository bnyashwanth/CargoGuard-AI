import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import os
os.makedirs("models", exist_ok=True)
os.makedirs("db", exist_ok=True)


df = pd.read_csv("data/ship_details.csv")
df.columns = df.columns.str.lower().str.strip()

# ---------------- Anomaly Detection ----------------
num_anomaly = ["port_congestion", "sea_traffic_index", "weather_severity"]

scaler = StandardScaler()
scaled = scaler.fit_transform(df[num_anomaly])

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(scaled)

scores = iso.decision_function(scaled)
df["anomaly_percent"] = (1 - (scores - scores.min()) / (scores.max() - scores.min())) * 100
df["anomaly_percent"] = df["anomaly_percent"].round(2)

# ---------------- Risk Model ----------------
num_features = [
    "shipment_distance_km", "route_risk_score",
    "total_ports", "ports_crossed",
    "port_congestion", "sea_traffic_index", "weather_severity"
]

cat_features = [
    "ship_type", "product_category",
    "origin_port", "destination_port",
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

model = RandomForestRegressor(
    n_estimators=80,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

with open("models/pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

with open("models/risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model training complete")
