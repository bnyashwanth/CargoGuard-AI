import pandas as pd
import pickle
import os
import time
import logging
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# ---------------- LOGGING SETUP ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CargoGuard")

# ---------------- CONFIGURATION ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "ship_details.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

class CargoGuardTrainer:
    def __init__(self, data_path):
        logger.info("Initializing CargoGuard AI Trainer...")
        try:
            self.df = pd.read_csv(data_path)
            self.df.columns = self.df.columns.str.lower().str.strip()
            logger.info(f"Dataset loaded successfully ({len(self.df)} rows).")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def get_pipeline(self, num_cols, cat_cols):
        num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ])
        return ColumnTransformer([
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols)
        ])

    def save_model(self, model_obj, name):
        """Saves any object (Model or Pipeline) to the models directory."""
        path = os.path.join(MODEL_DIR, f"{name}.pkl")
        with open(path, "wb") as f:
            pickle.dump(model_obj, f)
        logger.info(f"Disk Export: {path}")

    def train_risk_anomaly_model(self):
        """Uses Isolation Forest to generate anomaly scores, then trains a regressor to predict them."""
        logger.info("Starting training: [Risk Anomaly Model]...")
        
        cols = ["port_congestion", "sea_traffic_index", "weather_severity"]
        scaler = StandardScaler()
        scaled = scaler.fit_transform(self.df[cols])
        
        iso = IsolationForest(contamination=0.05, random_state=42)
        iso.fit(scaled)
        
        scores = iso.decision_function(scaled)
        # Normalize score to a 0-100 percentage
        self.df["anomaly_percent"] = (1 - (scores - scores.min()) / (scores.max() - scores.min())) * 100
        
        num_fea = ["shipment_distance_km", "total_ports", "port_congestion", "sea_traffic_index", "weather_severity"]
        cat_fea = ["ship_type", "product_category", "origin_port", "destination_port"]
        
        preprocessor = self.get_pipeline(num_fea, cat_fea)
        
        # Create a full pipeline that includes preprocessing and the model
        full_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
        ])
        
        full_pipeline.fit(self.df[num_fea + cat_fea], self.df["anomaly_percent"])
        self.save_model(full_pipeline, "risk_model_pipeline")

    def train_standard_models(self):
        """Trains secondary predictive models including the new Ports Crossed model."""
        
        # Define tasks: target column, features, and model type
        tasks = [
            {
                "name": "sea_traffic_model", 
                "target": "sea_traffic_index", 
                "type": "reg",
                "num": ["shipment_distance_km"],
                "cat": ["ship_type", "origin_port", "destination_port"]
            },
            {
                "name": "weather_model", 
                "target": "weather_severity", 
                "type": "clf",
                "num": ["shipment_distance_km"],
                "cat": ["ship_type", "origin_port", "destination_port"]
            },
            {
                "name": "ports_crossed_model", 
                "target": "ports_crossed", 
                "type": "reg",
                "num": ["shipment_distance_km", "total_ports"],
                "cat": ["ship_type", "origin_port", "destination_port"]
            }
        ]

        for task in tasks:
            logger.info(f"Training Task: {task['name']}...")
            
            preprocessor = self.get_pipeline(task['num'], task['cat'])
            
            if task['type'] == "reg":
                model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

            full_pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model)
            ])

            X = self.df[task['num'] + task['cat']]
            y = self.df[task['target']]
            
            full_pipeline.fit(X, y)
            self.save_model(full_pipeline, task['name'])

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 CARGOGUARD AI UNIFIED TRAINING SYSTEM")
    print("="*50)
    
    start_time = time.time()
    
    try:
        trainer = CargoGuardTrainer(DATA_PATH)
        
        # 1. Train Anomaly Detection
        trainer.train_risk_anomaly_model()
        
        # 2. Train Standard Predictive Models (including Ports Crossed)
        trainer.train_standard_models()
        
        duration = round(time.time() - start_time, 2)
        print("="*50)
        logger.info(f"✨ ALL MODELS INTEGRATED & TRAINED in {duration} seconds.")
        print("="*50 + "\n")
        
    except Exception as fatal_error:
        logger.critical(f"FATAL ERROR: {fatal_error}")


        