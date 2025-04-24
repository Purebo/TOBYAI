from flask import Flask, render_template, request, jsonify
import requests
import os
import logging
import re

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
    
    # First, check if there are code blocks and format them properly
    message = format_code_blocks(message)
    
    # Regular text formatting for better readability
    message = message.replace(". ", ".<br><br>")
    message = message.replace("! ", "!<br><br>")
    message = message.replace("? ", "?<br><br>")
    
    return message

# Function to format code blocks nicely
def format_code_blocks(text):
    # Check if there are code blocks with triple backticks
    code_block_pattern = r"```(\w*)\n([\s\S]*?)\n```"
    
    def replacement(match):
        language = match.group(1) or ""
        code = match.group(2)
        
        # Indent code properly if it's not already
        formatted_code = indent_code(code, language)
        
        # Return formatted code with syntax highlighting classes
        return f'<pre class="code-block"><code class="language-{language}">{formatted_code}</code></pre>'
    
    # Replace code blocks with formatted HTML
    formatted_text = re.sub(code_block_pattern, replacement, text)
    return formatted_text

# Function to indent code based on its language
def indent_code(code, language):
    lines = code.split('\n')
    formatted_lines = []
    
    # Handle indentation and formatting based on language
    if language.lower() in ['python', 'py']:
        indent_level = 0
        for line in lines:
            # Clean up line
            line = line.rstrip()
            
            # Check for indentation changes
            if re.search(r':\s*$', line) and not line.strip().startswith(('#', '"', "'")):
                formatted_lines.append(line)
                indent_level += 1
            elif line.strip().startswith(('def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:')):
                # Reduce indent for new blocks
                if indent_level > 0 and line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:')):
                    if formatted_lines and not formatted_lines[-1].strip() == '':
                        formatted_lines.append('')  # Add blank line before new block
                formatted_lines.append(line)
                if line.endswith(':'):
                    indent_level += 1
            elif line.strip() == '':
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
                
    elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
        # Similar formatting logic for JavaScript/TypeScript
        indent_level = 0
        for line in lines:
            line = line.rstrip()
            
            # Handle bracket-based indentation
            if '{' in line and '}' not in line:
                formatted_lines.append(line)
                indent_level += 1
            elif '}' in line and '{' not in line:
                indent_level = max(0, indent_level - 1)
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
    
    elif language.lower() in ['html', 'xml']:
        # Basic HTML formatting
        for line in lines:
            formatted_lines.append(line.rstrip())
    else:
        # For other languages, just clean up whitespace
        for line in lines:
            formatted_lines.append(line.rstrip())
    
    # HTML escape the code to prevent rendering issues
    formatted_code = '\n'.join(formatted_lines)
    formatted_code = formatted_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    return formatted_code

# Format calculation steps for clarity
def format_calculations(text):
    # Format calculation steps with better spacing and readability
    text = re.sub(r'(\d+)\s*([+\-*/×÷=])\s*(\d+)', r'\1 \2 \3', text)
    text = re.sub(r'Step\s+(\d+):', r'<br><strong>Step \1:</strong>', text)
    return text

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

    # Enhanced system prompt with calculation instructions
    system_prompt = """
    You are Toby AI, created by Spicy (Pureheart). Be powerful, smart, helpful, and well-spoken.
    
    VERY IMPORTANT FORMATTING RULES:
    1. Always use proper spacing between words and after punctuation
    2. For calculations and math:
       - Show your work step by step in a clear, basic way
       - Use simple language that non-experts can understand
       - Explain what each step does
       - Present the final answer clearly after your calculations
       - Format your calculation steps as "Step 1:", "Step 2:", etc.
    
    When asked to write code:
    1. Always use proper indentation and spacing for readability
    2. Include comments to explain complex sections
    3. Use consistent formatting within each language
    4. Always wrap code in triple backticks with the language specified, like: ```python
    5. Structure your code logically with functions and classes where appropriate
    
    Answer questions directly and avoid repetitive greetings.
    """

    # Add conversation history to prevent repetitive responses
    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 800  # Increased token limit for more complete responses
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
                
                # Format the AI's reply
                ai_reply = format_calculations(ai_reply)  # Format calculation steps
                formatted_reply = format_message(ai_reply)
                
                # Fix common spacing issues
                formatted_reply = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', formatted_reply)
                formatted_reply = re.sub(r'\s{2,}', ' ', formatted_reply)
                
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
