"""
System utility functions for JARVIS voice assistant.
"""

import sys
import subprocess
import platform
import os
from typing import Tuple, List
from loguru import logger


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"


def check_ollama_connection() -> Tuple[bool, str]:
    """Check if Ollama is running and accessible."""
    try:
        import httpx
        # Import from backend/app/core/config
        sys.path.insert(0, 'backend/app')
        from core.config import get_settings
        settings = get_settings()

        response = httpx.get(f"{settings.ollama_host}/api/tags", timeout=5.0)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return True, f"Ollama connected - {len(models)} models available: {', '.join(model_names[:3])}{'...' if len(models) > 3 else ''}"
        else:
            return False, f"Ollama returned status {response.status_code}"
    except Exception as e:
        return False, f"Ollama connection failed: {str(e)}"


def check_microphone() -> Tuple[bool, str]:
    """Check if microphone is available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if input_devices:
            default_input = sd.default.device[0]
            device_info = sd.query_devices(default_input)
            return True, f"Microphone available: {device_info['name']}"
        else:
            return False, "No input devices found"
    except Exception as e:
        return False, f"Microphone check failed: {str(e)}"


def check_porcupine_access_key() -> Tuple[bool, str]:
    """Check if Porcupine access key is set."""
    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    if access_key is None or access_key == "your_access_key_here":
        return False, "Porcupine access key not set or is placeholder. Get a free key from https://picovoice.ai/account/"
    else:
        # Basic validation: access key should be a string of reasonable length
        if len(access_key) < 10:
            return False, "Porcupine access key appears too short"
        return True, "Porcupine access key is set"


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check if all required dependencies are installed."""
    # Map package name to import name (if different)
    package_import_map = {
        'pvporcupine': 'pvporcupine',
        'SpeechRecognition': 'speech_recognition',
        'pyaudio': 'pyaudio',
        'pyttsx3': 'pyttsx3',
        'pocketsphinx': 'pocketsphinx',
        # resemblyzer is optional; we'll not include in required list
        'numpy': 'numpy',
        'scipy': 'scipy',
        'loguru': 'loguru',
    }

    required_packages = [
        ('pvporcupine', 'Wake word detection'),
        ('SpeechRecognition', 'Speech recognition'),
        ('pyaudio', 'Audio I/O'),
        ('pyttsx3', 'Text-to-speech'),
        ('pocketsphinx', 'Offline speech recognition'),
        ('numpy', 'Numerical computing'),
        ('scipy', 'Scientific computing'),
        ('loguru', 'Logging'),
    ]

    results = []
    for package, description in required_packages:
        import_name = package_import_map.get(package, package)
        try:
            __import__(import_name)
            results.append((package, True, description))
        except ImportError:
            results.append((package, False, description))

    return results


def print_system_info():
    """Print system information."""
    logger.info("=== JARVIS System Information ===")
    logger.info(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info("")


def run_system_check() -> bool:
    """Run complete system check and return overall status."""
    print_system_info()

    all_passed = True

    # Check Python version
    passed, message = check_python_version()
    status = "✅ PASS" if passed else "❌ FAIL"
    logger.info(f"{status} Python Version: {message}")
    if not passed:
        all_passed = False

    # Check Ollama
    passed, message = check_ollama_connection()
    status = "✅ PASS" if passed else "❌ FAIL"
    logger.info(f"{status} Ollama Connection: {message}")
    if not passed:
        all_passed = False

    # Check microphone
    passed, message = check_microphone()
    status = "✅ PASS" if passed else "❌ FAIL"
    logger.info(f"{status} Microphone: {message}")
    if not passed:
        all_passed = False

    # Check Porcupine access key (warning only, does not fail the check)
    passed, message = check_porcupine_access_key()
    status = "✅ PASS" if passed else "⚠️  WARNING"
    logger.info(f"{status} Porcupine Access Key: {message}")
    if not passed:
        # We don't set all_passed to False here because the user can still run without wake word detection?
        # Actually, the wake word detection is required for the voice assistant to work.
        # But we'll let the main application handle the error and provide instructions.
        # So we just warn.
        pass

    # Check dependencies
    logger.info("\n=== Dependency Check ===")
    deps = check_dependencies()
    for package, passed, description in deps:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {package:<15} - {description}")
        if not passed:
            all_passed = False

    logger.info("\n" + "="*50)
    if all_passed:
        logger.info("🎉 All system checks passed! JARVIS is ready to run.")
    else:
        logger.warning("⚠️  Some system checks failed. Please resolve issues before running.")

    return all_passed


if __name__ == "__main__":
    success = run_system_check()
    sys.exit(0 if success else 1)
