import requests
import json
import time
import os

# === Settings ===
TOGETHER_API_KEY = "58bedad48b97a0b3e75916ddf975f00642ed68b29b4f91aafee697749e0e2682"  # Replace with your actual API key
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # Replace with a valid model if needed
LOG_FILE = "toby_chat_history.txt"

# === Typing Effect ===
def type_like_toby(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # New line after typing

# === Memory (Conversation History) ===
conversation_history = [
    {"role": "system", "content": "You are Toby AI, a powerful assistant created by Spicy (Pureheart). Be helpful, smart, and friendly."}
]

# === Save Conversation to File ===
def save_conversation(user_input, ai_response):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"You: {user_input}\n")
        f.write(f"Toby: {ai_response}\n\n")

# === Ask Together AI with Debugging ===
def ask_together_ai():
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": TOGETHER_MODEL,  # Ensure this is correct, i.e., it is a valid model name
        "messages": conversation_history,  # History of conversation
        "temperature": 0.7,
        "max_tokens": 500,
    }

    # Debugging: Print the payload being sent
    print("Payload being sent to Together API:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Debugging: Print the raw response for error diagnosis
        print("Response from Together API:")
        print(response.text)
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# === Main Chat Loop ===
def main():
    os.system("cls" if os.name == "nt" else "clear")
    type_like_toby("Toby: Hello, I'm Toby! Type your questions below. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "goodbye"]:
            type_like_toby("Toby: Goodbye, Spicy.")
            break

        conversation_history.append({"role": "user", "content": user_input})
        ai_response = ask_together_ai()
        conversation_history.append({"role": "assistant", "content": ai_response})

        type_like_toby(f"Toby: {ai_response}")
        save_conversation(user_input, ai_response)

if __name__ == "__main__":
    main()
