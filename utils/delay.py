def estimate_delay(risk, weather, congestion, traffic):
    days = 0
    if weather >= 4: days += 2
    if congestion > 0.7: days += 1
    if traffic > 0.8: days += 1
    if risk > 60: days += 1
    prob = min(30 + risk, 99)
    return days, prob
