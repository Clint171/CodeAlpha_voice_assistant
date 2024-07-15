import speech_recognition as sr
import pyaudio
import wave
import os

# Dictionary mapping voice commands to shell commands
commands = {
    "list files": "ls",
    "show directory": "pwd",
    "who am I": "whoami",
    "shutdown": "shutdown now",
    "reboot": "reboot"
}

def record_audio(filename="audio.wav", duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

def recognize_speech_from_audio_file(recognizer, filename):
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)

def main():
    recognizer = sr.Recognizer()

    while True:
        print("\nSay a command...")
        audio_file = record_audio()
        try:
            command = recognize_speech_from_audio_file(recognizer, audio_file)
            print(f"You said: {command}")
            action = commands.get(command.lower())
            if action:
                print(f"Executing: {action}")
                os.system(action)
            else:
                print("Command not recognized.")
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"ERROR: {e}")

        print("Do you want to continue? (yes/no)")
        audio_file = record_audio()
        try:
            continue_command = recognize_speech_from_audio_file(recognizer, audio_file)
            if continue_command.lower() == "no":
                break
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
