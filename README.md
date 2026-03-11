# OmniAgent - AI Voice Assistant 🤖

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**A sophisticated voice-controlled AI assistant with real-time search, automation, and natural language processing capabilities.**

</div>

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Requirements](#-api-requirements)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Capabilities

- **🎤 Voice Recognition** - Advanced speech-to-text using Web Speech API with Selenium
- **🔊 Text-to-Speech** - Natural voice synthesis using Microsoft Edge TTS
- **💬 Intelligent Chatbot** - Powered by Groq's LLaMA 3 70B model
- **🔍 Real-time Web Search** - Live internet search integration with Google
- **🤖 Task Automation** - Open/close applications, control system settings
- **🎨 Image Generation** - AI-powered image creation using Pollinations API
- **🖥️ Modern GUI** - Beautiful PyQt5 interface with voice and text input
- **🌐 Multi-language Support** - Automatic translation for non-English input

### Automation Features

- **Application Control** - Open and close applications by voice command
- **System Commands** - Control volume, brightness, mute/unmute
- **Web Actions** - Google search, YouTube search and playback
- **Content Generation** - Write letters, essays, code, and more

## 🎥 Demo

The assistant provides a sleek, modern interface with:
- Real-time voice visualization
- Animated status indicators
- Chat history view
- Voice and text input modes
- Custom frameless window design

## 🔧 Prerequisites

Before installing OmniAgent, ensure you have:

- **Python 3.8 or higher** installed
- **Windows OS** (currently optimized for Windows)
- **Google Chrome** browser (for speech recognition)
- **Active internet connection** (for API calls)
- **Microphone** (for voice input)
- **Speakers/Headphones** (for voice output)

## 📥 Installation

### Step 1: Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd OmniAgent

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On Linux/Mac:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r Requirements.txt
```

**Note:** Some packages like `torch` may take time to download due to large size.

### Step 4: Verify Installation

```bash
python -c "import PyQt5; import groq; import cohere; print('Dependencies installed successfully!')"
```

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create or edit the `.env` file in the project root directory:

```env
# User Configuration
Username=YourName
Assistantname=Jarvis

# Language Settings
InputLanguage=en
AssistantVoice=en-CA-LiamNeural

# API Keys (Required)
GroqAPIKey=your_groq_api_key_here
CohereAPIKey=your_cohere_api_key_here

# Optional API Keys
HuggingFaceAPIKey=your_hf_key_here
OCR_SPACE_KEY=your_ocr_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 2. Available Voice Options

Change `AssistantVoice` to any of these options:

**English:**
- `en-US-GuyNeural` (Male, US)
- `en-US-JennyNeural` (Female, US)
- `en-CA-LiamNeural` (Male, Canadian)
- `en-GB-RyanNeural` (Male, British)
- `en-AU-WilliamNeural` (Male, Australian)

**Other Languages:**
- `hi-IN-MadhurNeural` (Hindi)
- `es-ES-AlvaroNeural` (Spanish)
- `fr-FR-HenriNeural` (French)

[Full list available here](https://speech.microsoft.com/portal/voicegallery)

### 3. Language Support

Set `InputLanguage` to:
- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- Any language code supported by Web Speech API

## 🚀 Usage

### Starting the Assistant

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Run the main application
python Main.py
```

### Using Voice Input

1. **Click the microphone icon** to activate voice listening
2. **Speak your command** clearly
3. **Wait for response** - The assistant will process and respond
4. **Click mic icon again** to stop listening

### Using Text Input

1. **Type your query** in the text input box at the bottom
2. **Press Enter** or click the **Send** button
3. **View response** in the chat window

### Example Commands

**General Chat:**
```
"Hello, how are you?"
"Tell me a joke"
"What can you do?"
```

**Real-time Information:**
```
"What's the weather today?"
"Latest news about technology"
"Current Bitcoin price"
```

**Automation:**
```
"Open Chrome"
"Close Notepad"
"Increase volume"
"Mute system"
"Search Google for Python tutorials"
"Play music on YouTube"
```

**Content Creation:**
```
"Write a letter to my teacher"
"Generate code for a calculator in Python"
"Create an essay about climate change"
```

**Image Generation:**
```
"Generate image of a sunset over mountains"
"Create picture of a futuristic city"
```

## 🏗️ Architecture

### Project Structure

```
OmniAgent/
├── Main.py                 # Application entry point
├── Backend/                # Core logic and AI modules
│   ├── Model.py           # Decision-making model (Cohere)
│   ├── ChatBot.py         # Conversational AI (Groq)
│   ├── SpeechToText.py    # Voice recognition
│   ├── TextToSpeech.py    # Voice synthesis
│   ├── RealTimeSearchEngine.py  # Web search
│   ├── Automation.py      # Task automation
│   ├── ImageGeneration.py # AI image creation
│   └── ...
├── Frontend/               # GUI components
│   ├── GUI_1.PY          # Main interface
│   ├── Graphics/         # UI assets
│   └── Files/            # Temporary data
├── Data/                  # Runtime data
│   ├── ChatLog.json      # Conversation history
│   ├── speech.mp3        # Generated speech
│   └── ...
├── .env                   # Configuration
└── Requirements.txt       # Dependencies
```

### System Flow

```
User Input (Voice/Text)
    ↓
Speech Recognition / Text Input
    ↓
Decision Model (Cohere) - Classifies intent
    ↓
Router - Directs to appropriate handler
    ├→ ChatBot (General queries)
    ├→ Real-Time Search (Current info)
    ├→ Automation (System commands)
    └→ Image Generation (Create images)
    ↓
Response Processing
    ↓
Text-to-Speech + GUI Display
    ↓
User sees & hears response
```

## 🔑 API Requirements

### Required APIs

1. **Groq API** (Required)
   - Used for: Main chat functionality
   - Get key: [groq.com](https://console.groq.com)
   - Free tier: Available

2. **Cohere API** (Required)
   - Used for: Intent classification
   - Get key: [cohere.com](https://cohere.com)
   - Free tier: Available

### Optional APIs

3. **HuggingFace** (Optional)
   - Used for: Advanced ML features
   - Get key: [huggingface.co](https://huggingface.co)

4. **OCR Space** (Optional)
   - Used for: Image-to-text conversion
   - Get key: [ocr.space](https://ocr.space/ocrapi)

5. **Gemini** (Optional)
   - Used for: Alternative AI model
   - Get key: [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🐛 Troubleshooting

### Common Issues

#### 1. Dependencies Installation Fails

**Problem:** Error installing packages

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages one by one
pip install python-dotenv
pip install groq
# etc...
```

#### 2. Speech Recognition Not Working

**Problem:** Microphone not detecting voice

**Solutions:**
- Ensure microphone is enabled in system settings
- Grant browser microphone permissions
- Check `InputLanguage` in `.env` matches your speech language
- Try restarting the application

#### 3. Text-to-Speech Errors

**Problem:** No voice output or pygame errors

**Solutions:**
```bash
# Reinstall pygame and edge-tts
pip uninstall pygame edge-tts
pip install pygame edge-tts
```

#### 4. GUI Not Displaying

**Problem:** PyQt5 errors or blank window

**Solutions:**
```bash
# Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5

# On some systems, you may need:
pip install PyQt5-Qt5
```

#### 5. Google Search Not Working

**Problem:** `googlesearch-python` errors

**Solution:**
```bash
# If googlesearch-python is broken, replace it
pip uninstall googlesearch-python
pip install googlesearch-python
# Or use an alternative:
pip install duckduckgo-search
```

Then update `Backend/RealTimeSearchEngine.py` accordingly.

#### 6. API Key Errors

**Problem:** "Invalid API key" or authentication errors

**Solutions:**
- Verify API keys in `.env` file are correct
- Check for extra spaces or quotes around keys
- Ensure API keys are active and not expired
- Check API usage limits haven't been exceeded

#### 7. Virtual Environment Issues

**Problem:** Commands not finding packages

**Solution:**
```bash
# Make sure venv is activated (you should see (.venv) in prompt)
.venv\Scripts\activate

# If still issues, recreate venv:
deactivate
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r Requirements.txt
```

### Getting Help

If you encounter issues not covered here:
1. Check the console output for error messages
2. Verify all API keys are valid
3. Ensure all dependencies are installed
4. Try running individual modules to isolate the problem

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs** - Open an issue describing the problem
2. **Suggest Features** - Share ideas for improvements
3. **Submit Pull Requests** - Fix bugs or add features
4. **Improve Documentation** - Help make docs clearer

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] Linux and macOS support
- [ ] Multi-language UI
- [ ] Plugin system for custom commands
- [ ] Mobile app companion
- [ ] Calendar and reminder integration
- [ ] Email integration
- [ ] Smart home device control

## 👨‍💻 Author

**Pushp Sharma**

## 🙏 Acknowledgments

- **Groq** - For the powerful LLaMA API
- **Cohere** - For intent classification
- **Microsoft Edge TTS** - For natural voice synthesis
- **Pollinations AI** - For image generation
- **PyQt5** - For the GUI framework

---

<div align="center">

**Made with ❤️ using Python**

If you found this project helpful, please consider giving it a ⭐!

</div>
