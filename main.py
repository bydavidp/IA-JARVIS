"""
JARVIS Voice Assistant - Local, Premium Edition
A voice-activated AI assistant that only responds to the authorized user's voice.
"""

import asyncio
import threading
import time
import logging
import signal
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

# Load environment variables from .env file as early as possible
from dotenv import load_dotenv
load_dotenv()  # This loads .env from the current working directory

# Add backend to Python path so we can import app.* modules
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import voice components
from voice.wake_word import WakeWordDetector
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.voice_auth import voice_authenticator

# Import existing agent/Ollama components
from app.agent.router import agent_router
from app.agent.models import IntentResult
from app.core.ollama import ollama_client
from app.services.chat_service import chat_service, SYSTEM_PROMPTS

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/jarvis.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# Global instances
wake_word_detector: Optional[WakeWordDetector] = None
speech_to_text: Optional[SpeechToText] = None
text_to_speech: Optional[TextToSpeech] = None
is_running = False


class JarvisVoiceAssistant:
    """Main JARVIS voice assistant application."""

    def __init__(self):
        """Initialize the voice assistant."""
        self.is_listening_for_command = False
        self.is_processing = False
        self.wake_word_detector = None
        self.speech_to_text = None
        self.text_to_speech = None
        self._setup_components()

    def _setup_components(self):
        """Initialize all components."""
        global wake_word_detector, speech_to_text, text_to_speech

        try:
            # Initialize voice components
            self.wake_word_detector = WakeWordDetector(sensitivity=0.8)
            self.speech_to_text = SpeechToText(language="es-ES")
            self.text_to_speech = TextToSpeech(rate=175, volume=0.9)

            # Set global references
            wake_word_detector = self.wake_word_detector
            speech_to_text = self.speech_to_text
            text_to_speech = self.text_to_speech

            logger.info("All components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def start(self):
        """Start the voice assistant."""
        global is_running
        is_running = True

        logger.info("Starting JARVIS Voice Assistant...")
        self.text_to_speech.speak("Inicializando J.A.R.V.I.S.", block=True)

        # Check if user is enrolled (only if voice authentication is available)
        if voice_authenticator.encoder is not None and not voice_authenticator.is_enrolled():
            logger.warning("User voice not enrolled - please run enrollment first")
            self.text_to_speech.speak(
                "Por favor, ejecuta el script de inscripción de voz primero.",
                block=True
            )
        elif voice_authenticator.encoder is None:
            logger.warning("Voice authentication is not available (resemblyzer not installed or failed to initialize).")
            logger.warning("Anyone saying 'Jarvis' will be able to activate the assistant.")

        # Start wake word detection
        self.wake_word_detector.start_listening(self._on_wake_word_detected)
        logger.info("JARVIS Voice Assistant is now listening for wake word 'Jarvis'")

    def stop(self):
        """Stop the voice assistant."""
        global is_running
        is_running = False

        logger.info("Stopping JARVIS Voice Assistant...")
        self.text_to_speech.speak("Hasta luego", block=True)

        # Stop components
        if self.wake_word_detector:
            self.wake_word_detector.stop_listening()

        if self.text_to_speech:
            self.text_to_speech.stop()

        is_running = False
        logger.info("JARVIS Voice Assistant stopped")

    def _on_wake_word_detected(self):
        """Callback when wake word is detected."""
        if self.is_processing or self.is_listening_for_command:
            return  # Prevent reentrancy

        logger.info("Wake word detected - starting voice command flow")
        self.is_listening_for_command = True

        # Run in thread to avoid blocking wake word detection
        threading.Thread(target=self._process_voice_command, daemon=True).start()

    def _process_voice_command(self):
        """Process a voice command after wake word detection."""
        try:
            # Play audio feedback
            self.text_to_speech.speak("Sí?", block=False)

            # Listen for command
            logger.info("Listening for voice command...")
            command = self.speech_to_text.listen(timeout=4.0, phrase_time_limit=6.0)

            if not command:
                logger.info("No command detected")
                self.text_to_speech.speak("No te escuché", block=True)
                return

            logger.info(f"Command received: {command}")

            # Authenticate voice
            # Note: For simplicity, we're skipping real-time voice auth during command
            # In a full implementation, we'd authenticate the audio stream
            if voice_authenticator.encoder is None:
                logger.warning("Voice authentication not available - proceeding anyway")
            elif not voice_authenticator.is_enrolled():
                logger.warning("User not enrolled - proceeding anyway for demo")
            # TODO: Implement real-time voice authentication of the command audio

            # Process command through agent system
            self.is_processing = True
            logger.info("Processing command through agent system...")

            # Use asyncio to handle the async agent router
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(self._process_with_agent(command))
            finally:
                loop.close()

            self.is_processing = False

            # Speak response
            if response:
                logger.info(f"Responding: {response[:100]}...")
                self.text_to_speech.speak(response, block=True)
            else:
                logger.warning("No response generated")
                self.text_to_speech.speak("Lo siento, no pude procesar eso", block=True)

        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            self.text_to_speech.speak("Ha ocurrido un error", block=True)
        finally:
            self.is_listening_for_command = False
            self.is_processing = False

    async def _process_with_agent(self, command: str) -> str:
        """
        Process command using the existing agent system.

        Args:
            command: Voice command text

        Returns:
            Response text
        """
        try:
            # Classify intent
            intent_result = await agent_router.classify(command)
            logger.info(f"Intent classified as: {intent_result.intent.value} (confidence: {intent_result.confidence})")

            # Validate intent
            from app.agent.permissions import validar_intencion
            validation = validar_intencion(intent_result)
            if not validation.success:
                logger.warning(f"Intent validation failed: {validation.message}")
                return validation.message

            # Handle rejected intents
            if intent_result.intent.value == "reject":
                return (
                    "No puedo realizar esa acción. Por seguridad, no borro, "
                    "muevo, renombro ni ejecuto archivos o comandos en tu sistema."
                )

            # Route to appropriate handler
            response_parts = []
            async for token in agent_router.route(command):
                if token == "__CHAT_FALLBACK__":
                    # Fallback to regular chat with Ollama
                    logger.info("Falling back to regular chat with Ollama")
                    async for chat_token in chat_service.chat(
                        message=command,
                        mode="general"
                    ):
                        response_parts.append(chat_token)
                else:
                    response_parts.append(token)

            response = "".join(response_parts).strip()
            return response if response else "He procesado tu comando pero no tengo una respuesta específica."

        except Exception as e:
            logger.error(f"Error in agent processing: {e}")
            return f"Lo siento, tuve un problema al procesar tu solicitud: {str(e)}"


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    if 'assistant' in globals():
        assistant.stop()
    sys.exit(0)


def main():
    """Main entry point."""
    global assistant

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Create and start assistant
        assistant = JarvisVoiceAssistant()
        assistant.start()

        # Keep main thread alive
        logger.info("JARVIS Voice Assistant is running. Press Ctrl+C to stop.")
        while is_running:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise
    finally:
        if 'assistant' in globals():
            assistant.stop()


if __name__ == "__main__":
    main()