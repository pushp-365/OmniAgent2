from Frontend.GUI_2 import (  # type: ignore
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
    GetInputMode,
    GetTextQuery,
    SetTextQuery,
)

from Backend.Model import FirstLayerDMM
from Backend.RealTimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.ChatBot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.cad_generator import generate_cad

from dotenv import dotenv_values  # type:ignore
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ── Config & Globals ──────────────────────────────────────────────────────
env_vars = dotenv_values(".env")
print("Imports done")

Username: str | None = env_vars.get("Username")
Assistantname: str | None = env_vars.get("Assistantname")

def get_time_based_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        greeting = f"Good Morning {Username}"
    elif hour < 17:
        greeting = f"Good Afternoon {Username}"
    else:
        greeting = f"Good Evening {Username}"
    return greeting

def GetDefaultMessage() -> str:
    greeting = get_time_based_greeting()
    return (
        f"{Username}:Hello {Assistantname}, How are you?\n"
        f"{Assistantname}: {greeting}. I am doing great. How may I help you?"
    )

subprocesses: list[subprocess.Popen] = []
Functions = [
    "open",
    "close",
    "google search",
    "youtube search",
    "content",
    "system",
    "play",
]

# Commonly‑used paths ------------------------------------------------------
DATA_DIR = Path("Data")
CHATLOG_PATH = DATA_DIR / "ChatLog.json"
IMAGE_DATA_PATH = Path("Frontend/Files/ImageGeneration.data")
IMAGE_SCRIPT_PATH = Path("Backend/ImageGeneration.py").resolve()


# ── Helper Functions ─────────────────────────────────────────────────────

def ShowDefaultChatIfNoChats() -> None:
    CHATLOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CHATLOG_PATH.exists() or CHATLOG_PATH.stat().st_size < 5:
        Path(TempDirectoryPath("Database.data")).write_text("")
        Path(TempDirectoryPath("Responses.data")).write_text(GetDefaultMessage())


def ReadChatLogJson() -> list[dict]:
    if not CHATLOG_PATH.exists() or CHATLOG_PATH.stat().st_size == 0:
        return []
    with CHATLOG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def SaveMessageToJson(role: str, content: str) -> None:
    try:
        json_data = ReadChatLogJson()
        if not json_data:
            json_data = [{"id": 1, "name": "Default Chat", "messages": []}]
        
        current_chat_id = 1
        cid_path = Path(TempDirectoryPath("CurrentChat.data"))
        if cid_path.exists():
            cid_str = cid_path.read_text().strip()
            if cid_str.isdigit():
                current_chat_id = int(cid_str)

        # Find the current chat or default to the first one if not found
        target_chat = next((chat for chat in json_data if chat.get("id") == current_chat_id), None)
        if not target_chat and json_data:
            target_chat = json_data[0] # Fallback to the first chat if current_chat_id not found

        if target_chat:
            if "messages" not in target_chat:
                target_chat["messages"] = []
            target_chat["messages"].append({"role": role, "content": content})
        else: # If no chats exist at all (should be caught by `if not json_data` but as a safeguard)
            json_data.append({"id": current_chat_id, "name": "New Chat", "messages": [{"role": role, "content": content}]})

        with CHATLOG_PATH.open("w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving message: {e}")


def ChatLogIntegration() -> None:
    json_data = ReadChatLogJson()
    
    # Get current chat ID
    current_chat_id = 1
    cid_path = Path(TempDirectoryPath("CurrentChat.data"))
    if cid_path.exists():
        cid_str = cid_path.read_text().strip()
        if cid_str.isdigit():
            current_chat_id = int(cid_str)
    
    # Find the current chat
    target_chat = next((chat for chat in json_data if chat.get("id") == current_chat_id), None)
    if not target_chat and json_data:
        target_chat = json_data[0]  # Fallback to first chat
    
    formatted_chatlog = ""
    if target_chat:
        for message in target_chat.get("messages", []):
            role = "USER" if message["role"] == "user" else "ASSISTANT"
            formatted_chatlog += f"{role}: {message['content']}\n"

    Path(TempDirectoryPath("Database.data")).write_text(
        AnswerModifier(formatted_chatlog), encoding="utf-8"
    )


def ShowChatsOnGUI() -> None:
    db_path = Path(TempDirectoryPath("Database.data"))
    data = db_path.read_text(encoding="utf-8") if db_path.exists() else ""
    if data:
        Path(TempDirectoryPath("Responses.data")).write_text(data, encoding="utf-8")


