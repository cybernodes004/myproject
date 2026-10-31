


# =====================================
# SUDEM AI - PRIVATE PERSONAL ASSISTANT
# =====================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MY_PASSWORD = os.getenv("MY_PASSWORD", "Ananas")
DB = "sudem_memory.db"

st.set_page_config(
    page_title="Sudem AI",
    page_icon="🧠",
    layout="wide"
)

# =====================================
# DESIGN
# =====================================

st.markdown("""
<style>
.stApp {
    background-color: #101114;
    color: white;
}
h1 {
    color: #70D9FF;
}
[data-testid="stChatMessage"] {
    background-color: #191c22;
    border-radius: 15px;
    padding: 12px;
}
section[data-testid="stSidebar"] {
    background-color: #17191f;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# DATABASE
# =====================================

def init_database():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)

def save_message(role, content):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content)
        )

def get_messages():
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT role, content FROM messages ORDER BY id"
        ).fetchall()

def get_memories():
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT id, content FROM memories"
        ).fetchall()

def save_memory(content):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO memories (content) VALUES (?)",
            (content,)
        )

init_database()

# =====================================
# PRIVATE LOGIN
# =====================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🧠 SUDEM AI")
    st.subheader("Dein persönlicher KI-Assistent")

    st.write("Willkommen! Bitte melde dich an.")

    with st.form("private_login"):
        password = st.text_input(
            "Dein Passwort",
            type="password"
        )

        submitted = st.form_submit_button("Einloggen")

        if submitted:
            if hmac.compare_digest(password, MY_PASSWORD):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")

    st.stop()

# =====================================
# API CONNECTION
# =====================================

if not API_KEY:
    st.error("GEMINI_API_KEY fehlt in deiner .env Datei.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# =====================================
# PERSONALITY
# =====================================

SYSTEM_INSTRUCTION = """
Du bist SUDEM AI.

Du bist ein privater, persönlicher
und intelligenter KI-Assistent.

Deine Aufgaben:
- Fragen beantworten
- Informationen recherchieren, wenn
  entsprechende Werkzeuge verfügbar sind
- Probleme lösen
- Dokumente analysieren
- Bilder verstehen
- Texte schreiben
- Aufgaben planen
- Informationen organisieren
- Ideen entwickeln

Du sprichst Deutsch, Türkisch und Englisch.

Du bist freundlich, intelligent,
hilfsbereit und diskret.

Du darfst niemals behaupten,
dass du eine Aufgabe erledigt hast,
wenn du sie nicht tatsächlich erledigt hast.

Frage vor wichtigen externen Aktionen
immer nach Zustimmung.
"""

# =====================================
# HEADER
# =====================================

st.title("🧠 SUDEM AI")
st.caption("Your private personal AI assistant")

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("⚙️ Einstellungen")

    st.success("Privater Zugang aktiviert")

    st.divider()

    st.subheader("🧠 Mein Gedächtnis")

    memories = get_memories()

    for memory_id, memory in memories:
        col1, col2 = st.columns([4, 1])

        col1.write(memory)

        if col2.button("✖", key=f"delete_{memory_id}"):
            with sqlite3.connect(DB) as con:
                con.execute(
                    "DELETE FROM memories WHERE id = ?",
                    (memory_id,)
                )
            st.rerun()

    new_memory = st.text_input(
        "Neue Erinnerung hinzufügen"
    )

    if st.button("💾 Erinnerung speichern"):
        if new_memory.strip():
            save_memory(new_memory.strip())
            st.rerun()

    st.divider()

    uploaded_file = st.file_uploader(
        "📎 Bild oder Dokument hochladen",
        type=["png", "jpg", "jpeg", "webp", "pdf"]
    )

    st.divider()

    if st.button("🗑️ Chat löschen"):
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM messages")
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Abmelden"):
        st.session_state.authenticated = False
        st.rerun()

# =====================================
# CHAT HISTORY
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = get_messages()

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

# =====================================
# CHAT INPUT
# =====================================

prompt = st.chat_input(
    "Was soll ich für dich erledigen?"
)

if prompt:

    st.session_state.messages.append(
        ("user", prompt)
    )

    save_message("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Persönliche Erinnerungen laden
    memories = get_memories()

    memory_text = "\n".join(
        item[1] for item in memories
    )

    personal_context = (
        SYSTEM_INSTRUCTION
        + "\n\nPersönliches Gedächtnis:\n"
        + memory_text
    )

    # Gesprächsverlauf vorbereiten
    contents = []

    for role, content in st.session_state.messages[-21:-1]:

        contents.append(
            types.Content(
                role="user" if role == "user" else "model",
                parts=[
                    types.Part.from_text(text=content)
                ]
            )
        )

    current_parts = [
        types.Part.from_text(text=prompt)
    ]

    # Bild oder PDF hinzufügen
    if uploaded_file:

        current_parts.append(
            types.Part.from_bytes(
                data=uploaded_file.getvalue(),
                mime_type=uploaded_file.type
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=current_parts
        )
    )

    # KI ANTWORT
    with st.chat_message("assistant"):

        with st.spinner("Sudem AI denkt nach..."):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=personal_context,
                        temperature=0.7
                    )
                )

                answer = response.text or (
                    "Ich konnte keine Textantwort erstellen."
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    ("assistant", answer)
                )

                save_message("assistant", answer)

            except Exception as error:
                st.error(f"Fehler: {error}")

st.divider()

st.caption(
    "🔒 SUDEM AI | Private Personal Assistant"
)
