import streamlit as st
from google.genai import Client

st.title("Mein privater KIAssistent")
api_key = st.text_input(
    "Gib deinen Gemini API-SchlÃ¼ssel ein*", type="password"
)

if api_key:
    client = Client(api_key=api_key)
    prompt = st.text_input("Wie kann ich dir helfen?")

    if prompt:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        st.write(response.text)
