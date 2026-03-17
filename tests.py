from sentence_transformers import SentenceTransformer
import os

# where you want to store it
save_path = "models/all-MiniLM-L6-v2"

# create folder if not exists
os.makedirs(save_path, exist_ok=True)

# download model (from HF)
model = SentenceTransformer('all-MiniLM-L6-v2')

# save locally
model.save(save_path)

print(f"Model downloaded and saved to: {save_path}")