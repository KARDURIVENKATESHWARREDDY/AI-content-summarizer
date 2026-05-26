# AI Content Summarizer (Streamlit + Groq)

A beginner-friendly web app that summarizes content from:

- Pasted text
- Uploaded `.txt` / `.pdf` files
- Website URLs

You can choose summary **style** (Short, Detailed, Bullet Points) and **tone** (Professional, Simple, Academic, Casual), then view useful compression stats.

## Features

- Groq-powered summarization
- Multiple input methods (text/file/url)
- Summary style and tone controls
- Stats:
  - Original word count
  - Summary word count
  - Original character count
  - Summary character count
  - Percentage reduction
- Actions:
  - Generate summary
  - Clear everything
  - Copy result
  - Download summary as `.txt`
- Error handling for:
  - Missing API key
  - Empty input
  - Bad/unreadable PDF
  - Unreachable/unreadable website

## Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your env file from the sample:

```bash
copy .env.example .env
```

4. Add your Groq key to `.env`:

```env
GROQ_API_KEY=your_real_groq_api_key
```

## Run the app

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## Streamlit Cloud Deploy (Fix for GitHub URL Error)

If Streamlit shows this error:

> "The field needs to contain a Github URL pointing to a .py file"

Use the **app file URL** (not just repo URL) in the GitHub URL field:

`https://github.com/KARDURIVENKATESHWARREDDY/AI-content-summarizer/blob/main/streamlit_app.py`

Alternative app file URL:

`https://github.com/KARDURIVENKATESHWARREDDY/AI-content-summarizer/blob/main/app.py`

Also set secrets in Streamlit Cloud:

```toml
GROQ_API_KEY="your_real_groq_api_key"
```

## Notes

- Default model used in the app: `llama-3.1-8b-instant`
- If a URL fails, verify the site is publicly accessible and not blocking requests.
- Scanned/image PDFs may not contain extractable text.

# AI-content-summarizer 
