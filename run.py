import sys
import subprocess
import os
import warnings
import json
import pandas as pd
import zipfile
from faster_whisper import WhisperModel
import openai  # Import OpenAI library
from langdetect import detect  # Import language detection library

warnings.filterwarnings("ignore", category=UserWarning)

# OpenAI API key setup
openai.api_key = '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'

def download_audio(url, output_name):
    command = f"yt-dlp -x --audio-format mp3 -o {output_name} {url}"
    subprocess.run(command, shell=True)

def transcribe_audio(audio_path):
    model_size = "base"
    model = WhisperModel(model_size, device="cpu")
    segments, _ = model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"  # Fallback language if detection fails

def translate_text(text, target_lang="id"):
    prompt = f"Terjemahkan Bahasa ini ke {target_lang}:\n\n{text} \n\n dan lengkapi seluruh kata yang tidak lengkap, buat semuanya menjadi lebih masuk akal"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate this to {target_lang}:"},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Translation failed: {str(e)}"

def generate_question(text):
    question_prompt = f"Buatlah pertanyaan terbaik dan masuk akal yang memicu banyak pertanyaan lainnya berdasarkan teks ini:\n\n{text} \n\n Pastikan kamu memahami konteksnya dan buat banyak pertanyaan dari itu dipisahkan oleh koma"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": question_prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        # Replace new lines with commas
        return response.choices[0].message.content.strip().replace('\n', ', ')
    except Exception as e:
        return f"Question generation failed: {str(e)}"

def process_tiktok_links(links_file_path):
    df_data = []
    data_jsonl = []

    with open(links_file_path, 'r') as file, open('text.txt', 'w') as text_file:
        urls = file.readlines()

        for url in urls:
            url = url.strip()
            if not url.startswith("https://"):
                print(f"Invalid URL format: {url}")
                continue

            audio_name = f"tiktok_audio_{url.split('/')[-1]}.mp3"
            download_audio(url, audio_name)

            if os.path.exists(audio_name):
                transcription = transcribe_audio(audio_name)
                translation = translate_text(transcription)
                text_file.write(translation + '\n\n')

                generated_question = generate_question(translation)
                data = {
                    "messages": [
                        {"role": "system", "content": "Sistem, berikan pemahaman mendalam tentang konten pada data ini, analisa transkrip dan kumpulkan data, kemudian jelaskan konsep-konsep kunci yang teridentifikasi, pelajari pola unik yang terdapat pada transkrip yang dapat dioptimalkan, berikan respon terbaik berdasarkan transkrip, pelajari bagaimana menghasilkan respon terbaik untuk konten-konten berikutnya supaya lebih menarik dan dapat diandalkan, berperanlah sebagai Profesional untuk analisa konten yang memiliki potensi viral, selalu berikan rating pada setiap respon dan potensi viral dari konten yang telah direspon berdasarkan transkrip"},
                        {"role": "user", "content": generated_question},
                        {"role": "assistant", "content": translation}
                    ]
                }
                data_jsonl.append(data)
                df_data.append([url, translation])
                os.remove(audio_name)

    with open('data.jsonl', 'w') as data_jsonl_file:
        for item in data_jsonl:
            data_jsonl_file.write(json.dumps(item) + "\n")

    df = pd.DataFrame(df_data, columns=["Link", "Translated Transcript"])
    df.to_excel("transcripts.xlsx", index=False)

def zip_files(file_paths, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in file_paths:
            if os.path.exists(file):
                zipf.write(file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        links_file_path = sys.argv[1]
        process_tiktok_links(links_file_path)
