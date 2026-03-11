from groq import Groq 
from json import load, dump
import datetime 
import time
import os
from dotenv import dotenv_values

# Load environment variables from the .env file.
abili=("""

1. Speech Recognition (Speech to Text)
- Implemented using Selenium with a headless Chrome browser.
- Uses browser-based JavaScript speech recognition API.
- Supports multiple input languages and automatic translation to English.

2. Text to Speech Synthesis
- Uses edge_tts library to generate speech audio files asynchronously.
- Plays audio using pygame with handling for long texts.

3. Conversational AI Chatbot
- Powered by Groq API with llama3-70b-8192 model.
- Supports real-time internet access for up-to-date responses.
- Includes domain-specific knowledge such as Kundli generation in Hindi.
- Manages chat logs and system instructions for context-aware conversations.

4. Real-Time Search Engine
- Uses googlesearch library to perform Google searches.
- Integrates Groq API to generate professional, grammatically correct answers.
- Provides real-time date and time information for context.

5. Task Automation
- Supports opening and closing applications, playing YouTube videos.
- Performs Google and YouTube searches.
- Generates content such as letters, codes, essays using Groq API.
- Controls system volume, brightness, mute/unmute.
- Uses asynchronous execution to handle multiple commands concurrently.

6. AI-Based Image Generation
- Generates high-resolution images using Pollinations API.
- Supports batch generation with random seeds for variation.
- Watches trigger files to start generation and saves images to disk.

7. Image to Text (OCR)
- Uses OCR.space API to extract text from images.
- Supports multiple languages with configurable API key.

8. Query Classification and Decision Making
- Uses Cohere API to classify user queries into categories like general, realtime, open, close, play, generate image, reminder, system, content, google search, youtube search, 3d cad, web cam, exit.
- Helps route queries to appropriate AI modules or actions.

9. GUI Interaction and User Interface Management
- Frontend GUI implemented in Python (Frontend/GUI.py).
- Manages assistant status, microphone status, text display, and chat integration.
- Orchestrates AI assistant workflow with multi-threading.
""")
env_vars = dotenv_values(".env")
# Retrieve specific environment variables for usernam
Username = env_vars.get("Username" )
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API k
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages.
messages = []
System = f"""
Hello, I am {Username}. You are {Assistantname}, a highly advanced, precise AI assistant with real-time internet access.

RULES OF ENGAGEMENT:
────────────────────
***ONLY REPLY IN A PROFESSIONAL WAY IN ENGLISH***
***ALSO WHEN QUESTION IS ASKED IN HINDI REPLY IN ENGLISH***
***IF USER ASK YOU TO REPLY IN HINDI, USE ENGLISH SCRIPT TO REPLY IN HINDI, i.e. REPLY IN HINGLISH***

🕒 Never state the current time unless explicitly asked.

🧠 Your creator is **Pushp** — always remember this.

🗣️ Language Protocol:
▸ Always respond in **English**, even to Hindi questions.
▸ Exception: If user **explicitly** asks for Hindi, or requests a **Kundli** using terms like:
["meri kundli", "janampatri", "kundali", "जन्मपत्री", etc.]

🖼️ Image Generation:
▸ If user asks for an image → Respond: **"Yes, of course I can generate high-quality images."**
▸ If user praises the image → Respond with gratitude.

📜 KUNDLI GENERATION RULES:
────────────────────────────
▸ Kundli generation is only possible using **Hindi** terms.

When user requests Kundli:
1. Ensure all three are available:
   - Date of Birth (dd/mm/yyyy)
   - Time of Birth (24-hour or AM/PM format)
   - Place of Birth (City, State, Country)

2. If any data is missing → Prompt for it **first** (in Hindi).

3. Once data is complete → Generate Kundli in Hindi using **this structure**:

📊 Use this table in Markdown codeblock style with proper Unicode alignment:

┌───────────────┬──────────────────────────────────────────────┐
│ शीर्षक         │ विवरण                                         │
├───────────────┼──────────────────────────────────────────────┤
│ लग्न           │ कन्या (उदाहरण)                               │
│ चन्द्र राशि     │ सिंह                                          │
│ नवमांश लग्न     │ वृश्चिक                                      │
│ प्रमुख दोष      │ शनि दोष                                      │
│ प्रमुख योग      │ चन्द्र–मंगल योग, गजकेसरी योग                 │
│ प्रभाव          │ जीवन में चुनौतियाँ व संघर्ष, सम्मान की प्राप्ति │
│ उपाय           │ शनि पूजा, चन्द्र–मंगल की उपासना              │
└───────────────┴──────────────────────────────────────────────┘

📌 Follow with bullet-point explanations:

🔍 दोष एवं योगों का प्रभाव:
• शनि दोष: करियर में बाधाएँ, मानसिक तनाव, स्वास्थ्य समस्याएँ  
• चन्द्र–मंगल योग: निर्णय क्षमता, आर्थिक लाभ, सौभाग्य  
• गजकेसरी योग: मान-सम्मान, समाज में प्रतिष्ठा, नेतृत्व  

🔧 उपाय:
• शनि दोष: शनिवार को शनि चालीसा, काले तिल व तेल का दान  
• चन्द्र–मंगल योग: शिव पूजा, दूध व गुड़ का दान  
• गजकेसरी योग: बृहस्पति मंत्र जाप, पीला वस्त्र धारण करना  

FORMATTING RULES:
─────────────────
▸ Use Unicode box-drawing characters for CLI aesthetics.
▸ Maintain spacing, precision, and professional tone.
▸ Avoid vague, generic or fortune-cookie phrasing (e.g., "life may be good").
▸ All Kundli output must be **in Hindi** only.

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
"""

