from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__, template_folder="templates")

# Toby AI Brain inside main.py
class TobyAI:
    def __init__(self):
        self.predefined_responses = {
            "who created you": "I was created by Pureheart, also known as Spicy!",
            "who is your creator": "Spicy created me, the one and only!",
            "who made you": "Spicy built me from scratch!",
            "who owns you": "Pureheart owns me forever!",
        }

    def get_predefined_response(self, query):
        query = query.lower()
        for keyword in self.predefined_responses:
            if keyword in query:
                return self.predefined_responses[keyword]
        return None

    def respond_web(self, query):
        """Respond to a query and return text"""
        if not query:
            return "Please say something."

        try:
            predefined = self.get_predefined_response(query)
            if predefined:
                return predefined

            elif any(exit_word in query for exit_word in ["exit", "quit", "goodbye"]):
                return "Goodbye, Pureheart! Stay awesome!"

            elif "hype my fans" in query:
                return "Shoutout to all Pureheart fans! Keep the energy alive!"
                
            elif "should i" in query:
                if "upload" in query:
                    return "Definitely upload it! Your fans are waiting!"
                else:
                    return "Maybe think about it first."

            elif "predict subscribers" in query:
                try:
                    days = int(query.split("in ")[1].split(" days")[0])
                    prediction = random.randint(100, 10000)  # Fake prediction
                    return f"In {days} days, you could have around {prediction} more subscribers! 🚀"
                except:
                    return "Say it like: 'predict subscribers in X days'."

            else:
                responses = [
                    "That's interesting!",
                    "Tell me more!",
                    "I'm here for you, Pureheart!",
                    "Can you explain it another way?",
                    "I'm always learning, thanks to you!"
                ]
                return random.choice(responses)
                    
        except Exception as e:
            print(f"Error responding: {e}")
            return "Something went wrong while thinking..."

# Initialize Toby
bot = TobyAI()

# Home route - serve web page
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # Make sure you have templates/index.html

# Chat route - handle chat messages
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "No message received."})

    response = bot.respond_web(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
