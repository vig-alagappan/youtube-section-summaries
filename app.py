import os
import streamlit as st
from research_assistant import (
    get_video_id,
    fetch_transcript,
    get_sections,
    insert_sections,
    clean_transcript_lines,
    assemble_transcript,
    generate_filename,
    generate_pdf_from_transcript
)

# --- Password Protection ---
PASSWORD = os.getenv("PASSWORD", "my_secret_password")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        pwd = st.text_input("Enter password", type="default")
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
    output_dir = st.text_input("Enter output directory path:" ).strip().strip('\'"')
    
    if st.button("Generate PDF"):
        if url and output_dir:
            try:
                # Process the video and transcript
                video_id = get_video_id(url)
                transcript_text = fetch_transcript(video_id)
                sections = get_sections(url)
                transcript_with_sections = insert_sections(transcript_text, sections)
                cleaned_lines = clean_transcript_lines(transcript_with_sections)
                merged_transcript = assemble_transcript(cleaned_lines)
                
                # Generate the output file path automatically using the video metadata
                output_path = generate_filename(url, output_dir)
                
                # Generate the PDF
                generate_pdf_from_transcript(url, merged_transcript, output_path)
                st.success(f"PDF created successfully at {output_path}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter a valid YouTube URL and output directory path.")

if __name__ == "__main__":
    main()