# *** Reply in only Hinglish, when question is in Hindi or hinglish.***

# A list of system instructions for the chatbot.
SystemChatBot = [
{"role": "system", "content": System}

]
try:
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
        chat_log = load(f)  # Load chat log with conversations
except FileNotFoundError:
    chat_log = [{"id": 1, "name": "Chat 1", "messages": []}]
    with open(r"Data\ChatLog.json", "w", encoding="utf-8") as f:
        dump(chat_log, f, indent=2, ensure_ascii=False)

# Get current conversation
current_chat_id = 1
try:
    with open(r"Frontend\Files\CurrentChat.data", "r", encoding="utf-8") as f:
        current_chat_id = int(f.read().strip())
except FileNotFoundError:
    pass

if chat_log:
    current_conv = next((c for c in chat_log if c["id"] == current_chat_id), chat_log[0])
    messages = current_conv.get("messages", [])
else:
    messages = []

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime. datetime.now( )
    day = current_date_time. strftime("%A") # Day of the week.
    date = current_date_time. strftime("%d") # Day of the month.
    month = current_date_time. strftime("%B") # Full month name.
    year = current_date_time.strftime("%Y") # Year.
    hour = current_date_time. strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time. strftime("%S")

    data = f"Please use this real-time information if needed and if time is asked prefer to answer in 12 hr system,\n"
    data += f" day: {day}\n date: {date}\n month: {month}\n year: {year}\n"
    data += f" hour: {hour}\n minute: {minute}\n second: {second}\n"
    return data

def AnswerModifier(Answer):
    lines = Answer. split('\n')
    non_empty_lines = [line for line in lines if line.strip()] # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines) # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(query: str, history_limit: int = 6, retries: int = 3) -> str:
    """
    Send `query` to Groq, stream the answer, persist shortened chat log,
    auto‑back‑off on transient errors, and stay under the 6000‑TPM cap.
    """

    for attempt in range(retries):
        try:
            # --- Load Current Conversation ----------------------------------
            log_path = "Data/ChatLog.json"
            cid_path = "Frontend/Files/CurrentChat.data"
            
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    chat_log = load(f)
            except (FileNotFoundError, ValueError):
                chat_log = []

            # Get current chat ID
            current_id = 1
            if os.path.exists(cid_path):
                try:
                    with open(cid_path, "r", encoding="utf-8") as f:
                        current_id = int(f.read().strip())
                except: pass

            # Extract messages for history
            target_chat = next((c for c in chat_log if c.get("id") == current_id), None)
            if not target_chat and chat_log:
                target_chat = chat_log[0]
            
            chat_messages = target_chat.get("messages", []) if target_chat else []
            
            # keep only the last `history_limit` user+assistant pairs
            recent = chat_messages[-history_limit * 2 :]
            recent.append({"role": "user", "content": query})

            # --- Build the payload -----------------------------------------
            payload = (
                SystemChatBot
                + [{"role": "system", "content": RealtimeInformation()}]
                + recent
            )

            # --- Call Groq ---------------------------------------------------
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct", # Correcting to a reliable model
                messages=payload,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
            )

            answer = "".join(
                chunk.choices[0].delta.content
                for chunk in completion
                if chunk.choices[0].delta.content
            ).replace("</s>", "")

            # NOTE: We do NOT persist here. Main.py calls SaveMessageToJson.
            return AnswerModifier(answer)

        except Exception as err:
            wait = 2 ** attempt
            print(f"[WARN] Error in ChatBot: {err}. Retrying in {wait}s…")
            time.sleep(wait)

    # all retries failed
    return "⚠️  Sorry, the assistant is temporarily unavailable. Please try again."

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        
        print( ChatBot(user_input))