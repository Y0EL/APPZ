import sys
import subprocess
import os
import warnings
import json
import pandas as pd
from deepl import Translator
from faster_whisper import WhisperModel

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize DeepL API client with your API key
deepl_client = Translator(auth_key="74889b94-08bd-4938-a555-5aed76fb20ae:fx")

def download_audio(url, output_name):
    command = f"yt-dlp -x --audio-format mp3 -o {output_name} {url}"
    subprocess.run(command, shell=True)

def transcribe_audio(audio_path):
    model_size = "base"
    model = WhisperModel(model_size, device="cpu")
    segments, _ = model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])

def process_tiktok_links(links_file_path):
    df_data = []

    with open(links_file_path, 'r') as file:
        urls = file.readlines()

    os.remove(links_file_path)  # Delete the uploaded file

    with open('data.jsonl', 'w') as data_jsonl_file, open('text.txt', 'w') as text_file:
        for url in urls:
            url = url.strip()
            if not url.startswith("https://"):
                print(f"Invalid URL format: {url}")
                continue

            audio_name = f"tiktok_audio_{url.split('/')[-1]}.mp3"
            download_audio(url, audio_name)

            if os.path.exists(audio_name):
                transcription = transcribe_audio(audio_name)
                translation = deepl_client.translate_text(transcription, target_lang="ID")

                result_data = {
                    "text": translation.text,
                    "detected_source_lang": translation.detected_source_lang
                }

                best_words = generate_user_questions(translation.text)

                data = {
                    "messages": [
                        {"role": "system", "content": "TikTok audio transcription and translation"},
                        {"role": "user", "content": best_words},
                        {"role": "assistant", "content": result_data}
                    ]
                }
                data_jsonl_file.write(json.dumps(data) + "\n")
                text_file.write(translation.text + '\n')
                df_data.append([url, translation.text])

                os.remove(audio_name)
            else:
                print(f"Audio file not found: {audio_name}")

    df = pd.DataFrame(df_data, columns=["Link", "Translated Transcript"])
    df.to_excel("translated_transcripts.xlsx", index=False)

def generate_user_questions(translation):
    if translation:
        words = translation.split()
        sorted_words = sorted(words, key=lambda word: len(word), reverse=True)
        best_words = sorted_words[:5]
        return ' '.join(best_words)
    return ''

if __name__ == "__main__":
    if len(sys.argv) > 1:
        links_file_path = sys.argv[1]
        process_tiktok_links(links_file_path)
    else:
        print("No file path provided.")
