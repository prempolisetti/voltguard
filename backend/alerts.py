"""
VoltGuard Email Alerts
======================
Sends battery alerts via Gmail SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ==========================================
# ⚠️ CONFIGURE THESE (setup steps కింద)
# ==========================================
GMAIL_USER = "prempolisetti4492@gmail.com"       # మీ Gmail address
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"  # 16-character app password
TO_EMAIL = "prempolisetti492@gmail.com"           # alerts ఎవరికి పంపాలి

# ==========================================
# Anti-spam tracker
# ==========================================
_last_alert = {"time": None, "status": None}

def _should_send(status):
    """Rate limit: 1 alert per 30 seconds unless status changes"""
    now = datetime.now()
    if _last_alert["time"] is None:
        _last_alert["time"] = now
        _last_alert["status"] = status
        return True
    elapsed = (now - _last_alert["time"]).total_seconds()
    if _last_alert["status"] != status or elapsed > 30:
        _last_alert["time"] = now
        _last_alert["status"] = status
        return True
    return False

def _build_html(battery):
    """Build HTML email body"""
    status = battery["status"]
    v = battery["voltage"]
    c = battery["current"]
    t = battery["temperature"]
    risk = battery["risk"]
    health = battery["health"]
    rul = battery["rul_days"]
    action = battery["action"]
    reasons = battery["reasons"]
    time_str = datetime.now().strftime("%d %b %Y, %H:%M:%S")

    if status == "CRITICAL":
        header_color = "#ef4444"
        emoji = "🚨"
        title = "CRITICAL BATTERY ALERT"
    else:
        header_color = "#f59e0b"
        emoji = "⚠️"
        title = "Battery Warning"

    reasons_html = "".join(
        f'<li style="padding:8px 0;border-bottom:1px solid #eee;">{r}</li>'
        for r in reasons
    )

    html = f"""
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f7;">
      <div style="max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

        <div style="background:{header_color};padding:30px 24px;color:#fff;">
          <div style="font-size:28px;font-weight:bold;">{emoji} VoltGuard</div>
          <div style="font-size:16px;margin-top:6px;opacity:0.95;">{title}</div>
        </div>

        <div style="padding:28px 24px;">

          <div style="display:flex;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;">
            <div style="flex:1;min-width:140px;padding:12px;background:#f9fafb;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#6b7280;letter-spacing:1px;">VOLTAGE</div>
              <div style="font-size:22px;font-weight:bold;color:#111;">{v} V</div>
            </div>
            <div style="flex:1;min-width:140px;padding:12px;background:#f9fafb;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#6b7280;letter-spacing:1px;">CURRENT</div>
              <div style="font-size:22px;font-weight:bold;color:#111;">{c} A</div>
            </div>
            <div style="flex:1;min-width:140px;padding:12px;background:#f9fafb;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#6b7280;letter-spacing:1px;">TEMPERATURE</div>
              <div style="font-size:22px;font-weight:bold;color:#111;">{t} °C</div>
            </div>
          </div>

          <div style="display:flex;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;">
            <div style="flex:1;min-width:140px;padding:12px;background:#fef3c7;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#92400e;letter-spacing:1px;">FAILURE RISK</div>
              <div style="font-size:22px;font-weight:bold;color:#b45309;">{risk}%</div>
            </div>
            <div style="flex:1;min-width:140px;padding:12px;background:#d1fae5;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#065f46;letter-spacing:1px;">HEALTH SCORE</div>
              <div style="font-size:22px;font-weight:bold;color:#047857;">{health}/100</div>
            </div>
            <div style="flex:1;min-width:140px;padding:12px;background:#e0e7ff;border-radius:8px;margin:4px;">
              <div style="font-size:11px;color:#3730a3;letter-spacing:1px;">REMAINING LIFE</div>
              <div style="font-size:22px;font-weight:bold;color:#4338ca;">{rul} days</div>
            </div>
          </div>

          <h3 style="color:#111;font-size:15px;margin:0 0 10px;">Reasons</h3>
          <ul style="list-style:none;padding:0;margin:0 0 24px;background:#f9fafb;border-radius:8px;padding:8px 16px;">
            {reasons_html}
          </ul>

          <div style="padding:16px;background:{header_color}1a;border-left:4px solid {header_color};border-radius:6px;margin-bottom:24px;">
            <div style="font-size:11px;color:{header_color};font-weight:bold;letter-spacing:1px;margin-bottom:6px;">RECOMMENDED ACTION</div>
            <div style="font-size:14px;color:#111;line-height:1.5;">{action}</div>
          </div>

          <div style="text-align:center;padding-top:16px;border-top:1px solid #eee;">
            <a href="http://127.0.0.1:8000" style="display:inline-block;padding:12px 28px;background:{header_color};color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;font-size:14px;">
              Open Dashboard
            </a>
          </div>

        </div>

        <div style="background:#f9fafb;padding:16px 24px;text-align:center;font-size:12px;color:#6b7280;">
          Generated by VoltGuard — AI Battery Health Agent<br>
          {time_str}
        </div>

      </div>
    </body>
    </html>
    """
    return html

def send_email(subject, html_body, text_body):
    """Send email via Gmail SMTP"""
    if "your_email" in GMAIL_USER:
        print("[EMAIL] Not configured — skipping")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"VoltGuard <{GMAIL_USER}>"
        msg["To"] = TO_EMAIL

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] ✓ Sent to {TO_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] Auth failed — check app password")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_alert(battery):
    """Send battery alert email"""
    status = battery["status"]

    if status == "NORMAL":
        return False

    if not _should_send(status):
        print("[EMAIL] Rate limited — skipping")
        return False

    emoji = "🚨" if status == "CRITICAL" else "⚠️"
    subject = f"{emoji} VoltGuard {status}: Battery Alert"

    v = battery["voltage"]
    t = battery["temperature"]
    risk = battery["risk"]

    text_body = (
        f"VoltGuard Battery Alert\n"
        f"Status: {status}\n"
        f"Voltage: {v}V\n"
        f"Temperature: {t}°C\n"
        f"Risk: {risk}%\n\n"
        f"Action: {battery['action']}"
    )

    html_body = _build_html(battery)
    return send_email(subject, html_body, text_body)

def send_test():
    """Send a test email to verify setup"""
    subject = "✅ VoltGuard Connected"
    text = "Your VoltGuard email alerts are working!"
    html = """
    <div style="font-family:Arial;padding:24px;">
      <h2 style="color:#10b981;">✅ VoltGuard Connected</h2>
      <p>Your email alerts are now active.</p>
      <p>You'll receive battery alerts here when issues are detected.</p>
    </div>
    """
    return send_email(subject, html, text)