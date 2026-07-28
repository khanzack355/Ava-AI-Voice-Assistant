"""
gemini_client.py

Thin wrapper around the Google Gen AI SDK (the current, officially
recommended "google-genai" package) used by the rest of the app.
Keeping all Gemini calls in one place makes it easy to change models,
add logging, or swap providers later without touching the UI code.
"""

import json

from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-3.5-flash"


def get_client(api_key: str) -> genai.Client:
    """Create a Gemini client from an API key."""
    if not api_key:
        raise ValueError(
            "No Gemini API key was provided. Set it in .streamlit/secrets.toml "
            "as GEMINI_API_KEY or as an environment variable before running the app."
        )
    return genai.Client(api_key=api_key)


def _history_to_contents(history: list[dict]) -> list[types.Content]:
    """
    Convert the app's simple chat history format:
        [{"role": "user" | "assistant", "text": "..."}]
    into the Content objects the Gemini API expects.
    """
    contents = []
    for turn in history:
        role = "user" if turn["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=turn["text"])])
        )
    return contents


def send_chat_message(
    client: genai.Client,
    system_prompt: str,
    history: list[dict],
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Send the full conversation so far (including the latest user turn,
    which should already be appended to history) and return Ava's reply
    as plain text.
    """
    response = client.models.generate_content(
        model=model,
        contents=_history_to_contents(history),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    return (response.text or "").strip()


def transcribe_audio(
    client: genai.Client,
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Send recorded audio straight to Gemini and get back a plain text
    transcription of what the customer said. Gemini understands audio
    natively, so no separate speech-to-text library is required.
    """
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    types.Part.from_text(
                        text=(
                            "Transcribe exactly what is said in this audio clip. "
                            "Return only the transcribed words, nothing else."
                        )
                    ),
                ],
            )
        ],
    )
    return (response.text or "").strip()


def generate_report(
    client: genai.Client,
    system_prompt: str,
    report_prompt: str,
    history: list[dict],
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Turn a finished conversation into a written assessment report.
    """
    transcript_lines = []
    for turn in history:
        speaker = "Customer" if turn["role"] == "user" else "Ava"
        transcript_lines.append(f"{speaker}: {turn['text']}")
    transcript = "\n".join(transcript_lines)

    full_prompt = f"{report_prompt}\n\nConversation transcript:\n{transcript}"

    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
        ),
    )
    return (response.text or "").strip()


def extract_financial_metrics(
    client: genai.Client,
    history: list[dict],
    model: str = DEFAULT_MODEL,
) -> dict | None:
    """
    Look back over a finished financial conversation and pull out a few
    approximate monthly numbers (income, expenses, savings) so the report
    can include a simple chart. Returns None if the customer never gave
    enough numeric detail to make a meaningful chart, rather than guessing.
    """
    transcript_lines = []
    for turn in history:
        speaker = "Customer" if turn["role"] == "user" else "Ava"
        transcript_lines.append(f"{speaker}: {turn['text']}")
    transcript = "\n".join(transcript_lines)

    prompt = f"""
Read the conversation transcript below. If the customer gave enough
information to estimate their approximate MONTHLY income, monthly
expenses, and monthly savings in a single consistent currency, return
those three numbers. If they used a different time period (for example
yearly), convert it to a monthly figure. If a number was never
discussed clearly enough to estimate, use null for that field instead
of guessing.

Respond with ONLY a JSON object in exactly this shape, nothing else:
{{"income": <number or null>, "expenses": <number or null>, "savings": <number or null>, "currency_symbol": "<best guess symbol, e.g. $, or empty string if unclear>"}}

Conversation transcript:
{transcript}
"""

    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    raw = (response.text or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    income = data.get("income")
    expenses = data.get("expenses")
    savings = data.get("savings")

    # Need at least two of the three numbers for a chart to mean anything.
    present = [v for v in (income, expenses, savings) if isinstance(v, (int, float))]
    if len(present) < 2:
        return None

    return {
        "income": income if isinstance(income, (int, float)) else None,
        "expenses": expenses if isinstance(expenses, (int, float)) else None,
        "savings": savings if isinstance(savings, (int, float)) else None,
        "currency_symbol": data.get("currency_symbol") or "",
    }
