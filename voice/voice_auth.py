"""
Voice authentication for JARVIS voice assistant.
Verifies that the speaker is the authorized user.
"""

import numpy as np
import logging
import os
import pickle
from typing import Optional, Tuple
from loguru import logger

try:
    import resemblyzer
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    logger.warning("Resemblyzer not available - voice authentication disabled")


class VoiceAuthenticator:
    """Authenticates user by voice using speaker embeddings."""

    def __init__(self, voice_print_path: str = "data/voice_print.pkl"):
        """
        Initialize voice authenticator.

        Args:
            voice_print_path: Path to stored voice print
        """
        self.voice_print_path = voice_print_path
        self.voice_print = None
        self.threshold = 0.75  # Cosine similarity threshold
        self.encoder = None

        # Initialize encoder if available
        if RESEMBLYZER_AVAILABLE:
            try:
                self.encoder = VoiceEncoder()
                logger.info("Voice encoder initialized")
            except Exception as e:
                logger.error(f"Failed to initialize voice encoder: {e}")
                self.encoder = None

        # Load existing voice print
        self._load_voice_print()

    def _load_voice_print(self):
        """Load voice print from file."""
        if os.path.exists(self.voice_print_path):
            try:
                with open(self.voice_print_path, 'rb') as f:
                    self.voice_print = pickle.load(f)
                logger.info("Voice print loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load voice print: {e}")
                self.voice_print = None
        else:
            logger.info("No existing voice print found - enrollment required")

    def enroll_user(self, audio_sample: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        Enroll a new user voice print.

        Args:
            audio_sample: Audio samples as numpy array
            sample_rate: Sample rate of audio

        Returns:
            True if enrollment successful
        """
        if not RESEMBLYZER_AVAILABLE or not self.encoder:
            logger.error("Voice encoder not available for enrollment")
            return False

        try:
            # Preprocess audio
            wav = preprocess_wav(audio_sample, source_sr=sample_rate)

            # Generate embedding
            embedding = self.encoder.embed_utterance(wav)

            # Save voice print
            os.makedirs(os.path.dirname(self.voice_print_path), exist_ok=True)
            with open(self.voice_print_path, 'wb') as f:
                pickle.dump(embedding, f)

            self.voice_print = embedding
            logger.info("User voice print enrolled successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to enroll user: {e}")
            return False

    def authenticate(self, audio_sample: np.ndarray, sample_rate: int = 16000) -> Tuple[bool, float]:
        """
        Authenticate if audio sample matches enrolled user.

        Args:
            audio_sample: Audio samples as numpy array
            sample_rate: Sample rate of audio

        Returns:
            Tuple of (is_authenticated, confidence_score)
        """
        if not RESEMBLYZER_AVAILABLE or not self.encoder:
            logger.warning("Voice encoder not available - disabling authentication")
            return True, 1.0  # Allow all if not available

        if self.voice_print is None:
            logger.warning("No voice print enrolled - allowing access (first use)")
            return True, 1.0  # Allow first use

        try:
            # Preprocess audio
            wav = preprocess_wav(audio_sample, source_sr=sample_rate)

            # Generate embedding
            embedding = self.encoder.embed_utterance(wav)

            # Calculate cosine similarity
            similarity = np.dot(embedding, self.voice_print) / (
                np.linalg.norm(embedding) * np.linalg.norm(self.voice_print)
            )

            is_authenticated = similarity >= self.threshold
            logger.info(f"Voice authentication: {similarity:.3f} (threshold: {self.threshold}) - {'PASS' if is_authenticated else 'FAIL'}")

            return is_authenticated, float(similarity)

        except Exception as e:
            logger.error(f"Error during voice authentication: {e}")
            return False, 0.0

    def is_enrolled(self) -> bool:
        """Check if user voice print is enrolled."""
        return self.voice_print is not None

    def set_threshold(self, threshold: float):
        """
        Set authentication threshold.

        Args:
            threshold: Cosine similarity threshold (0.0 to 1.0)
        """
        self.threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Voice authentication threshold set to: {self.threshold}")


# Global instance
voice_authenticator = VoiceAuthenticator()