import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

df = pd.read_csv("dd_18000.csv")
df.columns = df.columns.str.lower().str.strip()

num_att_un = [
    "port_congestion",
    "sea_traffic_index",
    "weather_severity"
]

fea_un = df[num_att_un]

scaler = StandardScaler()
fea_scaled = scaler.fit_transform(fea_un)

iso = IsolationForest(
    n_estimators=40,      
    max_samples=8000,    
    contamination=0.05,
    random_state=42,
    n_jobs=-1           
)
iso.fit(fea_scaled)

labels = iso.predict(fea_scaled)
scores = iso.decision_function(fea_scaled)

df["anomaly_or_fraud"] = ["YES" if x == -1 else "NO" for x in labels]

anomaly_percent = (1 - (scores - scores.min()) /(scores.max() - scores.min())) * 100
df["anomaly_percent"] = anomaly_percent.round(2)

num_att_model = [
    "shipment_distance_km",
    "route_risk_score",
    "total_ports",
    "ports_crossed",
    "port_congestion",
    "sea_traffic_index",
    "weather_severity"
]

cat_att_model = [
    "ship_type",
    "product_category",
    "origin_port",
    "destination_port",
    "shipment_priority"
]

def form_pipeline(num_cols, cat_cols):
    num_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])

    cat_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer([
        ("num", num_pipe, num_cols),
        ("cat", cat_pipe, cat_cols)
    ])

features = df[num_att_model + cat_att_model]
target = df["anomaly_percent"]

pipeline = form_pipeline(num_att_model, cat_att_model)
fea = pipeline.fit_transform(features)

model = RandomForestRegressor(
    n_estimators=50,   
    random_state=42,
    n_jobs=-1          
)

model.fit(fea, target)

user_input = {
    "shipment_distance_km": 6496,
    "route_risk_score": 0.66,
    "total_ports": 4,
    "ports_crossed": 3,
    "port_congestion": 0.59,
    "sea_traffic_index": 0.38,
    "weather_severity": 3,
    "ship_type": "Ro-Ro Ship",
    "product_category": "Chemicals",
    "origin_port": "Tuticorin Port",
    "destination_port": "Chennai Port",
    "shipment_priority": 2
}

user_df = pd.DataFrame([user_input])
user_fea = pipeline.transform(user_df)

pred = model.predict(user_fea)[0]

print(f"Risk Percentage: {round(pred, 2)}%")

if pred <= 30:
    print("Anomaly / Fraud Risk: NO\nStatus: ✅ Safe")
elif pred <= 60:
    print("Anomaly / Fraud Risk: YES\nStatus: ⚠️ Suspicious")
else:
    print("Anomaly / Fraud Risk: YES\nStatus: 🚨 High Risk")


if pred <= 30:
    delay_status = "NO DELAY"
elif pred <= 60:
    delay_status = "POSSIBLE DELAY"
else:
    delay_status = "DELAY LIKELY"

print(f"Delay Status: ⏱️ {delay_status}")
