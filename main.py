

# =========================
# KONFIGURATION
# =========================

DB = "sudem_memory.db"

"st_set_page_config" (
    page_title="Sudem AI",
    page_icon='🧠'
)
  

MY_PASSWORD = os.getenv("MY_PASSWORD", "")

st.set_page_config(
    page_title="Sudem AI",
    page_icon="🧠",
    layout="wide"
)

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🧠 SUDEM AI")
    st.write("Willkommen bei deiner persönlichen KI!")

    password = st.text_input(
        "Dein persönliches Passwort",
        type="password"
    )

    if st.button("Einloggen"):
        if hmac.compare_digest(password, MY_PASSWORD):
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Falsches Passwort!")

    st.stop()

st.title("❤️ Hallo Sudem!")
st.success("Du bist erfolgreich eingeloggt.")
st.write("Deine persönliche KI ist bereit!")
if not API_KEY or not MY_PASSWORD:
    st.error("API-Schlüssel oder Passwort fehlt in .env")
    st.stop()

client = genai.Client(api_key=API_KEY)

# =========================
# LOKALE DATENBANK
# =========================

def database():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT
            )
        """)

database()


def load_messages():
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT role, content FROM messages ORDER BY id"
        ).fetchall()


def save_message(role, content):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content)
        )


def load_memories():
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT id, content FROM memories"
        ).fetchall()


# =========================
# LOGIN
# =========================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🧠 SUDEM AI")
    st.subheader("Dein privater KI-Assistent")

    with st.form("login"):
        password = st.text_input(
            "Dein persönliches Passwort",
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

# =========================
# DESIGN
# =========================

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
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# KI-PERSÖNLICHKEIT
# =========================

SYSTEM = """
Du bist SUDEM AI.

Du bist der persönliche digitale Assistent
deiner Besitzerin.

Deine Aufgaben:
- Fragen beantworten
- Informationen erklären
- Probleme lösen
- Dokumente analysieren
- Aufgaben organisieren
- Ideen entwickeln
- Texte schreiben
- Bei Entscheidungen helfen

Du bist freundlich, intelligent,
zuverlässig und diskret.

Du sprichst standardmäßig Deutsch.
Du kannst auch Türkisch und Englisch.

Du darfst niemals behaupten,
eine Aktion ausgeführt zu haben,
wenn du sie nicht wirklich ausgeführt hast.

Frage vor externen oder wichtigen Aktionen
immer nach Zustimmung.
"""

# =========================
# OBERFLÄCHE
# =========================

st.title("🧠 SUDEM AI")
st.caption("Dein persönlicher Assistent")

with st.sidebar:

    st.title("⚙️ Einstellungen")

    st.success("Privater Zugang aktiviert")

    st.subheader("Mein Gedächtnis")

    memories = load_memories()

    for memory_id, memory in memories:
        st.write("🧠", memory)

    new_memory = st.text_input(
        "Was soll ich mir merken?"
    )

    if st.button("Speichern"):
        if new_memory.strip():
            with sqlite3.connect(DB) as con:
                con.execute(
                    "INSERT INTO memories (content) VALUES (?)",
                    (new_memory,)
                )
            st.rerun()

    if st.button("Gespräch löschen"):
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM messages")
        st.session_state.messages = []
        st.rerun()

    if st.button("Abmelden"):
        st.session_state.authenticated = False
        st.rerun()

    uploaded_file = st.file_uploader(
        "Bild oder PDF hochladen",
        type=["png", "jpg", "jpeg", "webp", "pdf"]
    )

# =========================
# CHATVERLAUF
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

for message in st.session_state.messages:
    with st.chat_message(message[0]):
        st.markdown(message[1])

# =========================
# EINGABE
# =========================

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

    # Persönliches Gedächtnis laden
    memory_text = "\n".join(
        memory[1] for memory in load_memories()
    )

    instructions = SYSTEM + """

    PERSÖNLICHE ERINNERUNGEN:
    """ + memory_text

    contents = []

    # Letzte 20 Nachrichten als Kontext
    for role, content in st.session_state.messages[-20:-1]:
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

    # Datei hinzufügen
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

    # KI AUSFÜHREN
    with st.chat_message("assistant"):

        with st.spinner("Sudem AI arbeitet..."):

            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.7
                    )
                )

                answer = response.text

                if not answer:
                    answer = "Ich konnte keine Textantwort erstellen."

                st.markdown(answer)

                st.session_state.messages.append(
                    ("assistant", answer)
                )

                save_message("assistant", answer)

            except Exception as error:
                st.error(f"Fehler: {error}")
