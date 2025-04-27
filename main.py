import requests
import random
import os
import json
from flask import Flask, render_template, request, jsonify
from duckduckgo_search import DDGS

app = Flask(__name__)

class TobyAI:
    def __init__(self):
        self.creator = "Pureheart (Spicy)"
        self.name = "Toby AI"
        
        # Together AI API settings
        self.together_api_key = os.getenv("TOGETHER_API_KEY", "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs")
        self.together_model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
        self.together_api_url = "https://api.together.xyz/v1/chat/completions"
        
        # API keys
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "ee9863e5da3dc66f36b37f7b536d2989")
        
        # Conversation history
        self.conversation_history = []
        self.max_history_length = 5
        
        # Predefined responses
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
        
        print(f"Initialized {self.name} (web version)")

    def speak(self, text):
        """Return text with double line breaks between sentences for web use"""
        sentences = text.replace('. ', '.\n\n').replace('! ', '!\n\n').replace('? ', '?\n\n')
        return sentences.strip()

    def generate_response_with_together(self, query):
        self.conversation_history.append(f"User: {query}")
        
        messages = [
            {
                "role": "system",
                "content": f"You are {self.name}, an AI assistant created by {self.creator}. Always be friendly, direct, and complete your responses."
            }
        ]
        
        for i in range(max(0, len(self.conversation_history) - self.max_history_length), len(self.conversation_history)):
            history_item = self.conversation_history[i]
            if history_item.startswith("User: "):
                messages.append({"role": "user", "content": history_item[6:]})
            elif history_item.startswith(f"{self.name}: "):
                messages.append({"role": "assistant", "content": history_item[len(self.name) + 2:]})
        
        if not self.conversation_history or not self.conversation_history[-1].startswith("User: "):
            messages.append({"role": "user", "content": query})
        
        try:
            headers = {
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.together_model,
                "messages": messages,
                "max_tokens": 512,  # Increased for complete responses
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(self.together_api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"].strip()
                finish_reason = result["choices"][0].get("finish_reason", "stop")
                
                if finish_reason != "stop":
                    print(f"Warning: Response may be incomplete (finish_reason: {finish_reason})")
                
                self.conversation_history.append(f"{self.name}: {assistant_message}")
                
                if len(self.conversation_history) > self.max_history_length * 2:
                    self.conversation_history = self.conversation_history[-self.max_history_length * 2:]
                    
                return assistant_message
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return f"Error {response.status_code}: Unable to get response from Together AI."
        except Exception as e:
            print(f"API error: {e}")
            return "Error communicating with Together AI."

    def search_web(self, query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=2))
                if results:
                    response = results[0]['body']
                    return (response[:300] + "...") if len(response) > 300 else response
                return "I couldn't find anything useful."
        except Exception as e:
            print(f"Search error: {e}")
            return "Problem occurred while searching the web."

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
                return f"Couldn't get weather: {data.get('message', 'Unknown error')}"
        except Exception as e:
            print(f"Weather error: {e}")
            return "Unable to fetch weather right now."

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

    def respond(self, query):
        if not query:
            return "Please provide a query."
        
        try:
            predefined = self.get_predefined_response(query)
            if predefined:
                return self.speak(predefined)
            
            elif any(exit_word in query for exit_word in ["exit", "quit", "goodbye"]):
                return self.speak("Goodbye, Pureheart! Stay awesome!")
            
            elif "hype my fans" in query:
                return self.speak("Shoutout to all Pureheart fans! Keep the energy alive!")
            
            elif "weather in" in query:
                try:
                    city = query.split("weather in ")[1].strip()
                    return self.speak(self.get_weather(city))
                except IndexError:
                    return self.speak("Please tell me which city you mean.")
            
            elif "should i" in query:
                if "upload" in query:
                    return self.speak("Definitely upload it! Your fans are waiting!")
                else:
                    return self.speak("Maybe think about it first.")
            
            elif "predict subscribers" in query:
                try:
                    days = int(query.split("in ")[1].split(" days")[0])
                    return self.speak(self.predict_subscribers(days))
                except:
                    return self.speak("Say it like: 'predict subscribers in X days'.")
            
            elif any(q in query for q in ["what is", "when did", "did", "check", "who is", "where is", "is", "how to", "why do"]):
                return self.speak(self.search_web(query))
            
            else:
                response = self.generate_response_with_together(query)
                return self.speak(response)
        
        except Exception as e:
            print(f"Error responding: {e}")
            return self.speak("Something went wrong while thinking...")

toby = TobyAI()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        user_input = data.get('query', '').lower().strip()
        if not user_input:
            return jsonify({'response': 'Please provide a query.'})
        
        response = toby.respond(user_input)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error handling query: {e}")
        return jsonify({'response': 'Error processing your request.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
