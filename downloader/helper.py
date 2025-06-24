import subprocess
import os
import whisper

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
def extract_audio(video_path):
    """Extract .wav audio from video using ffmpeg"""
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(AUDIO_DIR, f"{base_name}.wav")

    command = [
        "ffmpeg",
        "-y",                # Overwrite existing file
        "-i", video_path,    # Input video
        "-vn",               # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",      # 16k sample rate
        "-ac", "1",          # Mono
        audio_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Audio extracted to {audio_path}")
        return audio_path
    except subprocess.CalledProcessError as e:
        print("❌ Audio extraction failed:", e)
        return None


def transcribe_audio(audio_path):
    """Transcribe audio to text using Whisper"""
    try:
        model = whisper.load_model("base")  # or "small", "medium", "large" if you want better accuracy
        print("🎙️ Transcribing audio...")
        result = model.transcribe(audio_path)
        transcript = result["text"]
        print("✅ Transcription complete.")
        print(transcript[:10])
        return transcript
    except Exception as e:
        print("❌ Transcription failed:", e)
        return None

