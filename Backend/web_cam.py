# web_cam.py – BLIP webcam caption/VQA
# Works on GPU if present, otherwise optimised CPU fallback (multithreaded).

from __future__ import annotations
import argparse, sys, warnings, os
from typing import Optional

import cv2
from PIL import Image
import torch
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    BlipForQuestionAnswering,
    GenerationConfig,
    logging as hf_logging,
)

print("[web_cam] imports done")

# ── Device & dtype ────────────────────────────────────────────
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
USE_CUDA = DEVICE.type == "cuda"
print(f"[web_cam] using {DEVICE}")

if not USE_CUDA:
    # Max out CPU threads for speed
    torch.set_num_threads(os.cpu_count())
    print(f"[web_cam] CPU threads: {os.cpu_count()}")

DTYPE = torch.float16 if USE_CUDA else torch.float32

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
hf_logging.set_verbosity_error()

if USE_CUDA:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True

# ── Models ────────────────────────────────────────────────────
_CAP_MODEL_NAME = "Salesforce/blip-image-captioning-base"
_VQA_MODEL_NAME = "Salesforce/blip-vqa-base"

_cap_processor = _cap_model = _qa_processor = _qa_model = None
FAST = {"use_fast": True}

def open_webcam(cam_index: int = 0, max_edge: int = 400) -> "Webcam":
    return Webcam(cam_index, max_edge)

def close_webcam(cam: "Webcam") -> None:
    if isinstance(cam, Webcam):
        cam.release()

@torch.no_grad()
def _lazy_load():
    global _cap_processor, _cap_model, _qa_processor, _qa_model
    if _cap_model is not None:
        return

    _cap_processor = BlipProcessor.from_pretrained(_CAP_MODEL_NAME, **FAST)
    _cap_model = BlipForConditionalGeneration.from_pretrained(
        _CAP_MODEL_NAME,
        torch_dtype=DTYPE if USE_CUDA else None
    ).to(DEVICE).eval()

    _qa_processor = BlipProcessor.from_pretrained(_VQA_MODEL_NAME, **FAST)
    _qa_model = BlipForQuestionAnswering.from_pretrained(
        _VQA_MODEL_NAME,
        torch_dtype=DTYPE if USE_CUDA else None
    ).to(DEVICE).eval()

    if USE_CUDA:
        # Warm‑up for lower latency
        dummy = torch.zeros(1, 3, 16, 16, dtype=DTYPE, device=DEVICE)
        _cap_model.vision_model(dummy)
        _qa_model.vision_model(dummy)

# ── Webcam wrapper ────────────────────────────────────────────
class Webcam:
    def __init__(self, cam_index: int = 0, max_edge: int = 400):
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open webcam {cam_index}")
        self.max_edge = max_edge

    def snap(self) -> Image.Image:
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Failed to read frame from webcam")
        h, w, _ = frame.shape
        scale = self.max_edge / max(h, w)
        if scale < 1.0:
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    def release(self):
        if getattr(self, "cap", None):
            self.cap.release()
            self.cap = None

    __enter__ = lambda self: self
    __exit__ = lambda self, exc_type, exc_val, exc_tb: self.release()

# ── Inference helpers ────────────────────────────────────────
@torch.no_grad()
def caption_image(img: Image.Image, max_len: int = 40) -> str:
    _lazy_load()
    inputs = _cap_processor(img, return_tensors="pt").to(DEVICE)
    cfg = GenerationConfig(max_new_tokens=max_len, num_beams=1, do_sample=False)
    if USE_CUDA:
        with torch.autocast("cuda", dtype=DTYPE):
            ids = _cap_model.generate(**inputs, generation_config=cfg)
    else:
        ids = _cap_model.generate(**inputs, generation_config=cfg)
    return _cap_processor.decode(ids[0], skip_special_tokens=True).strip()

@torch.no_grad()
def answer_question(img: Image.Image, question: str, max_len: int = 40) -> str:
    if not question.strip():
        raise ValueError("Question cannot be blank.")
    _lazy_load()
    inputs = _qa_processor(img, question, return_tensors="pt").to(DEVICE)
    cfg = GenerationConfig(max_new_tokens=max_len, num_beams=1, do_sample=False)
    if USE_CUDA:
        with torch.autocast("cuda", dtype=DTYPE):
            ids = _qa_model.generate(**inputs, generation_config=cfg)
    else:
        ids = _qa_model.generate(**inputs, generation_config=cfg)
    return _qa_processor.decode(ids[0], skip_special_tokens=True).strip()

# ── CLI loop ────────────────────────────────────────────────
def _interactive(new_snap_each_time: bool = True):
    with open_webcam() as cam:
        print(f"📸  BLIP webcam on {DEVICE} · dtype {DTYPE}")
        img: Optional[Image.Image] = None
        while True:
            if new_snap_each_time or img is None:
                input("\n⏎  Press Enter to capture (Ctrl+C to quit)…")
                img = cam.snap()
                print("✅  Captured. Ask anything about this frame.")
            try:
                q = input("🤔  Your question (blank to quit): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not q:
                break
            ans = answer_question(img, q)
            print(f"🤖  {ans}")

# ── Entry point ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLIP webcam caption/VQA")
    parser.add_argument("--once", action="store_true",
                        help="one snapshot, many questions")
    args = parser.parse_args()
    try:
        _interactive(new_snap_each_time=not args.once)
    except KeyboardInterrupt:
        print("\n⏹️  Aborted by user.")