import os
from dotenv import load_dotenv
load_dotenv()
from google import genai

# The new SDK uses genai.Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def build_style_profile(sample_messages: list[str]) -> str:
    joined = "\n---\n".join(sample_messages)
    
    # Swapped to 1.5-flash to bypass the 20/day limit
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=(
            "Summarize the writing style below in 3-4 sentences: "
            "tone, typical vocabulary, sentence length, and any "
            "recurring phrasing habits. Return only the summary.\n\n"
            f"{joined}"
        )
    )
    return response.text.strip()