import streamlit as st
import os
import whisper

def save_uploaded_file(uploaded_file, save_path):
    with open(os.path.join(save_path, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def load_whisper_model():
    model = whisper.load_model("base")
    return model


model = load_whisper_model()

def transcribe_audio(mp3_filepath):
    # Transcribe using whisper
    result = model.transcribe(mp3_filepath)
    transcription = result['text']
    return transcription

def main():
    st.title("Audio Whisperizer")

    # File uploader widget
    uploaded_file = st.file_uploader("Upload an audio file", type="mp3")

    if uploaded_file is not None:
        save_path = "audio_files"  # Folder to save the uploaded file
        os.makedirs(save_path, exist_ok=True)

        # Display the uploaded file
        st.audio(uploaded_file, format='audio/mp3')

        # Save the uploaded file
        save_uploaded_file(uploaded_file, save_path)
        st.success("Audio file uploaded successfully.")

        # Transcribe the audio
        transcribed_text = transcribe_audio(
            f"audio_files/{uploaded_file.name}")

        # Display the transcribed text
        st.subheader("Transcribed Text:")
        st.text_area("Transcribed Text", value=transcribed_text, height=200)
        st.download_button("Download Transcription", data=transcribed_text, file_name="transcription.txt", mime="text/plain")   


if __name__ == "__main__":
    main()


#streamlit run main.py    