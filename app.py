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
    data = request.json

    payload = {
        "from": {
            "email": "orders@scarceph.com",
            "name": "Scarceᴾᴴ"
        },
        "to": [
            {"email": data["to"]}
        ],
        "subject": data["subject"],
        "text": data["text"],
        "html": data["html"],
        "category": "transactional"
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
