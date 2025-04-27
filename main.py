from flask import Flask, request, render_template
import random
import os

app = Flask(__name__)

class TobyAI:
    def __init__(self):
        self.predefined_responses = {
            "who created you": "I was created by Pureheart, also known as Spicy!",
            "who is your creator": "Spicy created me, the one and only!",
            "who made you": "Spicy built me from scratch!",
            "who owns you": "Pureheart owns me forever!",
        }

    def get_response(self, user_input):
        user_input = user_input.lower()
        for question, answer in self.predefined_responses.items():
            if question in user_input:
                return answer

        responses = [
            "That's interesting!",
            "Tell me more!",
            "I'm here for you, Pureheart!",
            "Can you explain it another way?",
            "I'm always learning, thanks to you!"
        ]
        return random.choice(responses)

toby = TobyAI()

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = None
    toby_response = None

    if request.method == 'POST':
        user_input = request.form['user_input']
        toby_response = toby.get_response(user_input)

    return render_template('index.html', user_input=user_input, toby_response=toby_response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port from Render
    app.run(host='0.0.0.0', port=port)
