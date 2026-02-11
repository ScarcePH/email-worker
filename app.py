from flask import Flask, request, jsonify
import requests
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MAILTRAP_TOKEN = os.environ["MAILTRAP_TOKEN"]

MAILTRAP_URL = "https://send.api.mailtrap.io/api/send"


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json or {}

    email_type = data.get("type")

    if email_type == "validate_payment":
        template = os.environ["VALIDATE_TEMPLATE"]
    else:
        return jsonify({"error": "Unsupported email type"}), 400

    template_variables = data.get("template_variables")


    payload = {
        "from": {"email": "orders@scarceph.com"},
        "to": [{"email": data.get("to")}],
        "template_uuid": template,
        "template_variables": template_variables,
    }

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
