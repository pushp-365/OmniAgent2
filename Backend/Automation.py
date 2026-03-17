from AppOpener import close,open as appopen
import webbrowser
import random
import builtins
from pywhatkit import search, playonyt
from dotenv import dotenv_values

# from reminder import handle_reminders
# from cad_generator import generate_cad

# from Backend.cad_generator import generate_cad
# from Backend.reminder import save_remenders

from bs4 import BeautifulSoup
import re
from rich import print
from groq import Groq
import webbrowser
import subprocess
import keyboard
import requests
import asyncio
import time


try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
except ImportError:
    AudioUtilities = IAudioEndpointVolume = None      # absolute volume disabled

try:
    import screen_brightness_control as sbc           # absolute brightness
except ImportError:
    sbc = None



env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username" )
Assistantname = env_vars.get("Assistantname")


# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
# List to store chatbot messages.
messages = []

SystemChatBot = [{
    "role": "system",
    "content": (
        f"Hello, I am {Username}. "
        f"You are {Assistantname}, a professional content writer. You write essays, applications, poems, letters, kundlis(with respect to information provided), etc."
    )
}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def OpenNotePad(File):
    default_text_editor='notepad.exe'
    subprocess.Popen([default_text_editor, File])

# def Content(Topic):
#     def ContentWriterAI(prompt):
#         messages = [{"role": "user", "content": prompt}]
#         chat = SystemChatBot + messages

#         completion = client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=chat,
#             max_tokens=2048,
#             temperature=0.7,
#             top_p=1,
#             stream=True
#         )

#         answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 answer += chunk.choices[0].delta.content

#         return answer.replace("</s>", "")

#     Topic = Topic.replace("content ", "")
#     ContentByAI = ContentWriterAI(Topic)

#     filename = rf"Data\{Topic.lower().replace(' ', '')}.txt"
#     with builtins.open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)

#     OpenNotePad(filename)
#     return True

def YoutubeSearch(Topic):
    Url4Search= f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True




def PlayYoutube(query: str | None = None) -> bool:
    fav_songs = [
        "Ajab Si","Kun Faya Kun","Zinda","Ilahi",
        "Berklee Indian Ensemble ft Shreya Ghoshal"
    ]
    clean = (query or "").strip()

    if not clean or clean.lower() == "fav_songs":
        playonyt(random.choice(fav_songs))
    else:
        playonyt(clean)
    return True


def OpenApp(name: str, *, sess: requests.Session | None = None) -> bool:
    sess = sess or requests.Session()
    if name.lower() == "comment":
        webbrowser.open("https://www.perplexity.ai/b/home")
    try:
        appopen(name, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as exc:                       # narrow this if you can
        print(f"Appopen failed: {exc}. Falling back to web search…")

    try:
        html = sess.get(
            f"https://www.google.com/search?q={name}",
            headers={"User-Agent": useragent},
            timeout=10,
        ).text
        soup = BeautifulSoup(html, "html.parser")
        link = next((a["href"] for a in soup.select("a[jsname='UWckNb']")), None)
        if not link:
            raise ValueError("No result link found.")
        webbrowser.open(link)
        return True
    except Exception as exc:
        print(f"Fallback failed: {exc}")
        return False

def closeApp(app):
    if "chrome"in app :
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
        
def System(command: str) -> bool:
    cmd = command.lower().strip()

    # ── Shortcuts ───────────────────────────────────────────────
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")
    def brightness_up(): keyboard.press_and_release("brightness up")
    def brightness_down(): keyboard.press_and_release("brightness down")
    def screen_toggle(): keyboard.press_and_release("alt+tab")
    

    # ── Absolute volume (safe with COM init) ───────────────────
    def set_volume(level: int) -> bool:
        try:
            import comtypes
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL

            comtypes.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return True
        except Exception as e:
            print("❌ Volume set failed:", e)
            return False
        finally:
            try: comtypes.CoUninitialize()
            except: pass

    # ── Absolute brightness ────────────────────────────────────
    def set_brightness(level: int) -> bool:
        if sbc is None:
            print("⚠️  Install: pip install screen_brightness_control")
            return False
        try:
            sbc.set_brightness(level)
            return True
        except Exception as e:
            print("❌ Brightness set failed:", e)
            return False

    # ── Routing ────────────────────────────────────────────────
    if "mute" in cmd and "unmute" not in cmd: return mute() or True
    if "unmute" in cmd: return unmute() or True
    if "volume up" in cmd: return volume_up() or True
    if "volume down" in cmd: return volume_down() or True
    if "brightness up" in cmd: return brightness_up() or True
    if "brightness down" in cmd: return brightness_down() or True
    if "screen toggle" in cmd or "toggle screen"in cmd or "change screen" in cmd or cmd == "alt tab": return screen_toggle() or True

    # Absolute volume
    if m := re.fullmatch(r"volume\s+(\d{1,3})", cmd):
        level = int(m.group(1))
        if 0 <= level <= 100:
            return set_volume(level)
        else:
            print("⚠️ Volume must be 0-100")
            return False

    # Absolute brightness
    if m := re.fullmatch(r"brightness\s+(\d{1,3})", cmd):
        level = int(m.group(1))
        if 0 <= level <= 100:
            return set_brightness(level)
        else:
            print("⚠️ Brightness must be 0-100")
            return False

    print("⚠️ Unknown command:", command)
    return False        
   
async def TranslateAndExecute(commands):
    """
    For each string in *commands* fire the appropriate function in a thread
    and yield its result.  Keeps running even if one command crashes.
    """
    tasks = []

    for raw in commands:
        cmd   = raw.strip()
        lower = cmd.lower()

        # OPEN -----------------------------------------------------------------
        if lower.startswith("open "):
            if lower.startswith("open it"):
                print("[yellow]⚠️  'open it' branch not implemented")
            elif lower.startswith("open file"):
                print("[yellow]⚠️  'open file' branch not implemented")
            else:
                tasks.append(asyncio.to_thread(OpenApp, cmd[5:].strip()))
        # elif lower.startswith("reminder "):
        #     tasks.append(asyncio.to_thread(add_reminder, cmd[9:].strip()))

        # CLOSE ----------------------------------------------------------------
        elif lower.startswith("close "):
            tasks.append(asyncio.to_thread(closeApp, cmd[6:].strip()))
        #Reminders--------------------------------------------------------------
       
        # PLAY -----------------------------------------------------------------
         
        elif lower.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd[5:].strip()))    

        # # CONTENT --------------------------------------------------------------
        # elif lower.startswith("content "):
        #     tasks.append(asyncio.to_thread(Content, cmd[8:].strip()))

        # GOOGLE SEARCH --------------------------------------------------------
        elif lower.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd[14:].strip()))

        # YOUTUBE SEARCH -------------------------------------------------------
        elif lower.startswith("youtube search "):
            tasks.append(asyncio.to_thread(YoutubeSearch, cmd[15:].strip()))

        # SYSTEM ---------------------------------------------------------------
        elif lower.startswith("system "):
            tasks.append(asyncio.to_thread(System, cmd[7:].strip()))
        
        # elif lower.startswith("3d cad "):
        #     async def _cad_flow(raw: str):
        #         print("Generating 3-D CAD…")            #  announce start
        #         try:
        #             await asyncio.to_thread(generate_cad, raw)
        #             print("3d generation completed, Opening fusion.")  #  success
        #         except Exception as e:
        #             print(f"[red]❌  CAD generation error: {e}")          #  show error

        #     tasks.append(asyncio.create_task(_cad_flow(cmd[7:].strip())))
        # # UNWIRED BRANCHES -----------------------------------------------------


        elif lower.startswith("general ") or lower.startswith("realtime "):
            print(f"[yellow]⚠️  '{cmd.split()[0]}' branch not implemented")

        else:
            print(f"[red]❓  No handler found for: {cmd!r}")

    # Nothing scheduled? exit quietly
    if not tasks:
        return

    # Run them concurrently, swallow exceptions into the result list
    for result in await asyncio.gather(*tasks, return_exceptions=True):
        if isinstance(result, Exception):
            print(f"[red]❌  Task error: {result}")
        else:
            yield result

async def Automation(commands):
    """
    Wrapper: execute a batch and show a simple console report.
    """
    async for res in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    asyncio.run(Automation(['google search for good ai', 'youtube search a good ai']))