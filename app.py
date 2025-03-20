import os
import io
import streamlit as st
from research_assistant import (
    get_video_id,
    fetch_transcript,
    get_sections,
    insert_sections,
    clean_transcript_lines,
    assemble_transcript,
    generate_filename,
    write_paragraph_to_pdf
)
from fpdf import FPDF

# --- Password Protection ---
PASSWORD = os.getenv("PASSWORD", "my_secret_password")

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

# --- Generate PDF in memory and return a BytesIO buffer ---
def generate_pdf_buffer(url: str, transcript_text: str) -> io.BytesIO:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Write source at the top
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"Source: {url}")
    pdf.ln(5)

    paragraphs = transcript_text.split("\n\n")
    for paragraph in paragraphs:
        write_paragraph_to_pdf(paragraph, pdf)
    
    # Get PDF as a string using destination "S"
    pdf_str = pdf.output(dest="S")
    # Encode to bytes (FPDF outputs in Latin-1 encoding by default)
    pdf_bytes = pdf_str.encode("latin1")
    # Create a BytesIO buffer with the PDF bytes
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer


# --- Main Streamlit App ---
def main():
    st.title("YouTube Transcript PDF Generator")
    check_password()
    
    url = st.text_input("Enter the YouTube video URL:")
    
    if st.button("Generate PDF"):
        if url:
            try:
                # Process the video and transcript
                video_id = get_video_id(url)
                transcript_text = fetch_transcript(video_id)
                sections = get_sections(url)
                transcript_with_sections = insert_sections(transcript_text, sections)
                cleaned_lines = clean_transcript_lines(transcript_with_sections)
                merged_transcript = assemble_transcript(cleaned_lines)
                
                # Automatically generate a file name from video metadata
                output_filename = generate_filename(url, "")  # returns just the filename
                
                # Generate the PDF in memory
                pdf_buffer = generate_pdf_buffer(url, merged_transcript)
                
                # Offer the PDF via a download button
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=output_filename,
                    mime="application/pdf"
                )
                st.success("PDF generated successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()
