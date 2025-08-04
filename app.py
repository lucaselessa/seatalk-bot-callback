import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_ID = "NDc5OTY5MzIyNDE5"
APP_SECRET = "wt2UryrA_ixeelF41AmM01iQV_hqoFzh"
GROUP_ID = "OTU5MDcyNTQ2MTc3"

SEATALK_TOKEN_URL = "https://openapi.seatalk.io/auth/app_access_token"
SEATALK_MESSAGE_URL = "https://open.seatalk.io/api/v1/messages"

def gerar_token():
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(SEATALK_TOKEN_URL, headers=headers, json=payload)
    print("🛑 TOKEN RESPONSE:", response.status_code, response.text)
    response.raise_for_status()

    data = response.json()
    if "data" not in data or "app_access_token" not in data["data"]:
        print("❌ Erro: resposta não contém o token esperado.")
        return None

    return data["data"]["app_access_token"]

def enviar_para_seatalk(mensagem):
    print("📤 Enviando mensagem:", mensagem)

    token = gerar_token()
    if not token:
        print("❌ Não foi possível obter o token.")
        return

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

    if not response.ok:
        print("❌ ERRO AO ENVIAR MENSAGEM:", response.status_code, response.text)

@app.route("/callback", methods=["POST"])
def callback():
    ip = requests.get("https://api.ipify.org").text
    print("🌐 IP PÚBLICO DO RENDER:", ip)

    data = request.get_json()
    print("📥 Raw data recebido:", data)
    print("📩 Evento recebido:", json.dumps(data, indent=2))

    if data.get("event_type") == "event_verification":
        challenge = data["event"]["seatalk_challenge"]
        return jsonify({"seatalk_challenge": challenge}), 200

    if isinstance(data, dict) and "text" in data:
        enviar_para_seatalk(data["text"])
    else:
        print("⚠️ Nenhum campo 'text' encontrado no payload.")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
