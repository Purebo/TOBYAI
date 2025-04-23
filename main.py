from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

TOGETHER_API_KEY = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

conversation_history = [
    {"role": "system", "content": "You are Toby AI, created by Spicy. Be smart, fast, and friendly."}
]

@app.route("/")
def home():
    return open("chat.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    conversation_history.append({"role": "user", "content": user_message})

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": TOGETHER_MODEL,
            "messages": conversation_history,
            "temperature": 0.7,
            "max_tokens": 500
        }
    )

    ai_reply = response.json()["choices"][0]["message"]["content"]
    conversation_history.append({"role": "assistant", "content": ai_reply})
    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(debug=True)
