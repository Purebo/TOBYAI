import os
import random
import requests
from flask import Flask, request, jsonify, send_from_directory
from duckduckgo_search import DDGS

# --- Toby AI Class ---
class TobyAI:
    def __init__(self):
        self.creator = "Pureheart (Spicy)"
        self.name = "Toby AI"
        
        # API Keys and Settings
        self.together_api_key = os.getenv("TOGETHER_API_KEY", "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs")
        self.together_model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
        self.together_api_url = "https://api.together.xyz/v1/chat/completions"
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "ee9863e5da3dc66f36b37f7b536d2989")
        
        self.conversation_history = []
        self.max_history_length = 5
        
        self.predefined_responses = {
            "who are you": f"I am {self.name}, created by {self.creator}.",
            "what are you": f"I am {self.name}, an AI assistant created by {self.creator}.",
            "who created you": f"I was created by {self.creator}, also known as Spicy.",
            "who made you": f"My creator is {self.creator}, the one and only Spicy Pureheart!",
            "your name": f"My name is {self.name}. Nice to meet you!",
            "how are you": "I'm functioning perfectly and ready to assist you!",
            "hello": "Hello! How can I help today?",
            "hi": "Hi there! Need anything?",
            "help": "I can answer questions, check weather, search the web, and more. Just ask!",
            "thanks": "You're welcome!",
            "thank you": "You're welcome!"
        }

    def generate_response_with_together(self, query):
        self.conversation_history.append(f"User: {query}")

        messages = [
            {"role": "system", "content": f"You are {self.name}, created by {self.creator}. Always be helpful and friendly."}
        ]
        
        # Include conversation history
        for item in self.conversation_history[-self.max_history_length*2:]:
            if item.startswith("User: "):
                messages.append({"role": "user", "content": item[6:]})
            elif item.startswith(f"{self.name}: "):
                messages.append({"role": "assistant", "content": item[len(self.name) + 2:]})

        try:
            headers = {
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.together_model,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9
            }
            response = requests.post(self.together_api_url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"].strip()
                self.conversation_history.append(f"{self.name}: {assistant_message}")
                return assistant_message
            else:
                return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"API Error: {e}"

    def search_web(self, query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=2))
                if results:
                    response = results[0]['body']
                    return (response[:300] + "...") if len(response) > 300 else response
                return "I couldn't find anything useful."
        except Exception as e:
            return f"Search error: {e}"

    def get_weather(self, city):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            if response.status_code == 200:
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                return f"In {city}: {weather}, {temp}°C, feels like {feels_like}°C, humidity {humidity}%." 
            else:
                return f"Weather error: {data.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Weather fetch error: {e}"

    def predict_subscribers(self, days):
        base = 1000
        growth = random.uniform(0.9, 1.2)
        prediction = int(days * base * growth)
        return random.choice([
            f"You might reach {prediction} subscribers in {days} days!",
            f"Stay spicy! You could hit {prediction} subscribers in {days} days!",
            f"In {days} days, expect about {prediction} fans!"
        ])

    def get_predefined_response(self, query):
        for key, response in self.predefined_responses.items():
            if key in query:
                return response
        return None

    def handle_query(self, query):
        query = query.lower().strip()
        if not query:
            return "Please say something."

        predefined = self.get_predefined_response(query)
        if predefined:
            return predefined

        if any(exit_word in query for exit_word in ["exit", "quit", "goodbye"]):
            return "Goodbye, Pureheart! Stay awesome!"

        if "hype my fans" in query:
            return "Shoutout to all Pureheart fans! Keep the energy alive!"

        if "weather in" in query:
            try:
                city = query.split("weather in ")[1].strip()
                return self.get_weather(city)
            except IndexError:
                return "Please tell me which city you mean."

        if "should i" in query:
            if "upload" in query:
                return "Definitely upload it! Your fans are waiting!"
            else:
                return "Maybe think about it first."

        if "predict subscribers" in query:
            try:
                days = int(query.split("in ")[1].split(" days")[0])
                return self.predict_subscribers(days)
            except:
                return "Say it like: 'predict subscribers in X days'."

        if any(q in query for q in ["what is", "when did", "did", "check", "who is", "where is", "is", "how to", "why do"]):
            return self.search_web(query)

        return self.generate_response_with_together(query)


# --- Flask App Setup ---
app = Flask(__name__, static_folder='static')
toby = TobyAI()

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    user_input = data.get('message', '')
    if not user_input:
        return jsonify({'response': 'No input provided.'}), 400

    response = toby.handle_query(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
