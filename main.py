from flask import Flask, render_template, request, jsonify, session, app, Response
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Flask secret key for sessions
app.secret_key = os.urandom(24)

# In-memory storage for demo purposes
conversation_history = {}
user_settings = {}

# TOGETHER API Config
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682")
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

@app.route("/")
def home():
    return render_template("index.html")


# 1. Chat Route for AI Responses
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message", "")
    if not user_input.strip():
        return jsonify({"reply": "Please enter a valid question."})
    
    system_prompt = "You are Toby AI, created by Spicy. Act helpful and insightful."

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
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
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "I couldn't process your request.")
        # Save the reply to conversation history for current user
        user_id = session.get("user_id", "guest")
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        conversation_history[user_id].append(f"Toby: {reply}")
        return jsonify({"reply": reply})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"reply": "There was an error processing your request."})


# 2. Save Chat History
@app.route("/save_chat", methods=["POST"])
def save_chat():
    data = request.json
    user_id = data.get("user_id", "guest")
    conversation = data.get("conversation", [])
    conversation_history[user_id] = conversation
    return jsonify({"message": "Chat history saved!"})


# 3. Get Chat History
@app.route("/get_chat", methods=["GET"])
def get_chat():
    user_id = request.args.get("user_id", "guest")
    history = conversation_history.get(user_id, [])
    return jsonify({"conversation": history})


# 4. Export Chat History
@app.route("/export_chat", methods=["GET"])
def export_chat():
    user_id = request.args.get("user_id", "guest")
    history = conversation_history.get(user_id, [])
    export_data = "\n".join(history)
    response = Response(export_data, mimetype="text/plain")
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
    return response


# 5. User Authentication
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    # Replace this with a real authentication system
    if username == "admin" and password == "password":
        session["user_id"] = username
        return jsonify({"message": "Logged in successfully!"})
    return jsonify({"message": "Invalid credentials!"})


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully!"})


# 6. Save User Settings
@app.route("/save_settings", methods=["POST"])
def save_settings():
    data = request.json
    user_id = session.get("user_id", "guest")
    settings = data.get("settings", {})
    user_settings[user_id] = settings
    return jsonify({"message": "Settings saved!"})


# 7. Get User Settings
@app.route("/get_settings", methods=["GET"])
def get_settings():
    user_id = session.get("user_id", "guest")
    settings = user_settings.get(user_id, {})
    return jsonify({"settings": settings})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
