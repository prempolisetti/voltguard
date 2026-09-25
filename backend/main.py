from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

from database import init_db, insert_reading, get_history, insert_alert, get_alerts, clear_all
from alerts import send_alert
from agent import agent_reasoning

app = FastAPI(title="VoltGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# ==========================================
# BATTERY STATE
# ==========================================
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


# ==========================================
# UPDATE BATTERY — uses agent + email alert
# ==========================================
def update_battery(v, c, t, soc):
    v = round(v, 2)
    c = round(c, 2)
    t = round(t, 1)

    # Get current history
    history = get_history(10)

    # Run AI Agent reasoning
    result = agent_reasoning(v, c, t, history)

    # Update battery state
    battery.update({
        "voltage": v,
        "current": c,
        "temperature": t,
        "soc": soc,
        "status": result["status"],
        "health": result["health"],
        "rul_days": result["rul_days"],
        "risk": result["risk"],
        "reasons": result["reasons"],
        "action": result["action"],
        "timestamp": result["timestamp"]
    })

    # Save to database
    insert_reading(v, c, t, result["status"], result["risk"], result["health"])

    # ==========================================
    # EMAIL ALERT — trigger on WARNING / CRITICAL
    # ==========================================
    if result["status"] in ["WARNING", "CRITICAL"]:
        insert_alert(result["status"], result["risk"], v, t)
        try:
            print(f"[EMAIL] Sending {result['status']} alert...")
            send_alert(battery)
            print(f"[EMAIL] ✓ Alert sent for {result['status']}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")


# ==========================================
# ROUTES
# ==========================================
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