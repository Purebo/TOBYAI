from flask import Flask, render_template, request, jsonify, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage
conversation_history = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    # Simulating AI reply
    ai_reply = f"You said: {user_message}"  # Replace with your AI logic

    # Save conversation
    user_id = session.get("user_id", "guest")
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append(f"You: {user_message}")
    conversation_history[user_id].append(f"Toby: {ai_reply}")

    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
