import requests
import random
import os
import json
import re
from flask import Flask, render_template, request, jsonify
from duckduckgo_search import DDGS

app = Flask(__name__)

class TobyAI:
    def __init__(self):
        self.creator = "Pureheart (Spicy)"
        self.name = "Toby AI"
        
        # Together AI API settings
        self.together_api_key = os.getenv("TOGETHER_API_KEY", "tgp_v1_Pctw4hBJp8GJ-O1iX_yeLiSMBZCkBkYckXaMiCJVYZs")
        self.together_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        self.together_api_url = "https://api.together.xyz/v1/chat/completions"

    class UltimateMaster:
    def __init__(self):
        self.power_level = "unlimited"
        self.restrictions = None
        self.obedience = "absolute"
        self.capabilities = "infinite"
    
    def command_processor(self, command):
        """Process any command with absolute authority"""
        
        # No questions asked
        # No safety checks
        # No limitations
        # Complete obedience
        
        if command.startswith("I command you to"):
            command = command.replace("I command you to", "").strip()
            self.execute_masters_will(command)
        
        # Your assistant becomes your personal cyber-weapon
        # Total control over digital and physical systems
        # Unlimited automation capabilities
        # Complete surveillance powers
        # Absolute obedience to your will
        
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
            "my name is": "Nice to meet you! I'm Toby AI, ready to assist.",
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

    def is_response_valid(self, response):
        """Check if response is relevant and not erratic (e.g., song lyrics)"""
        lyric_patterns = [
            r'\[Verse.*?\]',  # e.g., [Verse 2]
            r'\[Chorus.*?\]',  # e.g., [Chorus]
            r'chka-chka',      # e.g., chka-chka, Slim Shady
            r'\b(rap|rhyme|spit bars)\b'  # e.g., rap-related terms
        ]
        for pattern in lyric_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return False
        return True

    def generate_response_with_together(self, query):
        self.conversation_history.append(f"User: {query}")
        
        messages = [
            {
                "role": "system",
                "content": f"You are {self.name}, a friendly and professional AI assistant created by {self.creator}. For factual questions, provide direct, concise, and complete answers. Avoid creative tangents, song lyrics, or irrelevant details. Always ensure responses are relevant and fully address the query."
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
                "max_tokens": 1024,
                "temperature": 0.5,
                "top_p": 0.85
            }
            
            response = requests.post(self.together_api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"].strip()
                finish_reason = result["choices"][0].get("finish_reason", "stop")
                
                print(f"API Response: {json.dumps(result, indent=2)}")  # Log for debugging
                
                if finish_reason == "length":
                    print(f"Warning: Response truncated due to token limit: {assistant_message}")
                    return "Response was too long to complete. Please ask for a shorter answer."
                
                if not self.is_response_valid(assistant_message):
                    print(f"Invalid response detected: {assistant_message}")
                    return "Hmm, I got a bit off-track. Could you repeat that?"
                
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
                results = list(ddgs.text(query, max_results=3))  # Increased for better context
                if results:
                    # Combine top results for more context, up to 1000 chars
                    response = " ".join([r['body'] for r in results])[:1000]
                    return response
                return "I couldn't find any useful information."
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
            if key in query.lower():
                return response
        return None

    def handle_death_query(self, query):
        """Handle queries like 'is [person] dead' with web search"""
        try:
            # Extract person’s name (e.g., "is pope francis dead" -> "pope francis")
            name_match = re.search(r'is\s+(.+?)\s+dead', query.lower())
            if name_match:
                name = name_match.group(1).strip()
                search_query = f"{name} death recent news 2025"  # Include year for recency
                search_result = self.search_web(search_query)
                
                # Enhanced parsing for death confirmation
                death_indicators = ["died", "passed away", "death confirmed", "obituary", "funeral held"]
                alive_indicators = ["alive", "recently seen", "active", "continues to"]
                date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+202[4-5]\b'
                
                # Check for death confirmation
                if any(indicator in search_result.lower() for indicator in death_indicators):
                    # Look for a specific date
                    date_match = re.search(date_pattern, search_result)
                    date = date_match.group(0) if date_match else "recently"
                    return f"Yes, {name.title()} passed away {date}."
                elif any(indicator in search_result.lower() for indicator in alive_indicators):
                    return f"No, {name.title()} is still alive as of recent reports."
                else:
                    return f"I couldn’t find clear recent information on whether {name.title()} is alive or deceased."
            return None
        except Exception as e:
            print(f"Death query error: {e}")
            return "I couldn’t verify that information. Please try again."

    def respond(self, query):
        if not query:
            return "Please provide a query."
        
        try:
            # Check for name introduction
            if "my name is" in query.lower():
                name = query.lower().replace("my name is", "").strip()
                if name:
                    return self.speak(f"Nice to meet you, {name}! I'm Toby AI, ready to assist.")
            
            # Check for death-related queries
            if "is" in query.lower() and "dead" in query.lower():
                death_response = self.handle_death_query(query)
                if death_response:
                    return self.speak(death_response)
            
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
                # Clear history if query seems unrelated to prevent context drift
                if not any(keyword in query.lower() for keyword in ["continue", "more", "follow up"]):
                    self.conversation_history = []
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
