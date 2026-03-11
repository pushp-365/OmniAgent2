
import os, sys, json, requests
from dotenv import dotenv_values

# ─── Load env vars ────────────────────────────────────────────────────────
env = dotenv_values(".env")           # reads .env in script directory
API_KEY  = env.get("OCR_SPACE_KEY") or os.getenv("OCR_SPACE_KEY") or ""
LANGUAGE = env.get("OCR_LANG", "eng")  # default to English

if not API_KEY:
    sys.exit("❌  Set OCR_SPACE_KEY in .env or environment variable.")

ENDPOINT = "https://api.ocr.space/parse/image"

# ─── Core function ────────────────────────────────────────────────────────
def ocr_space_image(path: str, lang: str = LANGUAGE) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    with open(path, "rb") as img:
        resp = requests.post(
            ENDPOINT,
            files={"filename": img},
            data={"apikey": API_KEY, "language": lang, "OCREngine": "2"},
            timeout=60,
        )

    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise RuntimeError(f"Non-JSON response: {resp.text[:120]}…")

    if data.get("IsErroredOnProcessing"):
        raise RuntimeError("; ".join(data.get("ErrorMessage", [])))

    return data["ParsedResults"][0]["ParsedText"].strip()

# ─── CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        img = input("🖼  Image path: ").strip('"').strip("'")
        print("\n📄 Extracted Text:\n")
        print(ocr_space_image(img) or "⚠️  No text detected.")
    except Exception as e:
        sys.exit(f"❌  {e}")