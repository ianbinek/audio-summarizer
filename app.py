import streamlit as st
import tempfile
from openai import OpenAI
from pydub import AudioSegment
import os

# Get your API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("Audio to Rich Summary ✍️🎙️ (Auto-Convert Built In)")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "mp4", "m4a", "wav", "mov", "aiff", "caf", "ogg", "webm"]
)

def convert_audio_to_mp3(input_path):
    output_path = input_path.replace(".tmp", "_converted.mp3")
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3")
    return output_path

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_audio_path = tmp_file.name

    with st.spinner('Converting audio to mp3 format if needed...'):
        try:
            converted_audio_path = convert_audio_to_mp3(input_audio_path)
        except Exception as e:
            st.error(f"Audio conversion failed: {e}")
            st.stop()

    with st.spinner('Transcribing audio...'):
        with open(converted_audio_path, "rb") as f:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        transcript = transcript_response.text

    st.success("Transcription Complete!")
    st.text_area("Transcript", transcript, height=300)

    with st.spinner('Summarizing...'):
        summary_prompt = f"""Summarize the following conversation into main ideas with bulleted points under each main idea. Make it comprehensive enough that someone would not have to listen to the original recording.

Transcript:
{transcript}
"""
        chat_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes audio transcriptions into clear, rich summaries with main ideas and bullet points."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        summary = chat_response.choices[0].message.content

    st.success("Summary Complete!")
    st.text_area("Summary", summary, height=400)
