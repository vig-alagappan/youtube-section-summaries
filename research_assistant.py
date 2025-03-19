import os
import re
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env immediately

from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# Initialize the OpenAI client using the API key from environment variables.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client:
    raise ValueError("Missing OPENAI_API_KEY environment variable.")

def get_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from a standard watch URL.
    Example:
      Input:  https://www.youtube.com/watch?v=8vk6rWMSxOk&ab_channel=RenaissancePeriodization
      Output: 8vk6rWMSxOk
    """
    match = re.search(r"v=([^&]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Could not extract video ID from URL.")

def fetch_transcript(video_id: str) -> str:
    """
    Fetches the transcript for the provided video ID and concatenates it into a single string.
    """
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = "\n".join(segment["text"] for segment in transcript_data)
    return transcript_text

def load_prompt(file_path: str) -> str:
    """
    Loads a prompt template from the specified text file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file '{file_path}' not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_response(context: str, temperature: float = 0.7) -> str:
    """
    Generates a response using the OpenAI API.
    The provided context (agent prompt plus transcript, optionally with a follow-up question)
    is sent as the system message.
    """
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[{"role": "system", "content": context}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def get_summary(url: str, agent_prompt_file: str = "youtube_agent.txt", temperature: float = 0.7) -> (str, str):
    """
    Given a YouTube URL and an agent prompt file, this function:
      - Extracts the video ID.
      - Fetches the video transcript.
      - Loads the agent prompt.
      - Combines them into a base context.
      - Generates and returns the summary.
      
    Returns:
      base_context: The combined agent prompt and transcript.
      summary: The generated summary text.
    """
    video_id = get_video_id(url)
    transcript = fetch_transcript(video_id)
    agent_prompt = load_prompt(agent_prompt_file)
    base_context = f"{agent_prompt}\n\nTranscript:\n{transcript}"
    summary = generate_response(base_context, temperature=temperature)
    return base_context, summary

def get_followup_answer(base_context: str, question: str, temperature: float = 0.7) -> str:
    """
    Given an existing base context (agent prompt + transcript) and a follow-up question,
    generates and returns the answer.
    """
    full_context = f"{base_context}\n\nQuestion: {question}"
    answer = generate_response(full_context, temperature=temperature)
    return answer

# Optionally, you can leave a main() for debugging purposes, but it's not used by your Streamlit UI.
if __name__ == "__main__":
    # For debugging, run: python research_assistant.py
    url = input("URL > ").strip()
    try:
        base_context, summary = get_summary(url)
        print("\n=== Summary ===")
        print(summary)
    except Exception as e:
        print(f"Error: {e}")