# ── Initialisation ───────────────────────────────────────────────────────

def InitialExecution() -> None:
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()


# ── Image Generation Launcher ────────────────────────────────────────────

def start_image_generation(query: str) -> None:
    IMAGE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMAGE_DATA_PATH.write_text(f"{query},True", encoding="utf-8")

    try:
        proc = subprocess.Popen(
            [sys.executable, str(IMAGE_SCRIPT_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        )
        subprocesses.append(proc)
        print("✅  ImageGeneration.py launched")
    except FileNotFoundError:
        print(f"❌  Script not found: {IMAGE_SCRIPT_PATH}")
    except Exception as e:
        print(f"❌  Failed to start ImageGeneration.py → {e}")


# ── CAD Handler (Threaded) ───────────────────────────────────────────────

def threaded_cad_handler(query: str):
    SetAssistantStatus("Generating 3D CAD ...")
    try:
        generate_cad(query)
        print("✅  3D generation completed, opening Fusion.")
        SetAssistantStatus("Fusion launched.")
    except Exception as e:
        print(f"❌  CAD generation error: {e}")
        SetAssistantStatus("CAD Generation Failed.")


# ── Main Execution Loop ──────────────────────────────────────────────────

def MainExecution() -> bool | None:
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    input_mode = GetInputMode()

    if input_mode == "voice":
        SetAssistantStatus("Listening ... ")
        Query: str = SpeechRecognition()
        ShowTextToScreen(f"{Username} : {Query}")
    else:  # text mode
        SetAssistantStatus("Waiting for text input ... ")
        Query = GetTextQuery()
        if not Query:
            return None  # No text query available yet
    ShowTextToScreen(f"{Username} : {Query}")
    SaveMessageToJson("user", Query)
    SetTextQuery("") # Clear text query once processed

    SetAssistantStatus("Thinking ... ")

    # Retrieve last 3-4 user queries for context
    json_data = ReadChatLogJson()
    current_chat_id = 1
    cid_path = Path(TempDirectoryPath("CurrentChat.data"))
    if cid_path.exists():
        cid_str = cid_path.read_text().strip()
        if cid_str.isdigit():
            current_chat_id = int(cid_str)

    target_chat = next((chat for chat in json_data if chat.get("id") == current_chat_id), None)
    if not target_chat and json_data:
        target_chat = json_data[0]

    last_queries = []
    if target_chat and "messages" in target_chat:
        user_messages = [msg["content"] for msg in target_chat["messages"] if msg["role"] == "user"]
        last_queries = user_messages[-4:]  # Get last 4 user queries

    Decision = FirstLayerDMM(Query, last_queries)

    print("\nDecision :", Decision, "\n")

    # Trigger CAD generation
    for q in Decision:
        if q.startswith("3d cad "):
            threading.Thread(target=threaded_cad_handler, args=(q,), daemon=True).start()

    # Flags
    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    # Merge general and realtime queries
    Mearged_query = " and ".join(
        " ".join(i.split()[1:])
        for i in Decision

        if i.startswith("general") or i.startswith("realtime")
    )

    # Trigger image generation
    for q in Decision:
        if q.startswith("generate "):
            ImageGenerationQuery = q
            ImageExecution = True
        if q.startswith("exit "):
            # exit the program, exit code 0
            sys.exit(0)

    # Handle automation tasks
    for q in Decision:
        if not TaskExecution and any(q.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        start_image_generation(ImageGenerationQuery)
    

    # Response generation
    if R:
        SetAssistantStatus("Searching ... ")
        answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
    else:
        general_queries = [q for q in Decision if q.startswith("general ")]
        if not general_queries:
            return None
        QueryFinal = general_queries[0].removeprefix("general ")
        answer = ChatBot(QueryModifier(QueryFinal))

    ShowTextToScreen(f"{Assistantname} : {answer}")
    SaveMessageToJson("assistant", answer)
    SetAssistantStatus("Answering ... ")
    TextToSpeech(answer)
    return True


# ── Thread Workers ───────────────────────────────────────────────────────

def FirstThread() -> None:
    while True:
        input_mode = GetInputMode()
        if input_mode == "voice":
            if GetMicrophoneStatus() == "True":
                MainExecution()
            else:
                if "Available" not in GetAssistantStatus():
                    SetAssistantStatus("Available ... ")
                sleep(0.1)
        else:
            # In text mode, MainExecution handles checking for queries
            MainExecution()
            sleep(0.1)


def SecondThread() -> None:
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")


# ── Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()