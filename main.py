import streamlit as st
import subprocess
import os
import zipfile
import base64

# Ensure the uploaded_files directory exists
os.makedirs('uploaded_files', exist_ok=True)

# Function to run your main.py script with the provided file path
def run_main_script(file_path):
    subprocess.run(['python', 'tiktok.py', file_path])

# Function to zip files
def zip_files(file_paths, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in file_paths:
            zipf.write(file)
            os.remove(file)  # Optionally remove the file after adding it to the zip

# Streamlit UI
st.set_page_config(page_title="Automation", page_icon="🎉")

st.title("ZANDO")
st.sidebar.selectbox("Menu", ["Automation", "How to Use", "Copyright"])

st.header("Upload File")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    file_path = f'./uploaded_files/{uploaded_file.name}'
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Run your main.py script here
    run_main_script(file_path)
    st.success("Processing complete")

    # List of files to be zipped
    output_files = ['data.jsonl', 'text.txt', 'translated_transcripts.xlsx']
    existing_files = [file for file in output_files if os.path.exists(file)]

# Function to generate a download link for the given file
def get_download_link(file_name):
    with open(file_name, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    button_html = f'''<a href="data:file/zip;base64,{b64}" download="{file_name}">
                          <button style="color: white; background-color: #FF4B4B; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                              Download File
                          </button>
                      </a>'''
    return button_html

# Zip the files and provide a download link
if existing_files:
    zip_name = f'{uploaded_file.name}.zip'
    zip_files(existing_files, zip_name)
    download_link = get_download_link(zip_name)
    st.markdown(download_link, unsafe_allow_html=True)
    st.markdown("Here's your file, Thank you for using Zando!")

# Footer
st.markdown("---")
st.markdown("Copyright 2024")
st.markdown("[Contact](https://www.instagram.com/yoelmanoppo)")
