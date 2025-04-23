from flask import Flask, request, jsonify, send_file
import requests
import time

app = Flask(__name__)

TOGETHER_API_KEY = "YOUR_API_KEY"
TOGETHER_MODEL = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"

conversation_history = [
    {"role": "system", "content": "You are Toby AI, created by Spicy (Pureheart). Be helpful, smart, and friendly."}
]

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
        "max_tokens": 500,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def index():
    return send_file("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    conversation_history.append({"role": "user", "content": user_input})
    ai_response = ask_together_ai()
    conversation_history.append({"role": "assistant", "content": ai_response})
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
