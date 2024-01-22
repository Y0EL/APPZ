import streamlit as st
import base64
import os
import subprocess
import zipfile

# Ensure the uploaded_files directory exists
os.makedirs('uploaded_files', exist_ok=True)

# Function to install packages listed in the 'installation' file
def install_packages():
    with open('installation', 'r') as f:
        packages_to_install = f.read().splitlines()
    
    for package in packages_to_install:
        try:
            subprocess.check_call(['pip', 'install', package])
            st.success(f'Successfully installed {package}')
        except subprocess.CalledProcessError as e:
            st.error(f'Error installing {package}: {str(e)}')

# Function to run your main.py script with the provided file path
def run_main_script(script_path, file_path):
    try:
        subprocess.run(['python', script_path, file_path], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f'Error running {script_path}: {str(e)}')

# Streamlit UI
st.set_page_config(page_title="Automation", page_icon="🎉")

st.title("ZANDO")

st.header("Upload File")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    file_path = f'./uploaded_files/{uploaded_file.name}'
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Install packages listed in the 'installation' file
    install_packages()

    # Run your main.py script here, specifying the correct path to tiktok.py
    script_path = 'tiktok.py'  # Adjust the path as needed
    run_main_script(script_path, file_path)
    st.success("Processing complete")

    # List of files to be zipped
    output_files = ['data.jsonl', 'text.txt', 'transcripts.xlsx']
    existing_files = [file for file in output_files if os.path.exists(file)]

    # Zip the files and provide a download link
    if existing_files:
        zip_name = f'{uploaded_file.name}.zip'
        zip_files(existing_files, zip_name)
        download_link = get_download_link(zip_name)
        st.markdown(download_link, unsafe_allow_html=True)
        st.markdown("Here's your file, Thank you for using Zando!")

# Footer
st.markdown("---")
st.markdown("[Copyright](https://www.instagram.com/yoelmanoppo) 2024")
