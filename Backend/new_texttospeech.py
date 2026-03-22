import os
import re
import asyncio
import random
import threading
import queue
import pygame
import edge_tts
from dotenv import dotenv_values
from gemma import ask_gemma
from StateManager import state_manager

# ────── ENV ─────────────────────────────────────────────
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")

os.makedirs("Data", exist_ok=True)

# ────── QUEUE SYSTEM (prevents overlap) ─────────────────
tts_queue = queue.Queue()
tts_running = True


# ────── SENTENCE SPLITTER ──────────────────────────────
def split_sentences(text: str):
    return re.split(r'(?<=[.!?]) +', text)


# ────── GEMMA SUMMARIZER ───────────────────────────────
def Summarize(text: str) -> str:
    system_prompt = f"""
You are {Assistantname}. Summarize the following response for {Username}.

Keep it short, natural, conversational.
No bullets, no numbering.

---
{text}
---
"""
    try:
        response = ask_gemma(system_prompt)
        lines = [ln.strip() for ln in response.splitlines() if ln.strip()]
        return " ".join(lines)
    except Exception as e:
        print(f"[Summarize Error] {e}")
        return text[:200]  # fallback


# ────── ASYNC TTS GENERATOR ────────────────────────────
async def generate_audio(text: str, file_path: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=AssistantVoice,
        pitch="+5Hz",
        rate="+13%",
    )
    await communicate.save(file_path)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


# ────── AUDIO PLAYER THREAD ────────────────────────────
def tts_worker():
    pygame.mixer.init()

    while tts_running:
        try:
            text = tts_queue.get(timeout=1)
        except queue.Empty:
            continue

        if not state_manager.get_speaker_status():
            continue

        file_path = f"Data/speech_{random.randint(1000,9999)}.mp3"

        try:
            run_async(generate_audio(text, file_path))

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            clock = pygame.time.Clock()

            while pygame.mixer.music.get_busy():
                clock.tick(10)

        except Exception as e:
            print(f"[TTS Error] {e}")

        finally:
            try:
                pygame.mixer.music.stop()
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass


# ────── START WORKER THREAD ────────────────────────────
threading.Thread(target=tts_worker, daemon=True).start()


# ────── MAIN API ───────────────────────────────────────
def TextToSpeech(text: str):
    if not state_manager.get_speaker_status():
        return

    sentences = split_sentences(text)

    responses = [
        "The rest of the result is on the chat screen.",
        "Check the chat screen for more details.",
        f"{Username}, the full answer is on the chat screen.",
        "I've shown the rest in the chat.",
    ]

    # Smart summarization trigger
    if len(sentences) > 4 and len(text) > 250:
        summary = Summarize(text)
        final_text = summary + " " + random.choice(responses)
    else:
        final_text = text

    tts_queue.put(final_text)


# ────── CLEAN SHUTDOWN ─────────────────────────────────
def stop_tts():
    global tts_running
    tts_running = False
    pygame.mixer.quit()


# ────── TEST ───────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()

    while True:
        user_input = input("Enter text: ")
        if user_input.lower() == "exit":
            stop_tts()
            break
        TextToSpeech(user_input)