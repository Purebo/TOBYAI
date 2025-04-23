from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# === Settings ===
TOGETHER_API_KEY = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"
"mistralai/Mistral-7B-Instruct-v0.1"
  # or another model you're using
LOG_FILE = "toby_chat_history.txt"

# === Typing Effect (Optional, not used on web) ===
def type_like_toby(text, delay=0.02):
    print(text)  # Simple print for the web, no typing effect on the webpage

# === Memory (Conversation History) ===
conversation_history = [
    {"role": "system", "content": "You are Toby AI, a powerful assistant created by Spicy (Pureheart). Be helpful, smart, and friendly."}
]

# === Save Conversation to File ===
def save_conversation(user_input, ai_response):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"You: {user_input}\n")
        f.write(f"Toby: {ai_response}\n\n")

# === Ask Together AI ===
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

# === Flask Web App Route ===
@app.route("/", methods=["GET", "POST"])
def index():
    ai_response = ""
    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input.lower() in ["exit", "quit", "goodbye"]:
            ai_response = "Goodbye, Spicy."
        else:
            conversation_history.append({"role": "user", "content": user_input})
            ai_response = ask_together_ai()
            conversation_history.append({"role": "assistant", "content": ai_response})
            save_conversation(user_input, ai_response)
    
    return render_template("index.html", ai_response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)
