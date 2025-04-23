from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# === Settings ===
TOGETHER_API_KEY = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"
TOGETHER_MODEL = "TOGETHER_MODEL = "meta-llama/Llama-2-7b-chat-hf"


# === Memory ===
conversation_history = [
    {"role": "system", "content": "You are Toby AI, a powerful assistant created by Spicy (Pureheart). Be helpful, smart, and friendly."}
]

@app.route("/")
def index():
    return send_from_directory(".", "chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    conversation_history.append({"role": "user", "content": user_message})

    response_text = ask_together_ai()
    conversation_history.append({"role": "assistant", "content": response_text})

    return jsonify({"response": response_text})


def ask_together_ai():
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": TOGETHER_MODEL,
        "messages": conversation_history,
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
