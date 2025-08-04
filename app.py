from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    print("📩 Evento recebido:", data)

    if data.get("event_type") == "event_verification":
        challenge = data["event"]["seatalk_challenge"]
        return jsonify({"seatalk_challenge": challenge}), 200

    if data.get("event_type") == "message.receive":
        message = data["event"].get("text")
        sender_id = data["event"].get("sender_id")
        print(f"💬 {sender_id} disse: {message}")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
