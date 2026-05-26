import os

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from summarizer_core import compute_stats, generate_summary, get_source_text


load_dotenv()

APP_TITLE = "AI Content Summarizer"


def init_state() -> None:
    defaults = {
        "summary": "",
        "source_text": "",
        "input_mode": "Paste Text",
        "style": "Short",
        "tone": "Professional",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_all() -> None:
    for key in [
        "summary",
        "source_text",
        "text_input",
        "url_input",
        "uploaded_file",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def render_copy_button(summary_text: str) -> None:
    escaped = (
        summary_text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )
    components.html(
        f"""
        <div style="margin-top: 6px;">
          <button
            onclick="navigator.clipboard.writeText(`{escaped}`); this.innerText='Copied ✅'; setTimeout(() => this.innerText='Copy Result', 1400);"
            style="
                width: 100%;
                background: #f3f4f6;
                color: #111827;
                border: 1px solid #d1d5db;
                padding: 0.5rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-weight: 600;
            "
          >
            Copy Result
          </button>
        </div>
        """,
        height=52,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")
    init_state()

    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.1rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            color: #6b7280;
            margin-bottom: 1.5rem;
        }
        .card {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1rem;
            background: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='main-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Summarize pasted text, uploaded files, or web pages with customizable style and tone.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Input")

        mode = st.radio(
            "Choose input source",
            ["Paste Text", "Upload File", "Website URL"],
            horizontal=True,
            key="input_mode",
        )

        text_input = ""
        uploaded_file = None
        url_input = ""

        if mode == "Paste Text":
            text_input = st.text_area(
                "Paste your text",
                height=280,
                placeholder="Paste article, notes, report, transcript, etc.",
                key="text_input",
            )
        elif mode == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload a .txt or .pdf file",
                type=["txt", "pdf"],
                key="uploaded_file",
            )
            st.caption("Tip: Large files may take a bit longer to process.")
        else:
            url_input = st.text_input(
                "Enter webpage URL",
                placeholder="https://example.com/article",
                key="url_input",
            )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            style = st.selectbox(
                "Summary style",
                ["Short", "Detailed", "Bullet Points"],
                key="style",
            )
        with c2:
            tone = st.selectbox(
                "Tone",
                ["Professional", "Simple", "Academic", "Casual"],
                key="tone",
            )

        b1, b2 = st.columns(2)
        with b1:
            generate_clicked = st.button(
                "Generate Summary", type="primary", use_container_width=True
            )
        with b2:
            clear_clicked = st.button("Clear Everything", use_container_width=True)

        if clear_clicked:
            clear_all()

        if generate_clicked:
            try:
                source_text = get_source_text(mode, text_input, uploaded_file, url_input)
                st.session_state["source_text"] = source_text

                with st.spinner("Generating summary with Groq..."):
                    summary = generate_summary(source_text, style, tone)

                if not summary:
                    raise RuntimeError("Received an empty summary from Groq.")
                st.session_state["summary"] = summary
                st.success("Summary generated successfully.")
            except Exception as exc:
                st.error(str(exc))

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Summary")

        summary_text = st.session_state.get("summary", "")
        source_text = st.session_state.get("source_text", "")

        if summary_text:
            st.text_area("Generated summary", value=summary_text, height=320)

            s1, s2 = st.columns(2)
            with s1:
                st.download_button(
                    "Download as .txt",
                    data=summary_text.encode("utf-8"),
                    file_name="summary.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with s2:
                render_copy_button(summary_text)

            ow, sw, oc, sc, reduction = compute_stats(source_text, summary_text)
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Original words", f"{ow:,}")
            m2.metric("Summary words", f"{sw:,}")
            m3.metric("Word reduction", f"{reduction:.1f}%")

            n1, n2 = st.columns(2)
            n1.metric("Original characters", f"{oc:,}")
            n2.metric("Summary characters", f"{sc:,}")
        else:
            st.info("Your summary will appear here after generation.")

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
