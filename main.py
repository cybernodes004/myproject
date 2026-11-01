
import time
import subprocess
import requests
import speech_recognition as sr
import sounddevice as sd
import numpy as np

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

MICROPHONE = 0
SAMPLE_RATE = 16000
SPEAK_PROGRAM = "/usr/bin/say"

recognizer = sr.Recognizer()


def speak(text):
    print("\nNORA:", text, flush=True)
    subprocess.run(
        [SPEAK_PROGRAM, str(text)],
        check=False
    )


def record_audio(seconds):
    print("NORA hört zu ...", flush=True)

    recording = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=MICROPHONE
    )

    sd.wait()

    audio_bytes = np.asarray(recording).tobytes()

    return sr.AudioData(
        audio_bytes,
        SAMPLE_RATE,
        2
    )


def recognize_audio(audio):
    return recognizer.recognize_google(
        audio,
        language="de-DE"
    )


def ask_nora(command):

    system = """
    Du bist NORA, Sudems persönliche KI-Assistentin im Stil von JARVIS.

    Du bist intelligent, loyal, aufmerksam und humorvoll.
    Du sprichst natürlich und selbstbewusst.
    Du antwortest auf Deutsch, wenn Sudem Deutsch spricht.
    Du antwortest auf Türkisch, wenn Sudem Türkisch spricht.
    Englisch nur auf ausdrücklichen Wunsch.

    Du nennst deine Benutzerin Sudem.
    Du erfindest keine erledigten Aktionen.
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system
                },
                {
                    "role": "user",
                    "content": command
                }
            ],
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def main():

    print("==============================")
    print("       NORA JARVIS")
    print("       ONLINE SYSTEM")
    print("==============================")

    speak("Nora ist bereit. Ich höre.")

    while True:

        try:

            audio = record_audio(3)

            try:
                heard = recognize_audio(audio).lower()
                print("ERKANNT:", heard)

            except sr.UnknownValueError:
                continue

            except sr.RequestError as error:
                print("Spracherkennungsfehler:", error)
                time.sleep(3)
                continue

            if "nora" not in heard:
                continue

            speak("Ja, Sudem. Ich höre.")

            command_audio = record_audio(8)

            try:
                command = recognize_audio(command_audio)

            except sr.UnknownValueError:
                speak("Das habe ich nicht verstanden.")
                continue

            except sr.RequestError:
                speak("Meine Spracherkennung ist gerade nicht erreichbar.")
                continue

            print("DEIN BEFEHL:", command)

            try:
                answer = ask_nora(command)
                speak(answer)

            except requests.exceptions.ConnectionError:
                speak("Ich kann Ollama nicht erreichen.")

            except Exception as error:
                print("KI-FEHLER:", repr(error))
                speak("Bei meiner Antwort ist ein Fehler aufgetreten.")

        except KeyboardInterrupt:
            speak("Bis später, Sudem.")
            break

        except Exception as error:
            print("SYSTEMFEHLER:", repr(error))
            time.sleep(3)


if __name__ == "__main__":
    main()
