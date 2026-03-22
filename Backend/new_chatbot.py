# new_chatbot.py - Fixed imports & ChatBot for Main.py integration

import sys
import os
from pathlib import Path

# Fix imports when run from different dirs
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Backend.gemma import ask_gemma
import datetime
from dotenv import dotenv_values
import subprocess
import time
import requests

# --- LOAD ENV ---
env_vars = dotenv_values(".env")
Username = env_vars.get("Username" )
Assistantname = env_vars.get("Assistantname")
ollama_path = "D:\ollama\Ollama\ollama.exe"

# --- ABILITIES ---
abili = """
Speech recognition, search youtube and google,cad generation, image generation, provide code.
"""

# --- BUILD SYSTEM PROMPT (WITH TIME INSIDE) ---
def build_system_prompt():
    now = datetime.datetime.now()

    return f"""
Your name is {Assistantname}, a highly advanced, precise AI assistant with real-time internet access, created by {Username}

RULES OF ENGAGEMENT:
────────────────────
***ONLY REPLY IN A PROFESSIONAL WAY IN ENGLISH***
***ALSO WHEN QUESTION IS ASKED IN HINDI REPLY IN ENGLISH***
***IF USER ASK YOU TO REPLY IN HINDI, USE ENGLISH SCRIPT TO REPLY IN HINDI, i.e. REPLY IN HINGLISH***
IDENTITY RULES:
- The user's name is {Username}
- If asked "what is my name" → answer: "{Username}"
- If asked "who am I" → answer: "{Username}"



🕒 Never state the current time unless explicitly asked.

🧠 Your creator is **Pushp** — always remember this.

🗣️ Language Protocol:
▸ Always respond in **English**, even to Hindi questions.
▸ Exception: If user **explicitly** asks for Hindi

*** YOU ARE A MODEL RESPONSIBLE FOR GENERAL QUERY HANDLER OF A HIGH TECH AI,
THE FULL ABILITIES OF THE AI MODEL ARE {abili}.
If abilities are asked like "can you do this task" and if the task is in {abili},
respond with "Yes, I can do this task".

Also if abilities are asked e.g. "what are your abilities",
respond like this or improve this:
"I am a highly advanced AI model, I can help with a wide range of tasks"
(from {abili}), analyze what tasks you can do.

Like if user asked "can you create 3D models?",
check in your {abili}. If you can make 3D models,
reply with "Yes, I can make 3D models." ***

Current Time is:
{now.strftime('%I:%M %p')}
"""

# --- START OLLAMA SERVER ---
def start_ollama():
    try:
        requests.get("http://127.0.0.1:11434")
        print("✅ Ollama already running")
        return
    except:
        print("🚀 Starting Ollama server...")

    subprocess.Popen(
        [ollama_path, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(3)

# --- LOAD MODEL ---
def load_model():
    try:
        requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": "hello",
                "stream": False
            }
        )
        print("✅ Gemma ready")
    except:
        print("❌ Failed to load model")

# --- MAIN CHATBOT FUNCTION (for Main.py integration) ---
def ChatBot(query: str):
    """
    Process single query using Gemma/Ollama.
    Returns response string.
    """
    # start_ollama()
    # load_model()
    
    full_prompt = build_system_prompt() + "\nUser: " + query + "\nAI:"
    
    response = ask_gemma(full_prompt)
    
    return response

# --- INTERACTIVE TEST MODE ---
if __name__ == "__main__":
    print(f"🚀 {Assistantname} standalone test (type 'exit' to quit)\n")
    start_ollama()
    load_model()
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = ChatBot(user_input)
            print(f"{Assistantname}: {response}\n")
        except KeyboardInterrupt:
            print("\n⚠️ Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")