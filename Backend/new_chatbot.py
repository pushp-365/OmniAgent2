from gemma import ask_gemma
import datetime
from dotenv import dotenv_values

# --- LOAD ENV ---
env = dotenv_values(".env")

Username = env.get("Username", "User")
Assistantname = env.get("Assistantname", "Assistant")

# --- SYSTEM PROMPT ---
abili = """
Speech recognition, automation, search, content generation, image generation, etc.
"""

System = f"""
You are {Assistantname}, an AI assistant created by {Username}.

Rules:
- Always reply in English
- Be professional
- Follow instructions strictly
- If task is in abilities, say YES

Abilities:
{abili}
"""

# --- REALTIME ---
def get_realtime_info():
    now = datetime.datetime.now()
    return f"""
Current Date: {now.strftime('%d %B %Y')}
Current Time: {now.strftime('%I:%M %p')}
"""

# --- MEMORY ---
history = []

# --- CHAT LOOP ---
def chat():
    print(f"🚀 {Assistantname} started (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        history.append(f"User: {user_input}")

        full_prompt = (
            System
            + "\n"
            + get_realtime_info()
            + "\n"
            + "\n".join(history)
            + "\nAI:"
        )

        response = ask_gemma(full_prompt)

        history.append(f"AI: {response}")

        print("AI:", response)


if __name__ == "__main__":
    chat()