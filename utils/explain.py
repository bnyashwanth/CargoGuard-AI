def generate_explanation(risk, weather, congestion, traffic):
    reasons = []
    if weather >= 4: reasons.append("severe weather")
    if congestion > 0.7: reasons.append("high port congestion")
    if traffic > 0.8: reasons.append("dense sea traffic")

    if not reasons:
        return "Shipment conditions are stable with low operational risk."

    return f"High risk is mainly due to {', '.join(reasons)}."
