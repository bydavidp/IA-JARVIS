"""
Speech-to-text conversion for JARVIS voice assistant.
Uses SpeechRecognition library with multiple backends.
"""

import speech_recognition as sr
import logging
import io
import wave
import numpy as np
from typing import Optional
from loguru import logger


class SpeechToText:
    """Converts speech to text using various backends."""

    def __init__(self, language: str = "es-ES"):
        """
        Initialize speech-to-text converter.

        Args:
            language: Language code for recognition (es-ES for Spanish)
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        logger.info("Adjusting for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Speech-to-text initialized")

    def listen(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """
        Listen for speech and convert to text.
        Uses offline recognition (Sphinx) by default to avoid API charges.

        Args:
            timeout: Seconds to wait for speech start
            phrase_time_limit: Max seconds for phrase

        Returns:
            Recognized text or None if failed
        """
        try:
            logger.info("Listening for speech...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            logger.info("Processing speech with offline recognition...")
            # Try offline recognition first (Sphinx) to avoid API charges
            text = self._recognize_offline(audio)
            if text:
                logger.info(f"Recognized (offline): {text}")
                return text

            # If offline fails, we could optionally try online as fallback
            # But per user request to avoid APIs that might charge, we'll skip online fallback
            logger.warning("Offline recognition failed - no online fallback to avoid potential charges")
            return None

        except sr.WaitTimeoutError:
            logger.info("Listening timeout - no speech detected")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return None

    def _recognize_offline(self, audio) -> Optional[str]:
        """
        Attempt offline recognition using available backends.
        """
        try:
            # Try Sphinx (offline, but less accurate)
            text = self.recognizer.recognize_sphinx(audio, language=self.language)
            logger.info(f"Offline recognition: {text}")
            return text
        except Exception as e:
            logger.debug(f"Offline recognition failed: {e}")
            return None

    def listen_with_wake_word(self, wake_word_detected_callback) -> Optional[str]:
        """
        Listen for speech specifically after wake word detection.
        This assumes wake word has already been detected and we're ready for command.

        Args:
            wake_word_detected_callback: Called when we start listening

        Returns:
            Recognized text or None
        """
        if wake_word_detected_callback:
            wake_word_detected_callback()

        return self.listen(timeout=3.0, phrase_time_limit=8.0)