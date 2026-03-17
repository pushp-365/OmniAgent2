import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# -------------------------------
# Model path
# -------------------------------

model_path = r"D:\OMNI_AGENT\SLM"

# -------------------------------
# Quantization config
# -------------------------------

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

# -------------------------------
# Load tokenizer
# -------------------------------

tokenizer = AutoTokenizer.from_pretrained(model_path)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# -------------------------------
# Load model
# -------------------------------

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto"
)

# -------------------------------
# Memory
# -------------------------------

history = ""

# -------------------------------
# Ask Omni function
# -------------------------------
def askOmni(user_input, system_prompt=None):

    global history

    if system_prompt is None:
        system_prompt = """
You are OmniAgent, a precise AI assistant.
Rules:
-Answer only the user's question
-Do not invent new questions
-Keep responses concise
"""

    history += f"\nUser: {user_input}"

    prompt = f"""
{system_prompt}

Conversation so far:
{history}

Assistant:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=1000,
        temperature=0.3,
        top_p=0.9,
        top_k=40,
        repetition_penalty=1.1,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    generated_tokens = outputs[0][inputs.input_ids.shape[-1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    stop_words = ["User:", "\nUser:", "\n\nUser:"]

    for stop in stop_words:
        if stop in response:
            response = response.split(stop)[0]

    response = response.strip()

    history += f"\nAssistant: {response}"

    return response


