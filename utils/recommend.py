def recommend_action(risk):
    if risk >= 75:
        return "🚨 Reroute or delay shipment by 48 hours."
    elif risk >= 45:
        return "⚠️ Add buffer days and monitor conditions."
    return "✅ Proceed as planned."
