from flask import Flask, render_template, request, jsonify, session, Response
import requests
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage
conversation_history = {}

# Together AI API Configuration
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "your_api_key_here")
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    system_prompt = "You are Toby AI, created to assist users intelligently and helpfully."

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        ai_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't process your request.")
        
        # Save conversation history
        user_id = session.get("user_id", "guest")
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        conversation_history[user_id].append(f"You: {user_message}")
        conversation_history[user_id].append(f"Toby: {ai_reply}")

        return jsonify({"reply": ai_reply})
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({"reply": f"Error communicating with the AI service: {str(e)}"})

@app.route("/get_chat", methods=["GET"])
def get_chat():
    user_id = request.args.get("user_id", "guest")
    history = conversation_history.get(user_id, [])
    return jsonify({"conversation": history})

@app.route("/export_chat", methods=["GET"])
def export_chat():
    user_id = request.args.get("user_id", "guest")
    history = conversation_history.get(user_id, [])
    export_data = "\n".join(history)
    response = Response(export_data, mimetype="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
