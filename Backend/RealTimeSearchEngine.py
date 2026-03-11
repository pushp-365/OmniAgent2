from ddgs import DDGS
from groq import Groq
from json import load, dump
from dotenv import dotenv_values
import datetime

env_vars = dotenv_values(".env")

Username = env_vars.get("Username" )
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
        chat_log = load(f)  # Load chat log with conversations
except FileNotFoundError:
    chat_log = [{"id": 1, "name": "Chat 1", "messages": []}]
    with open(r"Data\ChatLog.json", "w", encoding="utf-8") as f:
        dump(chat_log, f, ensure_ascii=False)

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

def GoogleSearch(query):
    try:
        results = list(DDGS().text(query, max_results=5))
        Answer = f"The search result for '{query}' are:\n[start]\n"
        for i in results:
            Answer += f"Title: {i.get('title', '')}\nDescription: {i.get('body', '')}\nLink: {i.get('href', '')}\n\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Error during search: {e}"

def ModifyAnswer(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]  # Filter out empty lines
    modified_answer = '\n'.join(non_empty_lines)  # Join non-empty lines back into a single string
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role":"user","content": "Hi"},
    {"role":"assistant","content": "Hello, how can I help you?"}
]

def Information():
    data=""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A") # Day of the week.
    date = current_date_time.strftime("%d") # Day of the month.
    month = current_date_time.strftime("%B") # Full month name.
    year = current_date_time.strftime("%Y") # Year.
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data +=f"Use this real time infromation if needed and if time is asked prefer to answer in 12 hr system,\n"
    data += f" day: {day}\n date: {date}\n month: {month}\n year: {year}\n"
    data += f" hour: {hour}\n minute: {minute}\n second: {second}\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages, chat_log, current_conv
    # Reload chat_log to get latest
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
            chat_log = load(f)
    except FileNotFoundError:
        chat_log = [{"id": 1, "name": "Chat 1", "messages": []}]

    # Get current conversation messages
    current_conv = next((c for c in chat_log if c["id"] == current_chat_id), chat_log[0])
    messages = current_conv.get("messages", [])

    messages.append({"role": "user", "content": f'{prompt}'})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=SystemChatBot+[{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None,
    )
    Answer=""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer =Answer.strip().replace("</s>", "")  # Clean up the answer by removing empty lines.
    messages.append({"role": "assistant", "content": Answer})

    # Update the chat_log with new messages
    current_conv["messages"] = messages
    with open(r"Data\ChatLog.json", "w", encoding="utf-8") as f:
        dump(chat_log, f, indent=4, ensure_ascii=False)

    SystemChatBot.pop() # Remove the last system message after processing.
    return ModifyAnswer(Answer=Answer)  # Return the cleaned answer.

if __name__ == "__main__":
    while True:
        prompt=input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))