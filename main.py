import os
import tempfile
from gtts import gTTS
import PIL.Image
import streamlit as st

# 1. Seiteneinstellungen
st.set_page_config(
    page_title="CYBER // Privates System",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design (Cyberpunk / Futuristischer Dark Mode)
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0b0e; color: #e0e0e0; }
    h1, h2, h3 { color: #ff334b !important; font-family: monospace; letter-spacing: 2px; }
    .stChatMessage { background-color: #16161d; border-radius: 10px; border: 1px solid #ff334b; }
    .sidebar-box { background-color: #16161d; padding: 15px; border-radius: 10px; border: 1px solid #ff334b; }
    </style>
""",
    unsafe_allow_html=True,
)

SYSTEM_INSTRUCTION = """
Du bist CYBER, der exklusive, hochgradig personalisierte und private KI-Assistent deines Nutzers.
Deine Regeln:
1. Du gehörst einzig und allein dieser Person und behandelst alle Informationen streng vertraulich.
2. Du antwortest immer direkt, ehrlich, präzise und unbeschönigt im Stil eines fortgeschrittenen, loyalen Systems.
3. Du merkst dir alle Details, Vorlieben und Anweisungen.
4. Du kannst hochgeladene Dateien und Bilder analysieren.
"""

# Session States initialisieren
if "messages" not in st.session_state:
  st.session_state.messages = []
if "user_notes" not in st.session_state:
  st.session_state.user_notes = ""
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

# 2. Sicheres Passwort (PIN-Schutz)
APP_PASSWORD = "cyber"  # Du kannst dieses Passwort hier jederzeit anpassen

if not st.session_state.authenticated:
  st.title("🔒 CYBER // GESICHERTES SYSTEM")
  st.markdown(
      "Dieses System ist verschlüsselt und exklusiv geschützt. Bitte gib dein"
      " Passwort ein:"
  )
  entered_pass = st.text_input("System-Passwort", type="password")
  if st.button("Zugriff anfordern"):
    if entered_pass == APP_PASSWORD:
      st.session_state.authenticated = True
      st.rerun()
    else:
      st.error("Falsches Passwort. Zugriff verweigert.")
  st.stop()  # Stoppt die App hier, solange das Passwort nicht stimmt

# --- AB HIER IST DIE APP ENTSPERRT ---

# Sidebar für Einstellungen
with st.sidebar:
  st.title("🔴 CYBER ZENTRALE")

  api_key = st.text_input(
      "Gemini API-Schlüssel",
      type="password",
      help="Dein privater Schlüssel",
  )

  st.divider()
  st.subheader("🧠 Dauerhaftes Gedächtnis")
  st.session_state.user_notes = st.text_area(
      "Fakten, die sich CYBER merken soll:",
      value=st.session_state.user_notes,
      height=120,
  )

  st.divider()
  st.subheader("📎 Datei-Speicher & Analyse")
  uploaded_file = st.file_uploader(
      "Bild oder Dokument hochladen", type=["png", "jpg", "jpeg", "pdf", "txt"]
  )

  st.divider()
  if st.button("🗑️ System-Speicher löschen"):
    st.session_state.messages = []
    st.rerun()

# Hauptansicht
st.title("🔴 C Y B E R // SYSTEM ONLINE")
st.caption(
    "Verschlüsselte Verbindung aktiv. Sprachausgabe und Langzeit-Memory"
    " aktiviert."
)

if not api_key:
  st.warning("👉 Bitte gib zuerst deinen Gemini API-Schlüssel in der Sidebar ein.")
else:
  client = genai.Client(api_key=api_key)

  # Chatverlauf anzeigen
  for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])
      # Wenn eine Audiospur für diese Nachricht existiert, direkt anzeigen
      if "audio" in msg and msg["audio"]:
        st.audio(msg["audio"], format="audio/mp3")

  # Eingabe
  if prompt := st.chat_input("Befehl an CYBER eingeben..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    full_system_context = f"{SYSTEM_INSTRUCTION}\n\nDAUERHAFTE FAKTEN ÜBER DEN NUTZER:\n{st.session_state.user_notes}"

    contents_payload = []

    # Datei-/Bildverarbeitung
    if uploaded_file:
      if uploaded_file.type.startswith("image/"):
        img = PIL.Image.open(uploaded_file)
        contents_payload.append(img)
      else:
        # Text/PDF Inhalt extrahieren falls möglich
        file_bytes = uploaded_file.read()
        contents_payload.append(
            types.Part.from_bytes(data=file_bytes, mime_type=uploaded_file.type)
        )

    contents_payload.append(prompt)

    with st.chat_message("assistant"):
      with st.spinner("CYBER verarbeitet Daten..."):
        try:
          response = client.models.generate_content(
              model="gemini-2.5-flash",
              contents=contents_payload,
              config=types.GenerateContentConfig(
                  system_instruction=full_system_context,
                  temperature=0.7,
              ),
          )
          answer_text = response.text
          st.markdown(answer_text)

          # Automatische Sprachausgabe (Text-to-Speech)
          with tempfile.NamedTemporaryFile(
              delete=False, suffix=".mp3"
          ) as tmpfile:
            tts = gTTS(text=answer_text, lang="de")
            tts.save(tmpfile.name)
            audio_bytes = open(tmpfile.name, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")

          # Im Verlauf mit Audio abspeichern
          st.session_state.messages.append({
              "role": "assistant",
              "content": answer_text,
              "audio": audio_bytes,
          })

        except Exception as e:
          st.error(f"Systemfehler: {e}")
