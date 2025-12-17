def generate_explanation(risk, weather, congestion, traffic):
    reasons = []
    if weather >= 4:
        reasons.append("severe weather conditions")
    if congestion > 0.7:
        reasons.append("high port congestion")
    if traffic > 0.8:
        reasons.append("dense sea traffic")

    if not reasons:
        return "Shipment conditions are stable with minimal operational risk."

    return f"High risk is primarily due to {', '.join(reasons)}."
