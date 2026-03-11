import asyncio, urllib.parse, aiohttp, secrets
from random import randint
from PIL import Image, UnidentifiedImageError
import os
from time import sleep

# ── Config ────────────────────────────────────────────────────────────────
BATCH_N = 4
WIDTH   = 768
HEIGHT  = 768
MODEL   = "flux"                     # flux / nebula / photon / etc.

# ── Helpers ───────────────────────────────────────────────────────────────
def open_images(prompt: str):
    stem = prompt.replace(" ", "_")
    for i in range(1, BATCH_N + 1):
        path = os.path.join("Data", f"{stem}{i}.jpg")
        try:
            Image.open(path).show()
            print("opening:", path)
            sleep(0.8)
        except (IOError, UnidentifiedImageError):
            print("Unable to open", path)

# ── Pollinations GET wrapper with explicit seed ───────────────────────────
async def pollinations_fetch(prompt: str,
                             seed:   int,
                             width:  int = WIDTH,
                             height: int = HEIGHT,
                             model:  str = MODEL) -> bytes:
    base = "https://image.pollinations.ai/prompt/"
    q    = urllib.parse.quote(prompt)
    url  = (f"{base}{q}?model={model}&width={width}&height={height}"
            f"&private=true&seed={seed}")      # seed ⇒ guaranteed variation
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as s:
        r = await s.get(url)
        r.raise_for_status()
        return await r.read()

# ── Async image generator (4 independent seeds) ───────────────────────────
async def generate_images(prompt: str):
    os.makedirs("Data", exist_ok=True)
    tasks = [
        pollinations_fetch(
            f"{prompt}, 4K, ultra-detailed, high resolution",
            seed=secrets.randbelow(2**32)      # new random seed each call
        )
        for _ in range(BATCH_N)
    ]
    blobs = await asyncio.gather(*tasks)
    stem  = prompt.replace(" ", "_")
    for i, img in enumerate(blobs, 1):
        with open(fr"Data\{stem}{i}.jpg", "wb") as f:
            f.write(img)

def GenerateImage(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ── Main watcher loop ─────────────────────────────────────────────────────
TRIGGER_FILE = r"Frontend\Files\ImageGeneration.data"

while True:
    try:
        with open(TRIGGER_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
        if "," not in data:
            sleep(1); continue
        prompt, flag = data.split(",", 1)
        if flag == "True":
            print("Generating …")
            GenerateImage(prompt)
            with open(TRIGGER_FILE, "w", encoding="utf-8") as f:
                f.write("False,False")
            break
        sleep(1)
    except Exception as e:
        print("⚠️", e)
        sleep(1)