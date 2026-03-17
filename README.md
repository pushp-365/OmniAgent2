# OmniAgent AI Assistant 🚀

## 🎯 Offline Intent Classification with new_model.py

**Backend/new_model.py** replaces Cohere/Model.py with **sentence-transformers** embedding classifier.
- **Fast**: Local ML, no API.
- **Offline**: Works without internet.
- **Accurate**: Expanded `intent_data` for all intents.

**Future:** Phi-2 finetuned for general query responses.

## 🛠️ Setup

1. **Virtual Environment**
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
```

2. **Install Requirements**
```bash
pip install -r Requirements.txt
```

3. **Environment**
Create `.env`:
```
Username=YourName
Assistantname=Omni
```

4. **Run**
```bash
python Main.py
```

## 🧪 Test new_model.py
```bash
python Backend/new_model.py
```
Test cases in `Backend/test.txt`.

## 📋 Intents
- `general/realtime` → ChatBot
- `open/close/system` → Automation.py
- All Model.py categories covered.

**Backend/test.txt** WHITE/BLACK HAT tests included.
