import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# -------------------------------
# Check GPU (CUDA)
# -------------------------------

print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
else:
    print("Running on CPU (slow)")

# -------------------------------
# Model path
# -------------------------------

model_path = "D:\OMNI_AGENT\SLM"

# -------------------------------
# 4-bit quantization (fits in VRAM)
# -------------------------------

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

# -------------------------------
# Load tokenizer
# -------------------------------

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path)

# -------------------------------
# Load model
# -------------------------------

print("Loading model...")

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto"
)

print("Model loaded successfully!")
print("Model running on:", model.device)

# -------------------------------
# Conversation memory
# -------------------------------

history = ""

# -------------------------------
# Chat loop
# -------------------------------

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Assistant: Goodbye!")
        break

    # Build prompt with context
    history += f"\nUser: {user_input}\nAssistant:"

    prompt = f"""
You are a friendly helpful AI assistant.

Respond naturally to the user's message.

User: {user_input}
Assistant:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
    **inputs,
    max_new_tokens=1000,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.15,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract assistant reply only
    response = response.split("Assistant:")[-1].strip()

    print("Assistant:", response)

    history += " " + response