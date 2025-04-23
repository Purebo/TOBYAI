from flask import Flask, render_template, request, jsonify
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# TOGETHER API Config
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682")
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

# Format AI response for readability
def format_message(message):
    if not message:
        return "No response received from AI."
    
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
    user_input = request.json.get("message", "")
    logger.info(f"Received user input: {user_input}")
    
    if not user_input.strip():
        return jsonify({"reply": "No input received."})

    # Add conversation history to prevent repetitive responses
    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": "You are Toby AI, created by Spicy (Pureheart). Be powerful, smart, helpful, and well-spoken. Avoid repetitive greetings. Answer directly based on the user's query."},
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
        # Log the request being sent
        logger.info(f"Sending request to Together API: {payload}")
        
        response = requests.post("https://api.together.xyz/v1/chat/completions", 
                              headers=headers, 
                              json=payload,
                              timeout=30)  # Add timeout
        
        # Log the raw response
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")  # Log first 200 chars
        
        response.raise_for_status()
        response_json = response.json()
        
        # Check if the expected fields exist
        if "choices" in response_json and len(response_json["choices"]) > 0:
            if "message" in response_json["choices"][0] and "content" in response_json["choices"][0]["message"]:
                ai_reply = response_json["choices"][0]["message"]["content"]
                logger.info(f"AI reply: {ai_reply[:100]}...")  # Log first 100 chars
                
                # Check if response is just a greeting
                lower_reply = ai_reply.lower()
                if any(greeting in lower_reply for greeting in ["how can i assist", "how may i help", "how can i help"]):
                    ai_reply = "I noticed you might be experiencing a loop. Please provide more specific instructions or questions, and I'll do my best to assist with those directly."
                
                formatted_reply = format_message(ai_reply)
                return jsonify({"reply": formatted_reply})
            else:
                logger.error("Unexpected response structure: missing message or content")
        else:
            logger.error("Unexpected response structure: missing choices")
        
        return jsonify({"reply": "Received an unexpected response format from the AI service."})
    
    except requests.exceptions.Timeout:
        logger.error("Request to Together API timed out")
        return jsonify({"reply": "The request to the AI service timed out. Please try again."})
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({"reply": f"Error communicating with the AI service: {str(e)}"})
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"reply": f"An unexpected error occurred: {str(e)}"})

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
