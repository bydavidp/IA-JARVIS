"""
Voice enrollment script for JARVIS voice assistant.
Records a voice sample to create the user's voice print.
"""

import argparse
import logging
import sys
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from loguru import logger

# Check if resemblyzer is available (required for voice enrollment)
try:
    import resemblyzer
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


def record_audio(duration: int = 5, sample_rate: int = 16000) -> np.ndarray:
    """
    Record audio from microphone.

    Args:
        duration: Recording duration in seconds
        sample_rate: Audio sample rate

    Returns:
        Audio samples as numpy array
    """
    logger.info(f"Recording {duration} seconds of audio...")
    logger.info("Please speak clearly in your normal voice")

    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float64'
    )

    # Show countdown
    for i in range(duration, 0, -1):
        print(f"\rRecording... {i} seconds remaining", end="", flush=True)
        time.sleep(1)
    print("\rRecording complete!            ")

    # Wait for recording to finish
    sd.wait()

    # Flatten to 1D array
    audio = recording.flatten()
    logger.info(f"Recorded {len(audio)} samples at {sample_rate}Hz")

    return audio


def save_wav_file(audio: np.ndarray, filename: str, sample_rate: int = 16000):
    """
    Save audio as WAV file for reference.

    Args:
        audio: Audio samples
        filename: Output filename
        sample_rate: Sample rate
    """
    # Convert to 16-bit PCM for WAV
    audio_int16 = (audio * 32767).astype(np.int16)
    write(filename, sample_rate, audio_int16)
    logger.info(f"Audio saved to {filename}")


def main():
    """Main enrollment function."""
    if not RESEMBLYZER_AVAILABLE:
        logger.error("Voice enrollment requires the 'resemblyzer' package, which failed to install.")
        logger.error("This is likely due to missing Microsoft C++ Build Tools.")
        logger.error("")
        logger.error("To fix this:")
        logger.error("1. Install Microsoft C++ Build Tools from:")
        logger.error("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        logger.error("   (Select the 'Desktop development with C++' workload)")
        logger.error("2. After installation, restart this script.")
        logger.error("")
        logger.error("Alternatively, you can use JARVIS without voice authentication:")
        logger.error("   - The assistant will still respond to voice commands,")
        logger.error("     but anyone saying 'Jarvis' will be able to activate it.")
        logger.error("   - To disable voice authentication warnings, you can ignore")
        logger.error("     the enrollment step and the system will run with reduced security.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Enroll user voice for JARVIS")
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Audio sample rate (default: 16000)"
    )
    parser.add_argument(
        "--save-wav",
        action="store_true",
        help="Save recording as WAV file for reference"
    )

    args = parser.parse_args()

    logger.info("=== JARVIS Voice Enrollment ===")
    logger.info("This script will record your voice to create a voice print.")
    logger.info("Please speak in your normal voice for the duration.")
    logger.info("")

    try:
        # Record audio
        audio = record_audio(args.duration, args.sample_rate)

        # Save WAV if requested
        if args.save_wav:
            save_wav_file(audio, "voice_enrollment.wav", args.sample_rate)

        # Enroll voice
        logger.info("Enrolling voice print...")
        from voice.voice_auth import voice_authenticator
        success = voice_authenticator.enroll_user(audio, args.sample_rate)

        if success:
            logger.info("✅ Voice enrollment successful!")
            logger.info("You can now use JARVIS Voice Assistant.")
            logger.info("Say 'Jarvis' to activate the assistant.")
        else:
            logger.error("❌ Voice enrollment failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nEnrollment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Enrollment failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
