import streamlit as st

st.title("Mein privater KIAssistent")
api_key = st.text_input(
    "Gib deinen Gemini API-Schlüssel ein*", type="password"
)

if api_key:
  client = genai.Client(api_key=api_key)
  prompt = st.text_input("Wie kann ich dir helfen?")

  if prompt:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    st.write(response.text)
