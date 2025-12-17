PORT_DISTANCE = {
    ("Mumbai", "Rotterdam"): 12000,
    ("Mumbai", "Singapore"): 4200,
    ("Mumbai", "Dubai"): 3000,
    ("Chennai", "Singapore"): 3600,
}

def get_distance(origin, destination):
    return PORT_DISTANCE.get((origin, destination), 8000)

def estimate_ports(distance_km):
    return max(2, int(distance_km / 1500))
