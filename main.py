# Toby AI - Updated main.py with OpenAI GPT integration and Hugging Face support

import os
import requests
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# --- LOAD ENV VARIABLES SAFELY ---
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
HUGGINGFACE_API_KEY = os.getenv("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")
HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

OPENAI_API_KEY = os.getenv("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")
openai.api_key = OPENAI_API_KEY

# --- BRAIN FUNCTIONALITY ---

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"response": "Please enter a valid message."}), 400

    response_text = handle_query(user_input)
    return jsonify({"response": response_text})


def handle_query(message):
    if message.lower().startswith("generate image"):
        prompt = message.replace("generate image", "").strip()
        return generate_image(prompt)

    if "who created you" in message.lower():
        return "Spicy created me. He is my creator and guide."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Toby AI, created by Spicy. Be helpful, powerful, and smart."},
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error contacting OpenAI: {str(e)}"


def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    data = {
        "inputs": prompt
    }
    response = requests.post(HUGGINGFACE_MODEL_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            with open("static/generated_image.png", "wb") as f:
                f.write(response.content)
            return "Image generated! [Click here to view](static/generated_image.png)"
        except Exception as e:
            return f"Image received but error saving: {str(e)}"
    else:
        return f"Failed to generate image: {response.text}"


@app.route("/")
def home():
    return "Toby AI is running. Use the /chat endpoint with POST requests."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
