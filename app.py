import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Credenciais fixas (pode mover para variáveis de ambiente se quiser)
APP_ID = "NDc5OTY5MzIyNDE5"
APP_SECRET = "wt2UryrA_ixxeIF41AmM01iQV_hqoFzh"  # substitua pelo valor completo real
GROUP_ID = "OTU5MDcyNTQ2MTc3"

SEATALK_OAUTH_URL = "https://open.seatalk.io/oauth2/token"
SEATALK_MESSAGE_URL = "https://open.seatalk.io/api/v1/messages"

# Gera um token OAuth2 novo
def gerar_token():
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET,
        "grant_type": "client_credentials"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(SEATALK_OAUTH_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]

# Envia mensagem para o SeaTalk
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

    # Verifica verificação inicial
    if data.get("event_type") == "event_verification":
        challenge = data["event"]["seatalk_challenge"]
        return jsonify({"seatalk_challenge": challenge}), 200

    # Recebe mensagens do GSheets com "text"
    if "text" in data:
        mensagem = data["text"]
        enviar_para_seatalk(mensagem)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
