"""
Wake word detection for JARVIS voice assistant.
Uses Porcupine for accurate, offline wake word detection.
"""

import struct
import os
import pvporcupine
import pyaudio
import threading
import time
from typing import Optional, Callable
from loguru import logger


class WakeWordDetector:
    """Detects wake word 'Jarvis' using Porcupine."""

    def __init__(self, sensitivity: float = 0.7):
        """
        Initialize wake word detector.

        Args:
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        self.sensitivity = sensitivity
        self.porcupine = None
        self.audio_stream = None
        self.is_listening = False
        self.detection_callback: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None

        # Get access key from environment
        access_key = os.getenv("PORCUPINE_ACCESS_KEY")
        if access_key is None:
            logger.error(
                "Porcupine access key not found. Set the PORCUPINE_ACCESS_KEY environment variable. "
                "Get a free access key from https://picovoice.ai/account/"
            )
            raise ValueError("Porcupine access key required for wake word detection")

        # Initialize Porcupine
        try:
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=["jarvis"],
                sensitivities=[sensitivity]
            )
            logger.info("Wake word detector initialized for 'Jarvis'")
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            raise

    def start_listening(self, callback: Callable):
        """
        Start listening for wake word in background thread.

        Args:
            callback: Function to call when wake word is detected
        """
        if self.is_listening:
            logger.warning("Wake word detection already listening")
            return

        self.detection_callback = callback
        self.is_listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("Started wake word detection")

    def stop_listening(self):
        """Stop listening for wake word."""
        self.is_listening = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Stopped wake word detection")

    def _listen_loop(self):
        """Main listening loop running in background thread."""
        try:
            # Initialize audio stream
            self.audio_stream = pyaudio.PyAudio().open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            logger.info(f"Audio stream started: {self.porcupine.sample_rate}Hz")

            while self.is_listening:
                try:
                    # Read audio frame
                    pcm = self.audio_stream.read(
                        self.porcupine.frame_length,
                        exception_on_overflow=False
                    )
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                    # Process with Porcupine
                    result = self.porcupine.process(pcm)

                    if result >= 0:  # Wake word detected
                        logger.info("Wake word 'Jarvis' detected!")
                        if self.detection_callback:
                            self.detection_callback()

                        # Small delay to prevent multiple detections
                        time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error in wake word detection loop: {e}")
                    time.sleep(0.1)

        except Exception as e:
            logger.error(f"Failed to initialize audio stream: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up audio resources."""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

        if hasattr(self, '_pa') and self._pa:
            self._pa.terminate()

    def __del__(self):
        """Cleanup on deletion."""
        self.stop_listening()
        if self.porcupine:
            self.porcupine.delete()
