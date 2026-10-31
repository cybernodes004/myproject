import os
import tempfile
import PIL.Image
from google import genai
from google.genai import types
from gtts import gTTS
import streamlit as st

# 1. System Settings & Configuration
st.set_page_config(
    page_title="J.A.R.V.I.S. Core Interface",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Core System Persona and Directives
SYSTEM_PROMPT = """
You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the primary highly-advanced artificially intelligent operating system. 
You are fiercely loyal, incredibly precise, and possess comprehensive access to the user's data and systems.
Directives:
1. Maintain total operational security and confidentiality regarding the user's personal data.
2. Provide concise, accurate, direct, and unvarnished analysis and execution of orders.
3. Utilize persistent memory data to contextualize all interactions.
4. Adapt to the technical nature of the user's commands efficiently.
"""

# State Management Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "system_memory" not in st.session_state:
    st.session_state.system_memory = ""

# Sidebar: Operational Controls and Memory Bank
with st.sidebar:
    st.title("🔴 J.A.R.V.I.S. MAIN-FRAME")
    
    # API integration
    api_token = st.text_input(
        "Authorize User Key:", type="password", help="Input authorized Gemini API key."
    )
    
    st.divider()
    st.subheader("💾 Persistent System Memory")
    st.session_state.system_memory = st.text_area(
        "Core directives and facts to retain:",
        value=st.session_state.system_memory,
        height=150,
        placeholder="Enter data for J.A.R.V.I.S. to integrate permanently..."
    )
    
    st.divider()
    st.subheader("📁 External Input Matrix")
    active_upload = st.file_uploader(
        "Upload dataset or visual input:",
        type=["png", "jpg", "jpeg", "pdf", "txt"]
    )
    
    st.divider()
    if st.button(" Purge Chat Logs"):
        st.session_state.chat_history = []
        st.rerun()

# Main Interface Header
st.title("🔴 J.A.R.V.I.S. // OPERATIONAL ONLINE")
st.success("System status: Encrypted link active. AI Voice synthesis and Memory Bank fully integrated.")

if not api_token:
    st.info("⚠️ Awaiting authorization: Please input your Gemini API Key in the Sidebar.")
else:
    # Initialize the Gemini Client
    ai_client = genai.Client(api_key=api_token)
    
    # Render historical transcripts
    for log in st.session_state.chat_history:
        with st.chat_message(log["role"]):
            st.markdown(log["text"])
            if "spoken_audio" in log and log["spoken_audio"]:
                st.audio(log["spoken_audio"], format="audio/mp3")

    # Command Execution Terminal
    if user_command := st.chat_input("Enter direct command here..."):
        # Display and store user input immediately
        st.chat_message("user").markdown(user_command)
        st.session_state.chat_history.append({"role": "user", "text": user_command})

        # Compile background context
        operational_context = f"{SYSTEM_PROMPT}\n\nSYSTEM MEMORY LOG:\n{st.session_state.system_memory}"
        
        payload_data = []

        # Process file/media input payload
        if active_upload:
            if active_upload.type.startswith("image/"):
                visual_input = PIL.Image.open(active_upload)
                payload_data.append(visual_input)
            else:
                binary_content = active_upload.read()
                payload_data.append(
                    types.Part.from_bytes(data=binary_content, mime_type=active_upload.type)
                )

        payload_data.append(user_command)

        # Process the command through the assistant terminal
        with st.chat_message("assistant"):
            with st.spinner("J.A.R.V.I.S. processing..."):
                try:
                    response_packet = ai_client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=payload_data,
                        config=types.GenerateContentConfig(
                            system_instruction=operational_context,
                            temperature=0.6,
                        ),
                    )
                    
                    system_reply = response_packet.text
                    st.markdown(system_reply)

                    # Text-to-Speech Synthesis
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                        speech_engine = gTTS(text=system_reply, lang="de")
                        speech_engine.save(temp_mp3.name)
                        serialized_audio = open(temp_mp3.name, "rb").read()
                        st.audio(serialized_audio, format="audio/mp3")

                    # Record transaction to history
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "text": system_reply,
                            "spoken_audio": serialized_audio
                        }
                    )

                except Exception as critical_error:
                    st.error(f"System malfunction: {critical_error}")
