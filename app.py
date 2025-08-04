import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_ID = "NDc5OTY5MzIyNDE5"
APP_SECRET = "wt2UryrA_ixeelF41AmM01iQV_hqoFzh"  # valor completo
GROUP_ID = "OTU5MDcyNTQ2MTc3"

SEATALK_TOKEN_URL = "https://open.seatalk.io/open-apis/auth/v1/app_access_token"
SEATALK_MESSAGE_URL = "https://open.seatalk.io/open-apis/message/v1/message/send"

import base64

def gerar_token():
    url = "https://open.seatalk.io/oauth2/token"
    payload = {
        "grant_type": "client_credentials"
    }
    auth_string = f"{APP_ID}:{APP_SECRET}"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def enviar_para_seatalk(mensagem):
    token = gerar_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "receiver_id": GROUP_ID,
        "message": {
            "type": "text",
            "content": mensagem
        }
    }
    response = requests.post(SEATALK_MESSAGE_URL, headers=headers, json=body)
    print("🔁 SeaTalk response:", response.status_code, response.text)
    response.raise_for_status()

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    print("📩 Evento recebido:", json.dumps(data, indent=2))

    if data.get("event_type") == "event_verification":
        challenge = data["event"]["seatalk_challenge"]
        return jsonify({"seatalk_challenge": challenge}), 200

    if "text" in data:
        enviar_para_seatalk(data["text"])

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


