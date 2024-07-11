import speech_recognition as sr
import sounddevice as sd
import numpy as np
import os

# Dictionary mapping voice commands to shell commands
commands = {
    "list files": "ls",
    "show directory": "pwd",
    "who am I": "whoami",
    "shutdown": "shutdown now",
    "reboot": "reboot"
}

def record_audio(duration=5):
    fs = 44100  # Sample rate
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return myrecording

def recognize_speech_from_mic(recognizer, audio_data):
    """Transcribe speech from recorded audio data."""
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio_data)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def main():
    recognizer = sr.Recognizer()

    while True:
        print("\nSay a command...")
        audio_data = record_audio()
        try:
            command = recognize_speech_from_mic(recognizer, audio_data)
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        if command["transcription"]:
            print(f"You said: {command['transcription']}")
            action = commands.get(command["transcription"].lower())
            if action:
                print(f"Executing: {action}")
                os.system(action)
            else:
                print("Command not recognized.")
        elif command["error"]:
            print(f"ERROR: {command['error']}")

        print("Do you want to continue? (yes/no)")
        continue_command = recognize_speech_from_mic(recognizer, record_audio())

        if continue_command["transcription"].lower() == "no":
            break

if __name__ == "__main__":
    main()
