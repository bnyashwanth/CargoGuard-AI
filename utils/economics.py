RATE_PER_KM_PER_TON = 20  # ₹

def calc_cost(distance, weight):
    return distance * weight * RATE_PER_KM_PER_TON

def balanced_score(cost, time, risk):
    return (cost * 0.4) + (time * 0.3) + (risk * 0.3)
