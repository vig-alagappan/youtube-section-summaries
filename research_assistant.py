import os
import re
from dotenv import load_dotenv
load_dotenv()
from fpdf import FPDF
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from pytubefix import YouTube

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client:
    raise ValueError("Missing OPENAI_API_KEY environment variable.")

def get_video_id(url: str) -> str:
    match = re.search(r"v=([^&]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Could not extract video ID from URL.")

def fetch_transcript(video_id: str) -> str:
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    cleaned_transcript = [
        segment['text']
        for segment in transcript_data
        if not re.fullmatch(r'\[.*\]', segment['text'].strip())
    ]
    transcript_text = "\n".join(f"{i+1}: {line}" for i, line in enumerate(cleaned_transcript))
    return transcript_text

def load_prompt(file_path: str = "/Users/vignesh.alagappan/Documents/GitHub/youtube-section-summaries/youtube_agent.txt") -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file '{file_path}' not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_response(context: str, temperature: float) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[{"role": "system", "content": context}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def get_sections(url: str) -> str:
    video_id = get_video_id(url)
    transcript = fetch_transcript(video_id)
    agent_prompt = load_prompt()
    context = f"{agent_prompt}\n\nVideo Transcript:\n{transcript}"
    sections = generate_response(context, temperature=0.1)
    return sections

def insert_sections(transcript: str, sections_str: str) -> str:
    transcript_lines = transcript.split("\n")
    if sections_str.strip() != "Transcript Not Available":
        section_defs = []
        for line in sections_str.splitlines():
            m = re.match(r"(.+):\s*Line\s*(\d+)", line)
            if m:
                section_name = m.group(1).strip()
                line_num = int(m.group(2))
                section_defs.append((line_num, section_name))
        section_defs.sort(key=lambda x: x[0], reverse=True)
        for line_num, section_name in section_defs:
            index = line_num - 1
            if index < len(transcript_lines):
                transcript_lines.insert(index, f"### {section_name}")
            else:
                transcript_lines.append(f"### {section_name}")
    return "\n".join(transcript_lines)

def clean_transcript_lines(transcript: str):
    lines = transcript.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.startswith("###"):
            cleaned_lines.append(line)
        else:
            cleaned_line = re.sub(r'^\d+:\s*', '', line)
            cleaned_lines.append(cleaned_line)
    return cleaned_lines

def assemble_transcript(clean_lines) -> str:
    paragraphs = []
    current_paragraph = []
    for line in clean_lines:
        if line.startswith("###"):
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph).strip())
                current_paragraph = []
            paragraphs.append(line.strip())
        else:
            if line.strip():
                current_paragraph.append(line.strip())
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph).strip())
    return "\n\n".join(paragraphs)

def write_paragraph_to_pdf(paragraph, pdf):
    # Add spacing before the paragraph.
    pdf.ln(4)
    if paragraph.startswith("###"):
        header_text = paragraph.lstrip("###").strip()
        pdf.set_font("Arial", "B", 18)
        pdf.multi_cell(0, 10, header_text)
    else:
        pdf.set_font("Arial", "", 14)
        pdf.multi_cell(0, 10, paragraph)
    # Add equal spacing after the paragraph.
    pdf.ln(4)

def generate_filename(url: str, output_dir: str) -> str:
    outp
    
    yt = YouTube(url)
    channel_name = yt.author
    video_title = yt.title
    safe_channel = re.sub(r'\W+', '-', channel_name.lower())
    safe_title = re.sub(r'\W+', '-', video_title.lower())
    filename = f"{safe_channel}_{safe_title}.pdf"
    return os.path.join(output_dir, filename)

def generate_pdf_from_transcript(url, transcript_text, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"Source: {url}")
    pdf.ln(5)

    paragraphs = transcript_text.split("\n\n")
    for paragraph in paragraphs:
        write_paragraph_to_pdf(paragraph, pdf)
    pdf.output(output_path)