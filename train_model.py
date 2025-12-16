import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

df = pd.read_csv("ship_details.csv")
df.columns = df.columns.str.lower().str.strip()

num_att_un = ["port_congestion", "sea_traffic_index", "weather_severity"]

scaler = StandardScaler()
fea_scaled = scaler.fit_transform(df[num_att_un])

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(fea_scaled)

scores = iso.decision_function(fea_scaled)
df["anomaly_percent"] = (
    1 - (scores - scores.min()) / (scores.max() - scores.min())
) * 100
df["anomaly_percent"] = df["anomaly_percent"].round(2)

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

num_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler())
])

cat_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=True))
])

pipeline = ColumnTransformer([
    ("num", num_pipe, num_att_model),
    ("cat", cat_pipe, cat_att_model)
])

X = pipeline.fit_transform(df[num_att_model + cat_att_model])
y = df["anomaly_percent"]

model = RandomForestRegressor(
    n_estimators=50,
    random_state=42,
    n_jobs=-1
)
model.fit(X, y)

with open("pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

with open("risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Training complete. Model and pipeline saved.")
