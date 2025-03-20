import streamlit as st
import tkinter as tk
from tkinter import filedialog
import os
from dotenv import load_dotenv
load_dotenv()

PASSWORD = os.getenv("PASSWORD")

from research_assistant import (
    get_video_id,
    fetch_transcript,
    get_sections,
    insert_sections,
    clean_transcript_lines,
    assemble_transcript,
    generate_pdf_from_transcript
)

# --- File Selector Helper ---
def select_folder():
   root = tk.Tk()
   root.withdraw()
   folder_path = filedialog.askdirectory(master=root)
   root.destroy()
   return folder_path

# --- Simple Password Protection ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pwd = st.text_input("Enter password", type="password")
        if pwd == PASSWORD:
            st.session_state.password_correct = True
        else:
            st.error("Incorrect password")
            st.stop()

# --- Main Streamlit App ---
def main():
    st.title("YouTube Transcript PDF Generator")
    check_password()
    
    url = st.text_input("Enter the YouTube video URL:")
    
    if st.button("Select Folder"):
        output_path = select_folder()
        st.session_state['output_path'] = output_path
        st.success(f"Selected file: {output_path}")
    
    if st.button("Generate PDF"):
        if url and 'output_path' in st.session_state and st.session_state['output_path']:
            try:
                video_id = get_video_id(url)
                transcript_text = fetch_transcript(video_id)
                sections = get_sections(url)
                transcript_with_sections = insert_sections(transcript_text, sections)
                cleaned_lines = clean_transcript_lines(transcript_with_sections)
                merged_transcript = assemble_transcript(cleaned_lines)
                # Since we already have an output file via the file dialog, use that path.
                generate_pdf_from_transcript(url, merged_transcript, st.session_state['output_path'])
                st.success("PDF created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter a valid YouTube URL and select an output file.")

if __name__ == "__main__":
    main()
