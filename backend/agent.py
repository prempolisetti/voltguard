"""
VoltGuard AI Agent
==================
Handles battery status classification, health calculation,
reason generation, and action recommendations.
"""

from datetime import datetime


# ==========================================
# HEALTH CALCULATION
# ==========================================
def calculate_health(v, c, t):
    """Calculate battery health score (0-100) using realistic normal operating ranges."""
    v_score = 100.0 - abs(12.6 - v) * 18
    temp_score = 100.0 - max(0.0, t - 28.0) * 2.5
    current_score = 100.0 - max(0.0, c - 2.0) * 12

    score = (v_score + temp_score + current_score) / 3
    return max(0, min(100, round(score)))


# ==========================================
# STATUS CLASSIFICATION
# ==========================================
def classify_status(v, c, t):
    """Classify battery status as NORMAL / WARNING / CRITICAL"""
    critical = 0
    warning = 0

    if v < 11.0:
        critical += 1
    elif v < 11.8:
        warning += 1

    if t > 50:
        critical += 1
    elif t > 40:
        warning += 1

    if c > 5:
        critical += 1
    elif c > 3.5:
        warning += 1

    if critical >= 1:
        return "CRITICAL"
    if warning >= 2:
        return "WARNING"
    return "NORMAL"


# ==========================================
# REASONS BUILDER
# ==========================================
def build_reasons(v, c, t, status, history):
    """Generate human-readable reasons for the status"""
    reasons = []

    # Voltage reasons
    if v < 11.0:
        reasons.append(f"Critical voltage: {v}V (below 11.0V cutoff)")
    elif v < 11.8:
        reasons.append(f"Low voltage: {v}V (nominal 12.6V)")
    elif v < 12.2:
        reasons.append(f"Voltage below nominal: {v}V")

    # Temperature reasons
    if t > 50:
        reasons.append(f"Overheating: {t}°C (danger threshold)")
    elif t > 40:
        reasons.append(f"High temperature: {t}°C (safe limit 40°C)")
    elif t > 35:
        reasons.append(f"Elevated temperature: {t}°C")

    # Current reasons
    if c > 5:
        reasons.append(f"Excessive current draw: {c}A")
    elif c > 3.5:
        reasons.append(f"High current draw: {c}A")

    # Trend analysis from history
    if history and len(history) >= 5:
        v_drop = history[0]["voltage"] - history[-1]["voltage"]
        t_rise = history[0]["temperature"] - history[-1]["temperature"]
        if v_drop > 0.3:
            reasons.append(f"Voltage dropping: -{round(v_drop, 2)}V in recent readings")
        if t_rise > 3:
            reasons.append(f"Rising temperature: +{round(t_rise, 1)}°C trend")

    # Fallback
    if not reasons:
        if status == "NORMAL":
            reasons = ["All parameters within safe operating range"]
        else:
            reasons = ["Anomalous pattern detected by AI reasoning engine"]

    return reasons


# ==========================================
# ACTION RECOMMENDATION
# ==========================================
def recommend_action(status, t, v, health):
    """Recommend next action based on status"""
    if status == "CRITICAL":
        if t > 50:
            return "IMMEDIATE: Disconnect charging. Cool battery. Call service center now."
        if v < 11.0:
            return "IMMEDIATE: Battery critically low. Stop vehicle. Request roadside service."
        return "IMMEDIATE: Battery inspection required within 2 hours. Do not continue long trips."

    if status == "WARNING":
        if health < 50:
            return "Schedule inspection within 24 hours. Monitor temperature closely."
        return "Schedule inspection within 48 hours. Reduce load if possible."

    return "No action needed. Battery is healthy. Continue normal operation."


# ==========================================
# MAIN AGENT FUNCTION
# ==========================================
def agent_reasoning(v, c, t, history):
    """
    Main AI Agent reasoning function.
    Returns a dict with status, health, risk, reasons, action.
    """
    status = classify_status(v, c, t)
    health = calculate_health(v, c, t)
    rul = max(1, int(health * 3.6))
    risk = max(0, min(100, 100 - health))
    if status == "NORMAL":
        risk = max(0, min(25, risk))
    reasons = build_reasons(v, c, t, status, history)
    action = recommend_action(status, t, v, health)

    return {
        "status": status,
        "health": health,
        "rul_days": rul,
        "risk": risk,
        "reasons": reasons,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }