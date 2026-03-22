# new_model.py

from sentence_transformers import SentenceTransformer, util
import torch
import re

# -------------------------------
# LOAD MODEL
# -------------------------------
model = SentenceTransformer('intent_model/all-MiniLM-L6-v2')

# -------------------------------
# INTENTS
# -------------------------------
funcs = [
    "exit","general","realtime","open","close","play",
    "generate image","system","content","google search",
    "youtube search","web cam","tell reminder"
]

# -------------------------------
# INTENT EXAMPLES
# -------------------------------
intent_data = {
    "general": ["who are you", "tell me something","hey","hello"],
    "open": ["open chrome", "open whatsapp", "open vs code"],
    "close": ["close chrome", "close whatsapp"],
    "play": ["play music", "play song", "start music"],
    "realtime": ["what is time", "weather today", "temperature now"],
    "google search": ["search for ai updates", "find best phone under 15000","search videos on chrome"],
    "youtube search": ["search youtube", "youtube video"],
    "system": ["volume up", "brightness down", "mute system","inc volume","set volume 59"],
    "generate image": ["generate image of iron man", "create image o a black cat flying"]
}

# -------------------------------
# BUILD EMBEDDINGS
# -------------------------------
examples = []
labels = []

for intent, exs in intent_data.items():
    for e in exs:
        examples.append(e)
        labels.append(intent)

embeddings = model.encode(examples, convert_to_tensor=True)

# -------------------------------
# SPLIT (CRITICAL FIX)
# -------------------------------
def split_input(text):
    text = text.lower()

    # split connectors
    base = re.split(r"\band\b|\balso\b|,|then", text)

    final = []

    for part in base:
        words = part.strip().split()

        current = []
        for word in words:
            # intent trigger words
            if word in ["open","close","play","google","youtube","volume","brightness","time","weather"]:
                if current:
                    final.append(" ".join(current))
                    current = []

            current.append(word)

        if current:
            final.append(" ".join(current))

    return [p.strip() for p in final if p.strip()]

# -------------------------------
# CLASSIFY (EMBEDDING)
# -------------------------------
def classify(text):
    emb = model.encode(text, convert_to_tensor=True)
    scores = util.cos_sim(emb, embeddings)[0]

    idx = torch.argmax(scores)
    return labels[idx]

# -------------------------------
# CLEAN
# -------------------------------
def clean(intent, text):
    if text.startswith(intent):
        text = text[len(intent):].strip()
    return text

# -------------------------------
# FIXES
# -------------------------------
def fix_play(text):
    if not text or text in ["music", "song", "songs"]:
        return "fav_songs"
    return text

def fix_search(intent, text):
    text = re.sub(r"(search|google|youtube|about|for)", "", text).strip()
    return text

def fix_realtime(text):
    if not text.endswith("?"):
        text += "?"
    return text

def fix_system(text):
    if "inc" in text:
        return "volume up"
    elif "dec" in text:
        return "volume down"
    elif f"volume {int}" in text:
        return f"volume {int}"
    return text
    

# -------------------------------
# MAIN FUNCTION
# -------------------------------
def FirstLayerDMM(prompt: str = "test", last_queries: list = [], depth: int = 0):

    parts = split_input(prompt)

    results = []

    for part in parts:
        intent = classify(part)

        if intent not in funcs:
            intent = "general"

        phrase = clean(intent, part)

        if intent == "play":
            phrase = fix_play(phrase)

        if intent in ["google search", "youtube search"]:
            phrase = fix_search(intent, phrase)

        if intent == "realtime":
            phrase = fix_realtime(phrase)

        if intent == "system":
            phrase = fix_system(phrase)

        if phrase:
            results.append(f"{intent} {phrase}")
        else:
            results.append(intent)

    return results


# -------------------------------
# TEST
# -------------------------------
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))