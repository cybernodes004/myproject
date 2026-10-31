
import streamlit as st
import google.genai
import google.genai.types
import sqlite3
import hmac
import os
import platform
import subprocess
import uuid
from pathlib import Path
from datetime import datetime
from io import BytesIO
import pypdf

# =====================================
# SUDEM AI - PERSONAL AI ASSISTANT
# =====================================

st.set_page_config(
    page_title="SUDEM AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "sudem_ai.db"

# =====================================
# GEHEIME EINSTELLUNGEN
# =====================================

try:
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
    API_KEY = st.secrets["GEMINI_API_KEY"]
    MODEL = st.secrets.get(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )
except Exception:
    st.error("API-Schlüssel oder Passwort fehlen.")
    st.stop()

# =====================================
# DATENBANK
# =====================================

def database():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection

def save_memory(content):
    connection = database()
    connection.execute(
        "INSERT INTO memories (content, created) VALUES (?, ?)",
        (content, datetime.now().isoformat())
    )
    connection.commit()
    connection.close()

def get_memories():
    connection = database()
    rows = connection.execute(
        "SELECT content FROM memories ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return [row[0] for row in rows]

def save_message(chat_id, role, content):
    connection = database()
    connection.execute(
        """INSERT INTO messages
        (chat_id, role, content, created)
        VALUES (?, ?, ?, ?)""",
        (
            chat_id,
            role,
            content,
            datetime.now().isoformat()
        )
    )
    connection.commit()
    connection.close()

def get_messages(chat_id):
    connection = database()
    rows = connection.execute(
        """SELECT role, content FROM messages
        WHERE chat_id = ? ORDER BY id""",
        (chat_id,)
    ).fetchall()
    connection.close()
    return [
        {"role": row[0], "content": row[1]}
        for row in rows
    ]

database()

# =====================================
# LOGIN
# =====================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🧠 SUDEM AI")
    st.caption("PERSONAL INTELLIGENCE SYSTEM")

    password = st.text_input(
        "ACCESS PASSWORD",
        type="password"
    )

    if st.button("ACCESS SYSTEM"):
        if hmac.compare_digest(password, APP_PASSWORD):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")

    st.stop()

# =====================================
# KI VERBINDUNG
# =====================================

try:
    client = google.genai.Client(api_key=API_KEY)
except Exception:
    st.error("KI-Verbindung fehlgeschlagen.")
    st.stop()

# =====================================
# CHAT SESSION
# =====================================

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = get_messages(
        st.session_state.chat_id
    )

# =====================================
# SYSTEM STATUS
# =====================================

st.title("🧠 SUDEM AI")
st.caption("PERSONAL ARTIFICIAL INTELLIGENCE")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("AI STATUS", "ONLINE")

with col2:
    st.metric("SYSTEM", platform.system())

with col3:
    st.metric("PYTHON", platform.python_version())

with col4:
    st.metric(
        "MEMORIES",
        len(get_memories())
    )

st.divider()

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("SYSTEM CONTROL")

    if st.button("NEW CONVERSATION"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("LONG-TERM MEMORY")

    memory_input = st.text_input(
        "Save information"
    )

    if st.button("SAVE MEMORY"):
        if memory_input.strip():
            save_memory(memory_input.strip())
            st.success("Memory saved.")
            st.rerun()

    for memory in get_memories():
        st.write("🧠", memory)

    st.divider()

    st.subheader("MAC CONTROL")

    allowed_apps = [
        "Finder",
        "Safari",
        "Calendar",
        "Notes",
        "Calculator",
        "Music"
    ]

    selected_app = st.selectbox(
        "Select application",
        allowed_apps
    )

    if st.button("OPEN APPLICATION"):
        try:
            subprocess.run(
                ["open", "-a", selected_app],
                check=True,
                timeout=10
            )
            st.success(selected_app + " opened.")
        except Exception:
            st.error("Application could not be opened.")

    st.divider()

    if st.button("LOG OUT"):
        st.session_state.authenticated = False
        st.rerun()

# =====================================
# SYSTEM INSTRUCTIONS
# =====================================

system_instruction = """
You are SUDEM AI.

You are a personal artificial intelligence assistant.

Your responsibilities:
- Help with daily tasks.
- Answer questions.
- Explain difficult subjects.
- Help organize plans.
- Analyze documents and images.
- Support research and learning.
- Give clear and honest answers.
- Never pretend to have performed an action
  that you have not performed.

You speak German by default.
You are friendly, intelligent and solution-oriented.
"""

memories = get_memories()

if memories:
    system_instruction += (
        "\nPersonal memory:\n"
        + "\n".join(memories)
    )

# =====================================
# CHAT HISTORY
# =====================================

st.subheader("AI CONVERSATION")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# =====================================
# FILE UPLOAD
# =====================================

uploaded_files = st.file_uploader(
    "UPLOAD FILES",
    type=["pdf", "png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

# =====================================
# VOICE INPUT
# =====================================

st.subheader("VOICE INTERFACE")

audio = st.audio_input("Record a voice message")

# =====================================
# MESSAGE PROCESSING
# =====================================

def ask_ai(prompt, audio_file=None):

    history = get_messages(st.session_state.chat_id)

    contents = []

    for message in history:
        role = (
            "model"
            if message["role"] == "assistant"
            else "user"
        )

        contents.append(
            google.genai.types.Content(
                role=role,
                parts=[
                    google.genai.types.Part(
                        text=message["content"]
                    )
                ]
            )
        )

    current_parts = []

    if prompt:
        current_parts.append(
            google.genai.types.Part(text=prompt)
        )

    if uploaded_files:
        for file in uploaded_files:

            if file.type == "application/pdf":
                reader = pypdf.PdfReader(
                    BytesIO(file.getvalue())
                )

                pdf_text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

                current_parts.append(
                    google.genai.types.Part(
                        text="PDF CONTENT:\n" + pdf_text
                    )
                )

            else:
                current_parts.append(
                    google.genai.types.Part.from_bytes(
                        data=file.getvalue(),
                        mime_type=file.type
                    )
                )

    if audio_file is not None:
        current_parts.append(
            google.genai.types.Part.from_bytes(
                data=audio_file.getvalue(),
                mime_type=audio_file.type
            )
        )

    contents.append(
        google.genai.types.Content(
            role="user",
            parts=current_parts
        )
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=google.genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )
    )

    return response.text or "No response generated."

# =====================================
# TEXT CHAT
# =====================================

prompt = st.chat_input("Talk to Sudem AI...")

if prompt:

    save_message(
        st.session_state.chat_id,
        "user",
        prompt
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Sudem AI is thinking..."):

            try:
                answer = ask_ai(prompt)

                st.write(answer)

                save_message(
                    st.session_state.chat_id,
                    "assistant",
                    answer
                )

            except Exception as error:
                st.error("AI ERROR")
                st.write(str(error))

    st.session_state.messages = get_messages(
        st.session_state.chat_id
    )

# =====================================
# VOICE CHAT
# =====================================

if audio is not None:

    if st.button("ANALYZE VOICE MESSAGE"):

        with st.spinner("Analyzing audio..."):

            try:
                answer = ask_ai(
                    "Listen to this audio and respond to the spoken message.",
                    audio
                )

                st.subheader("SUDEM AI RESPONSE")
                st.write(answer)

                save_message(
                    st.session_state.chat_id,
                    "user",
                    "[Voice message]"
                )

                save_message(
                    st.session_state.chat_id,
                    "assistant",
                    answer
                )

                st.session_state.messages = get_messages(
                    st.session_state.chat_id
                )

            except Exception as error:
                st.error("VOICE ERROR")
                st.write(str(error))

# =====================================
# FOOTER
# =====================================

st.divider()
st.caption(
    "SUDEM AI | PERSONAL INTELLIGENCE SYSTEM | "
    + datetime.now().strftime("%d.%m.%Y %H:%M")
)
