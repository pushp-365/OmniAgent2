import pygame
import random
import asyncio
import edge_tts 
import os
from dotenv import dotenv_values
from groq import AsyncGroq
from Backend.StateManager import state_manager
from Backend.new_chatbot import ChatBot

# ────── ENV & CLIENTS ───────────────────────────────────────────────────────────
env_vars       = dotenv_values(".env")
Username       = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

AssistantVoice = env_vars.get("AssistantVoice")
GroqAPIKey     = env_vars.get("GroqAPIKey")

groq_client = AsyncGroq(api_key=GroqAPIKey)

answer: list[str] = []        # spoken‑summary lines

os.makedirs("Data", exist_ok=True)   # guarantee output folder


# ────── SUMMARISER ──────────────────────────────────────────────────────────────
async def Summarize(text: str) -> list[str]:
    prompt = (
    f"You are an AI assistant named {Assistantname}. Below is the full answer you previously gave to the user {Username}.\n\n"
    "Your task is to summarize this answer into a few short, clear, plain sentences.\n"
    "Speak naturally, like in a conversation. Use first-person ('I', 'me') and second-person ('you') pronouns where appropriate.\n"
    "Do not use numbering, bullets, or any list formatting. Just write simple, flowing sentences.\n\n"
    f"Answer to summarize:\n---\n{text}\n---"
)

    chat = await groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=2048,      # current SDK param name
        temperature=0.7,
    )
    lines = [
        ln.strip("•*- ").strip()
        for ln in chat.choices[0].message.content.splitlines()
        if ln.strip()
    ]
    return [ln if ln.endswith(".") else ln + "." for ln in lines]


# ────── EDGE‑TTS HELPER ─────────────────────────────────────────────────────────
async def TextToAudioFile(text: str) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(
        text,
        voice=AssistantVoice,
        pitch="+5Hz",
        rate="+13%",
    )
    await communicate.save(file_path)


def TTS(text: str, func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(text))
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                if func() is False:
                    break
                clock.tick(10)
            return True
        except Exception as e:
            print(f"Error in TTS: {e}")
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")


# ────── MAIN PUBLIC API ────────────────────────────────────────────────────────
def TextToSpeech(text: str, func=lambda r=None: True):
    # Check speaker status from GUI temp file
    try:
        speaker_status = open(r"Frontend\Files\Speaker.data", encoding="utf-8").read().strip()
        if speaker_status == "off":
            return
    except FileNotFoundError:
        pass  # Default to on if file doesn't exist

    if not state_manager.get_speaker_status():
        return
    global answer
    sentences = text.split(".")
    responses = [
        f"The rest of the result has been printed to the chat screen.",
        f"You can see the rest of the text on the chat screen",
        f"The remaining part of the text is now on the chat screen.",
        f"{Username}, you'll find more text on the chat screen for you to see.",
        f"{Username}, the chat screen holds the continuation of the text.",
        f"You'll find the complete answer on the chat screen, kindly check it out {Username}.",
        f"Please review the chat screen for the rest of the text.",
        f"{Username}, look at the chat screen for the complete answer.",
    ]

    long_enough = len(sentences) > 4 and len(text) >= 250
    if long_enough:
        answer = asyncio.run(Summarize(text))
        spoken = " ".join(answer) + " " + random.choice(responses)
        TTS(spoken, func)
    else:
        answer = []
        TTS(text, func)


# ────── REPL ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()  # Pygame needs init once in some environments
    while True:
        TextToSpeech(input("Enter the text: "))
        if answer:
            print("\nSpoken summary:")
            for line in answer:
                print("•", line)