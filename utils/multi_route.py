def generate_routes(origin, destination, base_distance):
    return [
        {
            "name": "Primary Route",
            "distance": base_distance,
            "risk_factor": 1.0
        },
        {
            "name": "Safer Route",
            "distance": int(base_distance * 1.15),
            "risk_factor": 0.75
        },
        {
            "name": "Faster Route",
            "distance": int(base_distance * 0.9),
            "risk_factor": 1.25
        }
    ]
