# cad_generator_quiet.py  — Groq‑SDK + auto‑simplify retry
from __future__ import annotations
import json

import base64, os, re, sys, time, subprocess
from pathlib import Path
from typing import Optional, Final

import requests
from dotenv import dotenv_values
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from groq import Groq

# ── ENV ────────────────────────────────────────────────────────────────
env = dotenv_values(".env")
ZOO_API_KEY:  Final[str]         = env.get("ZOO_API_KEY")  or sys.exit("❌  ZOO_API_KEY missing")
GROQ_API_KEY: Final[str | None]  = env.get("GroqAPIKey")   # optional
client: Optional[Groq]           = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

HEADERS_ZOO = {"Authorization": f"Bearer {ZOO_API_KEY}", "Content-Type": "application/json"}
ZOO_SUBMIT_URL = "https://api.zoo.dev/ai/text-to-cad/step"
ZOO_STATUS_PATTERNS = [
    "https://api.zoo.dev/user/text-to-cad/{id}",
    "https://api.zoo.dev/ai/text-to-cad/step/{id}",
    "https://api.zoo.dev/ai/text-to-cad/jobs/{id}",
    "https://api.zoo.dev/ai/jobs/{id}",
]
SUCCESS, FAIL = {"succeeded", "completed", "success"}, {"failed", "cancelled", "error"}
REQUEST_TIMEOUT, POLL_INTERVAL = 30, 10

SESSION = requests.Session()
SESSION.headers.update(HEADERS_ZOO)

# ── HELPERS ────────────────────────────────────────────────────────────
def _groq_refine(prompt: str) -> str:
    if client is None:
        raise RuntimeError("Groq key not set")
    resp = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system",
             "content": "You are a CAD prompt engineer. Output ONLY one concise, precise prompt suitable for mechanical Text‑to‑CAD."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.2,
        top_p=1,
        stream=False,
    )
    return resp.choices[0].message.content.strip()

def _post_json(url: str, payload: dict) -> dict:
    r = SESSION.post(url, json=payload, timeout=REQUEST_TIMEOUT); r.raise_for_status(); return r.json()

def _get_json(url: str) -> dict:
    r = SESSION.get(url, timeout=REQUEST_TIMEOUT); r.raise_for_status(); return r.json()

def _submit_zoo(prompt: str, units: str) -> str:
    job_id = _post_json(ZOO_SUBMIT_URL, {"prompt": prompt, "units": units, "timeout": 900}).get("id")
    if not job_id: sys.exit("❌  Zoo: no job ID returned")
    return job_id

def _status_url(job_id: str) -> str:
    for pattern in ZOO_STATUS_PATTERNS:
        url = pattern.format(id=job_id)
        try:
            SESSION.get(url, timeout=REQUEST_TIMEOUT).raise_for_status()
            return url
        except requests.RequestException:
            continue
    raise RuntimeError("❌  Zoo status endpoint unreachable")

def _wait_done(url: str, max_wait: int) -> dict:
    waited = 0
    while waited < max_wait:
        data = _get_json(url)
        state = str(data.get("status", "")).lower()
        if state in SUCCESS: return data
        if state in FAIL:    raise RuntimeError(f"Zoo job failed: {json.dumps(data)}") 
        time.sleep(POLL_INTERVAL); waited += POLL_INTERVAL
    raise TimeoutError("Zoo job timed out")

def _b64decode(text: str) -> bytes:
    text = "".join(text.split()); text += "=" * ((4 - len(text) % 4) % 4)
    return base64.b64decode(text)

def _save_step(outputs: dict, out_path: Path) -> Path:
    step_key = next((k for k in outputs if k.lower().endswith(".step")), None)
    if not step_key: raise RuntimeError("No STEP entry in outputs")
    val = outputs[step_key]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(val, str) and val.startswith("http"):
        with SESSION.get(val, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for c in r.iter_content(chunk_size=1 << 15): f.write(c)
        return out_path
    out_path.write_bytes(_b64decode(val)); return out_path

# remove styling / font words Zoo hates
def _simplify_prompt(p: str) -> str:
    tokens = ["bold", "font", "sans-serif", "serif", "centered", "raised", "engraved", "engrave"]
    simplified = p
    for t in tokens:
        simplified = re.sub(rf"\b{t}\b.*?(?=[.,;]|$)", "", simplified, flags=re.I)
    simplified = re.sub(r"\s{2,}", " ", simplified).strip()
    return simplified

# ── MAIN GENERATOR ─────────────────────────────────────────────────────
def _try_once(prompt: str, units="mm") -> Path:
    job_id  = _submit_zoo(prompt, units)
    result  = _wait_done(_status_url(job_id), 900)
    return _save_step(result.get("outputs") or {}, Path("Data/model.step"))

def generate_cad(prompt: str) -> None:
    # 1. Groq refine (optional)
    try:
        prompt_groq = _groq_refine(prompt)
        print(f"Groq prompt: {prompt_groq}")
    except Exception:
        prompt_groq = None

    use_prompt = prompt_groq or prompt

    # 2. First attempt
    try:
        path = _try_once(use_prompt)
        _open_in_fusion360(path)
        print("Generation done. Opening Fusion 360…")
        return
    except RuntimeError as exc:
        if "422 Unprocessable Entity" not in str(exc):
            raise  # unrelated failure

        # 3. Retry with simplified prompt
        simple = _simplify_prompt(use_prompt)
        print("Retrying with simplified prompt…")
        try:
            path = _try_once(simple)
            _open_in_fusion360(path)
            print("Generation done (simplified). Opening Fusion 360…")
        except Exception as exc2:
            raise exc2  # bubble up final error

def _open_in_fusion360(step_path: Path) -> None:
    try:
        os.startfile(step_path)  # type: ignore[attr-defined]
    except AttributeError:
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open",
                        str(step_path)], check=False)

# ── CLI ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    part = input("Describe your part: ").strip()
    if not part: sys.exit("❌  Empty prompt")
    print("Generating…")
    try:
        generate_cad(part)
    except (HTTPError, ConnectionError, Timeout, RequestException, RuntimeError) as e:
        sys.exit(f"❌  Error: {e}")