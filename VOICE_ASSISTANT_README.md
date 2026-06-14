# JARVIS Voice Assistant - Local, Premium Edition

## Overview
This is a local, voice-activated version of JARVIS that transforms the existing web-based backend into a premium desktop assistant with voice capabilities.

## Features
- 🎤 **Voice Activation**: Wake word detection ("Jarvis") using Porcupine (requires access key)
- 🔒 **Voice Authentication**: Only responds to authorized user's voice (optional, requires resemblyzer)
- 🎧 **Speech Recognition**: High-accuracy speech-to-text
- 🔊 **Text-to-Speech**: Natural sounding responses
- 🧠 **AI Powered**: Leverages existing agent system and Ollama LLM
- 🔐 **Security Maintained**: All existing permissions and restrictions preserved
- 💻 **Local Only**: No web deployment - runs completely on your machine

## Components

### 1. Wake Word Detection (`voice/wake_word.py`)
- Uses Porcupine for accurate, offline wake word detection
- Trained for "Jarvis" wake word
- Low CPU usage, always-listening capability
- **Requires**: Porcupine access key from Picovoice

### 2. Speech Recognition (`voice/speech_to_text.py`)
- Uses SpeechRecognition library with Google Web Speech API
- Fallback to offline recognition (Sphinx)
- Configurable timeouts and language support

### 3. Text-to-Speech (`voice/text_to_speech.py`)
- Uses pyttsx3 for offline, cross-platform TTS
- Voice selection (prefers female voices)
- Configurable rate and volume
- Non-blocking speech queue

### 4. Voice Authentication (`voice/voice_auth.py`) - Optional
- Uses Resemblyzer for speaker verification
- Creates voice print during enrollment
- Cosine similarity matching for authentication
- **Requires**: Microsoft C++ Build Tools to compile dependencies
- If not available, the assistant will still work but anyone saying "Jarvis" can activate it

### 5. Core AI (`main.py`)
- Integrates with existing agent system (`agent/`)
- Uses Ollama for LLM capabilities (`core/ollama.py`)
- Maintains all existing permissions and security
- Processes commands through intent classification and action routing

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements_voice.txt
```

### 2. Install System Dependencies
#### For Wake Word Detection (Mandatory)
- Sign up for a free access key at [Picovoice](https://picovoice.ai/account/)
- Edit the `.env` file in the project root and replace `your_access_key_here` with your actual access key:
  ```
  PORCUPINE_ACCESS_KEY=your_actual_access_key_from_picovoice
  ```

#### For Voice Authentication (Optional but Recommended for Security)
- Install Microsoft C++ Build Tools from:
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
  (Select the 'Desktop development with C++' workload)
- After installation, the `resemblyzer` package will install correctly

### 3. Ensure Ollama is Running
Make sure you have Ollama installed and running with the required models:
```bash
ollama serve
# Ensure you have the models from .env:
# qwen2.5-coder:3b-instruct-q4_K_M
# llama3.2:3b-instruct-q4_K_M
```

### 4. (Optional) Enroll Your Voice for Authentication
If you installed Microsoft C++ Build Tools and resemblyzer is available:
```bash
python enroll_voice.py
```
- Speak clearly for 5 seconds when prompted
- This creates your voice print for authentication

## Usage

### Start the Assistant
```bash
start_voice.bat
```
Or directly:
```bash
python main.py
```

### Interact with JARVIS
1. Say "Jarvis" to wake the assistant
2. Wait for the "Sí?" response
3. Speak your command or question
4. JARVIS will process and respond verbally

### Example Commands
- "Jarvis, ¿qué puedes hacer?" (See capabilities)
- "Jarvis, abre el navegador" (Open browser)
- "Jarvis, pon música de rock" (Play rock music)
- "Jarvis, explica la teoría de relatividad" (Ask a question)
- "Jarvis, sube el volumen" (Increase volume)

## Configuration

### Environment Variables (.env)
```
# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL_CODER=qwen2.5-coder:3b-instruct-q4_K_M
OLLAMA_MODEL_GENERAL=llama3.2:3b-instruct-q4_K_M

# Porcupine Access Key (GET FROM https://picovoice.ai/account/)
PORCUPINE_ACCESS_KEY=your_access_key_here

# Audio Settings (optional)
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024

# Voice Authentication
VOICE_AUTH_THRESHOLD=0.75
```

### Adjusting Sensitivity
- Wake word sensitivity: Edit `voice/wake_word.py` line 26
- Voice auth threshold: Edit `voice/voice_auth.py` line 28
- Speech recognition: Adjust timeouts in `voice/speech_to_text.py`

## Architecture

```
JARVIS Voice Assistant
├── main.py                 # Entry point
├── voice/                  # Voice processing
│   ├── wake_word.py        # Porcupine wake word detection (requires access key)
│   ├── speech_to_text.py   # Speech recognition
│   ├── text_to_speech.py   # Text-to-speech
│   └── voice_auth.py       # Voice biometrics (optional, requires resemblyzer)
├── agent/                  # Reused: Intent classification & actions
├── core/                   # Reused: Ollama client, config
├── services/               # Reused: Chat service
├── utils/                  # Utilities: system check, etc.
├── data/                   # Database and voice prints
├── requirements_voice.txt  # Dependencies
├── enroll_voice.py         # Voice enrollment script
└── start_voice.bat         # Easy startup script
```

## Security & Privacy
- All audio processing happens locally (except optional Google STT fallback)
- Voice print is stored locally and never transmitted
- No audio is recorded or stored without explicit user consent
- Existing permission system prevents dangerous actions
- Fully operable offline (except for optional STT fallback and LLM if using remote models)

## Troubleshooting

### Common Issues
1. **"Porcupine access key not found"**
   - Get a free access key from [Picovoice](https://picovoice.ai/account/)
   - Set it in the `.env` file: `PORCUPINE_ACCESS_KEY=your_key_here`

2. **"Failed to initialize Porcupine"**
   - Ensure your access key is valid and has permission to use the "jarvis" keyword

3. **Microphone not working**
   - Check permissions in Windows Settings > Privacy > Microphone
   - Try different sample rates in `enroll_voice.py`

4. **Ollama not responding**
   - Ensure Ollama is running: `ollama serve`
   - Check models are installed: `ollama list`

5. **Voice authentication not available**
   - Install Microsoft C++ Build Tools and reinstall resemblyzer
   - See enrollment script for detailed instructions

### Optional: Using JARVIS Without Voice Authentication
If you cannot install resemblyzer:
1. Ignore the voice authentication warnings
2. The assistant will still respond to voice commands
3. **Anyone saying "Jarvis" will be able to activate it** (reduced security)
4. To use this mode, simply do not run `enroll_voice.py` and the system will run with a warning

## Future Enhancements
- [ ] Local Whisper.cpp for completely offline STT
- [ ] Custom wake word training
- [ ] Noise suppression and echo cancellation
- [ ] GUI interface with visual feedback
- [ ] Multi-language support
- [ ] Offline TTS with Coqui or Tacotron
- [ ] Integration with Windows Cortana/Apple Siri for system commands

## Credits
- Built upon the existing JARVIS backend
- Porcupine by Picovoice for wake word detection
- Resemblyzer for speaker verification
- SpeechRecognition and pyttsx3 for audio processing
- Ollama for LLM capabilities

---
*JARVIS Voice Assistant - Local, Premium Edition*
*Transforming AI assistance from web to voice*
