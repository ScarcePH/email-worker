from flask import Flask, request, jsonify
import requests
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MAILTRAP_TOKEN = os.environ["MAILTRAP_TOKEN"]

MAILTRAP_URL = "https://send.api.mailtrap.io/api/send"


def _send_mailtrap_payload(payload):
    r = requests.post(
        MAILTRAP_URL,
        headers={
            "Authorization": f"Bearer {MAILTRAP_TOKEN}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=10
    )

    if r.status_code >= 400:
        return jsonify(r.json()), r.status_code

    return jsonify({"status": "sent"})


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json or {}

    email_type = data.get("type")
    template_variables = data.get("template_variables") or {}

    if email_type == "validate_payment":
        template = os.environ["VALIDATE_TEMPLATE"]
    elif email_type == 'approve_payment':
        template = os.environ['APPROVE_TEMPLATE']
    elif email_type == 'decline_payment':
        template = os.environ['DECLINE_TEMPLATE']
    elif email_type == 'shipment_update':
        template = os.environ['SHIPMENT_UPDATE']
    elif email_type == "admin_order_notification":
        template = os.environ['ADMIN_ORDER_NOTIFICATION']
    elif email_type == "password_reset":
        template = os.environ.get("PASSWORD_RESET_TEMPLATE")
        if not template:
            reset_url = template_variables.get("reset_url")
            store_name = template_variables.get("store_name", "ScarcePH")
            expires_in = template_variables.get("expires_in", "1 hour")

            payload = {
                "from": {"email": "orders@scarceph.com"},
                "to": [{"email": data.get("to")}],
                "subject": f"Reset your {store_name} password",
                "text": (
                    f"Use this link to reset your {store_name} password: {reset_url}\n\n"
                    f"This link expires in {expires_in}. If you did not request this, ignore this email."
                ),
                "html": (
                    f"<p>Use this link to reset your {store_name} password:</p>"
                    f"<p><a href=\"{reset_url}\">Reset password</a></p>"
                    f"<p>This link expires in {expires_in}. If you did not request this, ignore this email.</p>"
                ),
            }

            return _send_mailtrap_payload(payload)
    else:
        return jsonify({"error": "Unsupported email type"}), 400

    payload = {
        "from": {"email": "orders@scarceph.com"},
        "to": [{"email": data.get("to")}],
        "template_uuid": template,
        "template_variables": template_variables,
    }

    return _send_mailtrap_payload(payload)
