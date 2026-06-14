"""
Text-to-speech conversion for JARVIS voice assistant.
Uses pyttsx3 for offline, cross-platform TTS.
"""

import pyttsx3
import threading
import queue
import logging
from typing import Optional
from loguru import logger


class TextToSpeech:
    """Converts text to speech using pyttsx3."""

    def __init__(self, rate: int = 180, volume: float = 0.9):
        """
        Initialize text-to-speech engine.

        Args:
            rate: Words per minute
            volume: Volume level (0.0 to 1.0)
        """
        self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = volume
        self._queue = queue.Queue()
        self._is_speaking = False
        self._speak_thread: Optional[threading.Thread] = None

        # Configure engine
        self._configure_engine()
        logger.info("Text-to-speech initialized")

    def _configure_engine(self):
        """Configure pyttsx3 engine properties."""
        # Set rate
        self.engine.setProperty('rate', self.rate)

        # Set volume
        self.engine.setProperty('volume', self.volume)

        # Try to set a nice voice (prefer female voices for assistant)
        voices = self.engine.getProperty('voices')
        if voices:
            # Prefer female voice if available
            female_voices = [v for v in voices if 'female' in v.name.lower() or 'zira' in v.name.lower() or 'hazel' in v.name.lower()]
            if female_voices:
                self.engine.setProperty('voice', female_voices[0].id)
                logger.info(f"Using female voice: {female_voices[0].name}")
            else:
                # Use first available voice
                self.engine.setProperty('voice', voices[0].id)
                logger.info(f"Using voice: {voices[0].name}")

    def speak(self, text: str, block: bool = False):
        """
        Speak the given text.

        Args:
            text: Text to speak
            block: If True, wait for speech to complete before returning
        """
        if not text.strip():
            return

        self._queue.put(text)
        if not self._is_speaking:
            self._start_speech_thread()

        if block:
            self._queue.join()  # Wait for queue to be empty

    def _start_speech_thread(self):
        """Start the background speech thread."""
        if self._speak_thread and self._speak_thread.is_alive():
            return

        self._is_speaking = True
        self._speak_thread = threading.Thread(target=self._speak_worker, daemon=True)
        self._speak_thread.start()

    def _speak_worker(self):
        """Worker thread that processes the speech queue."""
        while self._is_speaking or not self._queue.empty():
            try:
                # Get text from queue with timeout
                text = self._queue.get(timeout=0.5)
                logger.info(f"Speaking: {text[:50]}...")

                self.engine.say(text)
                self.engine.runAndWait()

                self._queue.task_done()

            except queue.Empty:
                # No more text to speak
                continue
            except Exception as e:
                logger.error(f"Error in speech synthesis: {e}")
                self._queue.task_done()

        self._is_speaking = False

    def stop(self):
        """Stop speech and clear queue."""
        self._is_speaking = False
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

        # Stop current speech
        self.engine.stop()

    def set_voice(self, voice_index: int):
        """
        Set voice by index.

        Args:
            voice_index: Index of voice to use
        """
        voices = self.engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            logger.info(f"Voice set to: {voices[voice_index].name}")
        else:
            logger.warning(f"Invalid voice index: {voice_index}")

    def set_rate(self, rate: int):
        """
        Set speech rate.

        Args:
            rate: Words per minute
        """
        self.rate = rate
        self.engine.setProperty('rate', rate)
        logger.info(f"Speech rate set to: {rate} wpm")

    def set_volume(self, volume: float):
        """
        Set volume level.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', self.volume)
        logger.info(f"Volume set to: {self.volume}")

    def __del__(self):
        """Cleanup on deletion."""
        self.stop()