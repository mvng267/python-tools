import os
from google.cloud import speech
from pydub import AudioSegment

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Admin\Documents\GitHub\python-tools\speech_to_text\key.json"

def convert_m4a_to_mp3(input_path, output_path):
    """
    Convert M4A file to MP3 using pydub and ffmpeg.
    """
    try:
        audio = AudioSegment.from_file(input_path, format="m4a")
        audio.export(output_path, format="mp3")
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {input_path}: {e}")

def transcribe_audio_long(gcs_uri):
    """
    Transcribe long audio files using LongRunningRecognize.
    """
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    audio = speech.RecognitionAudio(uri=gcs_uri)

    # LongRunningRecognize for large audio files
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Processing long audio... This may take a while.")
    response = operation.result(timeout=600)

    # Collect the transcript
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript

def upload_to_gcs(local_path, bucket_name, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage.
    """
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_path)

    print(f"Uploaded {local_path} to gs://{bucket_name}/{destination_blob_name}")
    return f"gs://{bucket_name}/{destination_blob_name}"

def process_audio_folder(input_folder, output_folder, output_text_file, bucket_name):
    """
    Process all audio files in a folder, convert M4A to MP3, upload long audio files to GCS,
    transcribe them, and save to output text file.
    """
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist!")
        return
    
    with open(output_text_file, "w", encoding="utf-8") as out_file:
        for file_name in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file_name)
            if not os.path.isfile(file_path):
                continue

            # Convert M4A to MP3 if necessary
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
                # Check file duration for long audio
                audio_duration = AudioSegment.from_file(audio_path).duration_seconds
                if audio_duration > 60:  # Long audio
                    destination_blob_name = f"audio/{file_name}"
                    gcs_uri = upload_to_gcs(audio_path, bucket_name, destination_blob_name)
                    transcript = transcribe_audio_long(gcs_uri)
                else:  # Short audio
                    transcript = transcribe_audio_to_text(audio_path)

                out_file.write(f"File: {file_name}\n")
                out_file.write(f"Transcript:\n{transcript}\n")
                out_file.write("=" * 80 + "\n")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

def transcribe_audio_to_text(audio_path):
    """
    Convert audio to text using Google Speech-to-Text API for short audio.
    """
    client = speech.SpeechClient()
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript

if __name__ == "__main__":
    input_folder = "C:/Users/Admin/Documents/GitHub/python-tools/speech_to_text/input"
    output_folder = "mp3_output"
    output_text_file = "transcripts.txt"
    bucket_name = "your-bucket-name"  # Replace with your Google Cloud Storage bucket name

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    process_audio_folder(input_folder, output_folder, output_text_file, bucket_name)
    print(f"Transcripts saved to {output_text_file}")
