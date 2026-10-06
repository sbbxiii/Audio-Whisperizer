"""
Audio Whisperizer - Local Audio Transcription & Subtitle Generator
Powered by OpenAI Whisper & Streamlit
"""

import os
import tempfile
import time
from datetime import timedelta
import streamlit as st
import whisper


st.set_page_config(
    page_title="Audio Whisperizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def load_whisper_model(model_name: str):
    """Load and cache the OpenAI Whisper model."""
    return whisper.load_model(model_name)


def format_timestamp(seconds: float) -> str:
    """Format seconds into SRT timestamp (HH:MM:SS,mmm)."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments: list) -> str:
    """Generate SubRip Subtitle (SRT) format from Whisper segments."""
    srt_lines = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_lines)


def main():
    st.title("🎙️ Audio Whisperizer")
    st.caption("Local, private automatic speech recognition powered by OpenAI Whisper")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Model Settings")
        model_size = st.selectbox(
            "Select Whisper Model:",
            options=["tiny", "base", "small", "medium"],
            index=1,
            help="Larger models provide higher accuracy but require more memory and processing time.",
        )
        task_mode = st.radio(
            "Task:",
            options=["transcribe", "translate"],
            format_func=lambda x: "Transcribe (Original Language)" if x == "transcribe" else "Translate to English",
            help="Translate converts non-English audio directly into English text.",
        )
        st.divider()
        st.markdown(
            "### 💡 Features\n"
            "- **Zero Cloud Leak:** Processes 100% locally on your machine.\n"
            "- **Multi-Format:** Supports MP3, WAV, M4A, OGG, and FLAC.\n"
            "- **Subtitle Export:** Direct download for `.srt` and `.txt`.\n"
        )

    # Audio file uploader
    uploaded_file = st.file_uploader(
        "Upload an audio file to transcribe:",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        help="Upload clear speech for optimal transcription results.",
    )

    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / (1024 * 1024):.2f} MB",
            "File type": uploaded_file.type or uploaded_file.name.split(".")[-1].upper(),
        }

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🎵 Audio Player")
            st.audio(uploaded_file)
            st.json(file_details)

        with col2:
            st.subheader("📝 Transcription")
            if st.button("🚀 Transcribe Audio", type="primary", use_container_width=True):
                # Save uploaded audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    temp_audio_path = tmp.name

                try:
                    with st.spinner(f"Loading '{model_size}' model and processing audio..."):
                        start_time = time.time()
                        model = load_whisper_model(model_size)
                        result = model.transcribe(temp_audio_path, task=task_mode)
                        elapsed_time = time.time() - start_time

                    transcription_text = result.get("text", "").strip()
                    detected_language = result.get("language", "unknown").upper()
                    segments = result.get("segments", [])
                    srt_content = generate_srt(segments)

                    # Display metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    metric_col1.metric("Processing Time", f"{elapsed_time:.1f}s")
                    metric_col2.metric("Detected Language", detected_language)
                    metric_col3.metric("Word Count", len(transcription_text.split()))

                    st.text_area("Full Transcript:", value=transcription_text, height=220)

                    # Download options
                    dl_col1, dl_col2 = st.columns(2)
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    with dl_col1:
                        st.download_button(
                            label="📥 Download Plain Text (.txt)",
                            data=transcription_text,
                            file_name=f"{base_name}_transcript.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )
                    with dl_col2:
                        st.download_button(
                            label="🎬 Download Subtitles (.srt)",
                            data=srt_content,
                            file_name=f"{base_name}_subtitles.srt",
                            mime="application/x-subrip",
                            use_container_width=True,
                        )

                except Exception as e:
                    st.error(f"Error during transcription: {e}")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)


if __name__ == "__main__":
    main()
