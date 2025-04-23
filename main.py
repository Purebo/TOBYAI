from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# TOGETHER API Config
TOGETHER_API_KEY = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

# Format AI response for readability
def format_message(message):
    message = message.replace(". ", ".<br><br>")
    message = message.replace("! ", "!<br><br>")
    message = message.replace("? ", "?<br><br>")
    return message

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Chat route
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"reply": "No input received."})

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": "You are Toby AI, created by Spicy (Pureheart). Be powerful, smart, helpful, and well-spoken. Format your responses with space for readability."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]

        formatted_reply = format_message(ai_reply)
        return jsonify({"reply": formatted_reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
