import os
import json
from google.cloud import speech
from pydub import AudioSegment

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def convert_m4a_to_mp3(input_path, output_path):
    """
    Convert M4A file to MP3 using pydub and ffmpeg.

    Args:
        input_path (str): Path to the input M4A file.
        output_path (str): Path to save the output MP3 file.

    Returns:
        None
    """
    try:
        audio = AudioSegment.from_file(input_path, format="m4a")
        audio.export(output_path, format="mp3")
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {input_path}: {e}")

def transcribe_audio_to_text(audio_path):
    """
    Convert audio to text using Google Speech-to-Text API.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: The transcribed text.
    """
    client = speech.SpeechClient()

    # Load audio file
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # Adjust based on your audio format
        sample_rate_hertz=16000,  # You may need to adjust based on your audio sample rate
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Collect the transcribed text
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript

def process_audio_folder(input_folder, output_folder, output_text_file):
    """
    Process all audio files in a folder, convert M4A to MP3, transcribe them to text, and save to output text file.

    Args:
        input_folder (str): Path to the folder containing audio files.
        output_folder (str): Folder to save converted MP3 files.
        output_text_file (str): Path to save the text file containing file names and transcripts.

    Returns:
        None
    """
    with open(output_text_file, "w", encoding="utf-8") as out_file:
        for file_name in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file_name)

            if os.path.isfile(file_path):
                # Check if the file is in M4A format and convert it to MP3
                if file_path.endswith(".m4a"):
                    mp3_file_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + ".mp3")
                    convert_m4a_to_mp3(file_path, mp3_file_path)
                    audio_path = mp3_file_path
                elif file_path.endswith((".mp3", ".wav", ".flac")):
                    audio_path = file_path
                else:
                    continue

                try:
                    print(f"Processing file: {file_name}")
                    transcript = transcribe_audio_to_text(audio_path)
                    out_file.write(f"File: {file_name}\n")
                    out_file.write(f"Transcript:\n{transcript}\n")
                    out_file.write("=" * 80 + "\n")
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    # Folder containing audio files
    input_folder = "input"
    
    # Folder to save converted MP3 files
    output_folder = "mp3_output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Path to save the output text file
    output_text_file = "transcripts.txt"

    # Process folder and generate transcripts
    process_audio_folder(input_folder, output_folder, output_text_file)
    print(f"Transcripts saved to {output_text_file}")
