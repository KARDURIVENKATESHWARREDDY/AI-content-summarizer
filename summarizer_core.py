import os
from io import BytesIO
from typing import Tuple

import requests
from bs4 import BeautifulSoup
from groq import Groq
from pypdf import PdfReader

MODEL_NAME = "llama-3.1-8b-instant"


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY. Add it to your .env file or environment variables."
        )
    return Groq(api_key=api_key)


def read_txt_file(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


def read_pdf_file(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        text = "\n".join(text_parts).strip()
        if not text:
            raise ValueError("PDF appears empty or contains non-extractable text.")
        return text
    except Exception as exc:
        raise ValueError(f"Could not read PDF file: {exc}") from exc


def fetch_website_text(url: str, timeout: int = 12) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.extract()

        raw = soup.get_text(separator=" ")
        cleaned = " ".join(raw.split())

        if not cleaned:
            raise ValueError("No readable text found on this webpage.")
        return cleaned
    except Exception as exc:
        raise ValueError(f"Could not fetch website content: {exc}") from exc


def summarization_prompt(style: str, tone: str, content: str) -> str:
    style_map = {
        "Short": "Write a concise summary in 3-5 sentences.",
        "Detailed": "Write a detailed summary with key context and important nuances.",
        "Bullet Points": "Summarize the content into clear bullet points.",
    }
    style_instruction = style_map.get(style, style_map["Short"])

    return (
        "You are a helpful summarization assistant. "
        f"{style_instruction} "
        f"Use a {tone.lower()} tone. "
        "Focus on clarity and preserve factual meaning. "
        "Do not include meta-commentary like 'here is the summary'.\n\n"
        f"CONTENT:\n{content}"
    )


def generate_summary(content: str, style: str, tone: str) -> str:
    client = get_groq_client()
    prompt = summarization_prompt(style=style, tone=tone, content=content)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You summarize content clearly and accurately.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=700,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        raise RuntimeError(f"Groq API request failed: {exc}") from exc


def compute_stats(original: str, summary: str) -> Tuple[int, int, int, int, float]:
    original_words = len(original.split())
    summary_words = len(summary.split())
    original_chars = len(original)
    summary_chars = len(summary)

    if original_words == 0:
        reduction = 0.0
    else:
        reduction = ((original_words - summary_words) / original_words) * 100

    return original_words, summary_words, original_chars, summary_chars, reduction


def get_source_text(mode: str, pasted_text: str, uploaded_file, url: str) -> str:
    if mode == "Paste Text":
        if not pasted_text.strip():
            raise ValueError("Please paste some text to summarize.")
        return pasted_text.strip()

    if mode == "Upload File":
        if uploaded_file is None:
            raise ValueError("Please upload a .txt or .pdf file.")

        file_bytes = uploaded_file.read()
        if not file_bytes:
            raise ValueError("Uploaded file is empty.")

        name = uploaded_file.name.lower()
        if name.endswith(".txt"):
            text = read_txt_file(file_bytes)
        elif name.endswith(".pdf"):
            text = read_pdf_file(file_bytes)
        else:
            raise ValueError("Unsupported file type. Please upload only .txt or .pdf.")

        if not text.strip():
            raise ValueError("No readable text found in the uploaded file.")
        return text.strip()

    if mode == "Website URL":
        url = url.strip()
        if not url:
            raise ValueError("Please enter a website URL.")
        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"
        return fetch_website_text(url)

    raise ValueError("Invalid input mode selected.")

