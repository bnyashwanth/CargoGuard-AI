def auto_weather(route_risk):
    if route_risk > 0.65: return 4
    if route_risk > 0.45: return 3
    return 2

def auto_congestion(route_risk):
    return round(min(0.9, 0.3 + route_risk), 2)

def auto_traffic(congestion):
    return round(min(0.9, congestion + 0.1), 2)
