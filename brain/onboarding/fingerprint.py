"""
Style fingerprinting.

Feed a sample of the user's own emails/messages (WITH their consent) into a
single Claude call asking it to summarize tone, vocabulary, and typical
sentence length as a short style-profile string. Store that string and
prepend it to future agent prompts so outputs sound like the user.
"""

import anthropic

from shared.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def build_style_profile(sample_messages: list[str]) -> str:
    joined = "\n---\n".join(sample_messages)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the writing style below in 3-4 sentences: "
                    "tone, typical vocabulary, sentence length, and any "
                    "recurring phrasing habits. Return only the summary.\n\n"
                    f"{joined}"
                ),
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")
