import pandas as pd
import pickle

pipeline = pickle.load(open("pipeline.pkl", "rb"))
model = pickle.load(open("risk_model.pkl", "rb"))

shipment_distance_km = input("Enter total shipment distance in kilometers: ")
route_risk_score = input("Enter route risk score (0 to 1): ")
carrier_rating = input("Enter carrier rating (1 to 5): ")
total_ports = input("Enter total number of ports involved: ")
ports_crossed = input("Enter number of ports crossed: ")
port_congestion = input("Enter port congestion level (0 to 1): ")
sea_traffic_index = input("Enter sea traffic index (0 to 1): ")
weather_severity = input("Enter weather severity level: ")
ship_type = input("Enter ship type: ")
product_category = input("Enter product category: ")
origin_port = input("Enter origin port: ")
destination_port = input("Enter destination port: ")
carrier_name = input("Enter carrier name: ")
shipment_priority = input("Enter shipment priority level: ")

inputs = [
    shipment_distance_km, route_risk_score, carrier_rating,
    total_ports, ports_crossed, port_congestion,
    sea_traffic_index, weather_severity,
    ship_type, product_category, origin_port,
    destination_port, carrier_name, shipment_priority
]

if "" in inputs:
    print("Error: Please fill ALL the fields. No field should be empty.")
else:
    try:
        values = [
            float(shipment_distance_km),
            float(route_risk_score),
            float(carrier_rating),
            int(total_ports),
            int(ports_crossed),
            float(port_congestion),
            float(sea_traffic_index),
            int(weather_severity),
            ship_type,
            product_category,
            origin_port,
            destination_port,
            carrier_name,
            int(shipment_priority)
        ]

        u_input = {
            "shipment_distance_km": [values[0]],
            "route_risk_score": [values[1]],
            "carrier_rating": [values[2]],
            "total_ports": [values[3]],
            "ports_crossed": [values[4]],
            "port_congestion": [values[5]],
            "sea_traffic_index": [values[6]],
            "weather_severity": [values[7]],
            "ship_type": [values[8]],
            "product_category": [values[9]],
            "origin_port": [values[10]],
            "destination_port": [values[11]],
            "carrier_name": [values[12]],
            "shipment_priority": [values[13]]
        }

        user_df = pd.DataFrame(u_input)
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

    except ValueError:
        print("Error: Please enter valid numeric values in all numeric fields.")
