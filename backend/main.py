from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

from database import init_db, insert_reading, get_history, insert_alert, get_alerts, clear_all
from alerts import send_alert

app = FastAPI(title="VoltGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

battery = {
    "voltage": 12.6,
    "current": 2.0,
    "temperature": 28.0,
    "soc": 87,
    "status": "NORMAL",
    "risk": 5,
    "health": 95,
    "rul_days": 365,
    "reasons": ["All parameters within safe operating range"],
    "action": "No action needed. Battery is healthy.",
    "timestamp": datetime.now().isoformat()
}

def calculate_health(v, c, t):
    score = 100.0
    score -= abs(12.6 - v) * 20
    if t > 35:
        score -= (t - 35) * 3
    if c > 3:
        score -= (c - 3) * 5
    return max(0, min(100, round(score)))

def classify_status(v, c, t):
    critical = 0
    warning = 0
    if v < 11.0: critical += 1
    elif v < 11.8: warning += 1
    if t > 50: critical += 1
    elif t > 40: warning += 1
    if c > 5: critical += 1
    elif c > 3.5: warning += 1
    if critical >= 1: return "CRITICAL"
    if warning >= 2: return "WARNING"
    return "NORMAL"

def build_reasons(v, c, t, status):
    reasons = []
    if v < 11.0: reasons.append(f"Critical voltage: {v}V (below 11.0V cutoff)")
    elif v < 11.8: reasons.append(f"Low voltage: {v}V (nominal 12.6V)")
    elif v < 12.2: reasons.append(f"Voltage below nominal: {v}V")

    if t > 50: reasons.append(f"Overheating: {t}°C (danger threshold)")
    elif t > 40: reasons.append(f"High temperature: {t}°C (safe limit 40°C)")
    elif t > 35: reasons.append(f"Elevated temperature: {t}°C")

    if c > 5: reasons.append(f"Excessive current draw: {c}A")
    elif c > 3.5: reasons.append(f"High current draw: {c}A")

    # Trend analysis from history
    hist = get_history(10)
    if len(hist) >= 5:
        v_drop = hist[0]["voltage"] - hist[-1]["voltage"]
        t_rise = hist[0]["temperature"] - hist[-1]["temperature"]
        if v_drop > 0.3:
            reasons.append(f"Voltage dropping: -{round(v_drop,2)}V in recent readings")
        if t_rise > 3:
            reasons.append(f"Rising temperature: +{round(t_rise,1)}°C trend")

    if not reasons:
        if status == "NORMAL":
            reasons = ["All parameters within safe operating range"]
        else:
            reasons = ["Anomalous pattern detected by AI reasoning engine"]
    return reasons

def recommend_action(status, t, v, health):
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

def update_battery(v, c, t, soc):
    v = round(v, 2)
    c = round(c, 2)
    t = round(t, 1)

    status = classify_status(v, c, t)
    health = calculate_health(v, c, t)
    rul = max(1, int(health * 3.6))
    risk = max(0, 100 - health)
    reasons = build_reasons(v, c, t, status)
    action = recommend_action(status, t, v, health)

    battery.update({
        "voltage": v,
        "current": c,
        "temperature": t,
        "soc": soc,
        "status": status,
        "health": health,
        "rul_days": rul,
        "risk": risk,
        "reasons": reasons,
        "action": action,
        "timestamp": datetime.now().isoformat()
    })

    insert_reading(v, c, t, status, risk, health)

    if status in ["WARNING", "CRITICAL"]:
        insert_alert(status, risk, v, t)
        try:
            send_alert(battery)
        except Exception as e:
            print(f"[ALERT ERROR] {e}")

@app.get("/")
def root():
    return {"app": "VoltGuard", "status": "running"}

@app.get("/data")
def get_data():
    return battery

@app.get("/history")
def history():
    return {"history": get_history(60)}

@app.get("/alerts")
def alerts():
    return {"alerts": get_alerts(20)}

@app.post("/simulate/{phase}")
def simulate(phase: str):
    if phase == "normal":
        v = 12.6 + random.uniform(-0.1, 0.1)
        c = 2.0 + random.uniform(-0.3, 0.3)
        t = 28.0 + random.uniform(-1, 1)
        soc = random.randint(85, 92)
    elif phase == "warning":
        v = 12.0 + random.uniform(-0.1, 0.1)
        c = 3.8 + random.uniform(-0.2, 0.2)
        t = 41.5 + random.uniform(-0.5, 0.5)
        soc = random.randint(60, 72)
    elif phase == "critical":
        v = 11.2 + random.uniform(-0.1, 0.1)
        c = 4.8 + random.uniform(-0.2, 0.2)
        t = 46.0 + random.uniform(-1, 1)
        soc = random.randint(25, 40)
    else:
        return {"error": "Invalid phase"}

    update_battery(v, c, t, soc)
    return battery

@app.post("/reset")
def reset():
    clear_all()
    battery.update({
        "voltage": 12.6, "current": 2.0, "temperature": 28.0, "soc": 87,
        "status": "NORMAL", "risk": 5, "health": 95, "rul_days": 365,
        "reasons": ["All parameters within safe operating range"],
        "action": "No action needed. Battery is healthy.",
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "reset"}

@app.post("/agent/approve")
def approve():
    ticket = "MT-" + str(random.randint(1000, 9999))
    return {"approved": True, "ticket": ticket}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)