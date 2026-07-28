"""
app.py

AI Voice Assistant
------------------------------
A Streamlit application where an AI consultant named Ava, powered by the
Google Gemini API, conducts voice or text conversations with customers to
run different kinds of assessments (financial, business management,
health and wellness, sales, or a general needs assessment) and then
produces a written report at the end of the conversation.

Run locally with:
    streamlit run app.py

See README.md for full setup and deployment instructions.
"""

import os
import html
import streamlit as st

import theme
import report_files
import data_store
import charts
from assessments import ASSESSMENTS, get_assessment
from gemini_client import (
    get_client,
    send_chat_message,
    transcribe_audio,
    generate_report,
    extract_financial_metrics,
)
from voice_utils import text_to_speech


# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Ava - AI Voice Assistant",
    page_icon=None,
    layout="centered",
)


def render_message(role: str, text: str, accent: str):
    """Render one chat turn as a styled bubble instead of the default
    Streamlit chat avatar, so the color and monogram match the active
    assessment's accent."""
    safe_text = html.escape(text).replace("\n", "<br>")
    if role == "assistant":
        st.markdown(
            f"""
            <div class="chat-row chat-row-assistant">
                <div class="avatar-badge" style="background:{accent}">A</div>
                <div class="bubble bubble-assistant" style="border-left-color:{accent}">{safe_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row chat-row-user">
                <div class="avatar-badge avatar-user">C</div>
                <div class="bubble bubble-user">{safe_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_api_key() -> str:
    """Look for the Gemini API key in Streamlit secrets first, then in
    the environment, so the same code works locally and when deployed."""
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY", "")


# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "assessment_key" not in st.session_state:
    st.session_state.assessment_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report" not in st.session_state:
    st.session_state.report = None
if "report_edited" not in st.session_state:
    st.session_state.report_edited = None
if "report_chart" not in st.session_state:
    st.session_state.report_chart = None
if "voice_replies" not in st.session_state:
    st.session_state.voice_replies = True
if "session_code" not in st.session_state:
    st.session_state.session_code = data_store.generate_session_code()


def save_progress():
    """Auto-save the current conversation under this browser tab's code
    so it can be resumed later even after closing the browser."""
    data_store.save_session(
        st.session_state.session_code,
        st.session_state.assessment_key,
        st.session_state.messages,
        st.session_state.report,
    )


def start_new_assessment(key: str):
    st.session_state.assessment_key = key
    st.session_state.messages = []
    st.session_state.report = None
    st.session_state.report_edited = None
    st.session_state.report_chart = None


def reset_all():
    st.session_state.assessment_key = None
    st.session_state.messages = []
    st.session_state.report = None
    st.session_state.report_edited = None
    st.session_state.report_chart = None
    st.session_state.session_code = data_store.generate_session_code()


def resume_session(code: str) -> bool:
    """Load a previously saved session by its code. Returns True on success."""
    saved = data_store.load_session(code)
    if not saved:
        return False
    st.session_state.session_code = code.strip().upper()
    st.session_state.assessment_key = saved.get("assistant_key")
    st.session_state.messages = saved.get("messages", [])
    st.session_state.report = saved.get("report")
    st.session_state.report_edited = saved.get("report")
    st.session_state.report_chart = None
    return True


# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown(theme.sidebar_mark_html(), unsafe_allow_html=True)
    st.header("Assistant Setup")

    labels = {key: value["title"] for key, value in ASSESSMENTS.items()}
    options = list(labels.keys())

    current_index = 0
    if st.session_state.assessment_key in options:
        current_index = options.index(st.session_state.assessment_key)

    selected_key = st.selectbox(
        "Choose an assistant type",
        options=options,
        format_func=lambda key: labels[key],
        index=current_index,
    )

    st.caption(get_assessment(selected_key)["description"])

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Start", use_container_width=True):
            start_new_assessment(selected_key)
    with col_b:
        if st.button("Reset", use_container_width=True):
            reset_all()

    st.divider()
    st.session_state.voice_replies = st.toggle(
        "Speak Ava's replies out loud", value=st.session_state.voice_replies
    )

    st.divider()
    st.caption("Your progress is auto-saved under this code:")
    st.code(st.session_state.session_code, language=None)
    st.caption("Close the browser any time and come back to this exact code to resume.")

    with st.expander("Resume a saved session"):
        resume_code = st.text_input("Enter a session code", placeholder="AVA-7K3F")
        if st.button("Resume", use_container_width=True):
            if resume_session(resume_code):
                st.success("Session restored.")
                st.rerun()
            else:
                st.error("No saved session found for that code.")

    history_entries = data_store.load_history(st.session_state.assessment_key) if st.session_state.assessment_key else []
    if history_entries:
        with st.expander(f"Report history ({len(history_entries)})"):
            for i, entry in enumerate(history_entries[:10]):
                st.caption(f"{entry['generated_at'][:16].replace('T', ' ')}")
                st.download_button(
                    "Download",
                    data=entry["report_text"],
                    file_name=f"{entry['assistant_key']}_report_{entry['generated_at'][:10]}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"history_dl_{i}",
                )
                st.divider()

    st.divider()
    st.caption(
        "This tool provides general information only and does not replace "
        "advice from a licensed professional in finance, medicine, or law."
    )


# ----------------------------------------------------------------------
# Theme and header
# ----------------------------------------------------------------------
active_accent = theme.accent_for(st.session_state.assessment_key)
st.markdown(theme.inject_css(active_accent), unsafe_allow_html=True)

active_title = None
if st.session_state.assessment_key:
    active_title = get_assessment(st.session_state.assessment_key)["title"]
st.markdown(theme.header_html(active_title), unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Main area
# ----------------------------------------------------------------------
api_key = get_api_key()

if not api_key:
    st.error(
        "No Gemini API key found. Add GEMINI_API_KEY to "
        ".streamlit/secrets.toml or set it as an environment variable, "
        "then restart the app. See README.md for details."
    )
    st.stop()

client = get_client(api_key)

if not st.session_state.assessment_key:
    st.markdown(
        """
        <div class="ava-landing-intro">
            <p>Ava runs a short, natural conversation to understand your
            situation, then turns it into a written report you can keep.
            Pick a starting point below, or use the panel on the left.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    keys = list(ASSESSMENTS.keys())
    for row_start in range(0, len(keys), 2):
        cols = st.columns(2)
        for col, key in zip(cols, keys[row_start:row_start + 2]):
            info = get_assessment(key)
            card_accent = theme.accent_for(key)
            with col:
                st.markdown(
                    f"""
                    <div class="ava-card" style="--card-accent: {card_accent};">
                        <div class="ava-card-title">{info['title']}</div>
                        <div class="ava-card-desc">{info['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Start", key=f"landing_start_{key}", use_container_width=True):
                    start_new_assessment(key)
                    st.rerun()
    st.markdown(theme.footer_html(), unsafe_allow_html=True)
    st.stop()

assessment = get_assessment(st.session_state.assessment_key)

# Greet the customer the first time an assessment starts
if not st.session_state.messages:
    opening_line = (
        f"Hello, I am Ava, your {assessment['title']} today. There is no need "
        "to prepare anything, just answer naturally and we will go step by "
        "step. Whenever you feel ready, tell me a little about your current "
        "situation to get us started."
    )
    st.session_state.messages.append({"role": "assistant", "text": opening_line})
    save_progress()

# Render conversation so far
for turn in st.session_state.messages:
    render_message(turn["role"], turn["text"], active_accent)

# ----------------------------------------------------------------------
# Progress indicator
# ----------------------------------------------------------------------
user_turns = sum(1 for turn in st.session_state.messages if turn["role"] == "user")
progress_value = min(user_turns / 6, 1.0)
if user_turns == 0:
    stage_label = "Getting started"
elif user_turns < 3:
    stage_label = "Learning the basics"
elif user_turns < 6:
    stage_label = "Building a full picture"
else:
    stage_label = "Ready for your report"

st.markdown('<div class="ava-progress-wrap">', unsafe_allow_html=True)
st.markdown(theme.progress_html(stage_label, f"{user_turns} exchanges"), unsafe_allow_html=True)
st.progress(progress_value)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Voice input
# ----------------------------------------------------------------------
st.caption("Speak your answer or type it below.")
audio_value = st.audio_input("Record your answer")

user_text = None

if audio_value is not None:
    if st.button("Send recorded answer"):
        with st.spinner("Listening..."):
            audio_bytes = audio_value.getvalue()
            user_text = transcribe_audio(client, audio_bytes, mime_type="audio/wav")

# ----------------------------------------------------------------------
# Text input
# ----------------------------------------------------------------------
typed_text = st.chat_input("Type your answer instead")
if typed_text:
    user_text = typed_text

# ----------------------------------------------------------------------
# Handle a new customer turn
# ----------------------------------------------------------------------
if user_text:
    st.session_state.messages.append({"role": "user", "text": user_text})
    render_message("user", user_text, active_accent)

    with st.spinner("Ava is thinking..."):
        reply = send_chat_message(
            client=client,
            system_prompt=assessment["system_prompt"],
            history=st.session_state.messages,
        )
    render_message("assistant", reply, active_accent)
    if st.session_state.voice_replies:
        audio_bytes = text_to_speech(reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

    st.session_state.messages.append({"role": "assistant", "text": reply})
    save_progress()

# ----------------------------------------------------------------------
# Report generation
# ----------------------------------------------------------------------
st.divider()

if st.button("Generate final report", use_container_width=True):
    if len(st.session_state.messages) < 3:
        st.warning(
            "Have a bit more of the conversation first so Ava has "
            "enough information to write a useful report."
        )
    else:
        with st.spinner("Ava is writing the report..."):
            report_text = generate_report(
                client=client,
                system_prompt=assessment["system_prompt"],
                report_prompt=assessment["report_prompt"],
                history=st.session_state.messages,
            )
        st.session_state.report = report_text
        st.session_state.report_edited = report_text

        # Only the Financial Assistant has numbers regular enough to chart
        # honestly. Other assistant types skip this rather than force a
        # chart onto qualitative conversations.
        chart_bytes = None
        if st.session_state.assessment_key == "finance":
            with st.spinner("Looking for numbers to chart..."):
                metrics = extract_financial_metrics(client, st.session_state.messages)
                if metrics:
                    chart_bytes = charts.build_financial_bar_chart(metrics)
        st.session_state.report_chart = chart_bytes

        data_store.append_history(
            st.session_state.assessment_key, assessment["title"], report_text
        )
        save_progress()

if st.session_state.report:
    st.markdown('<div class="ava-section-title">Assistant Report</div>', unsafe_allow_html=True)

    if st.session_state.report_chart:
        st.image(st.session_state.report_chart, use_container_width=True)

    safe_report = html.escape(st.session_state.report).replace("\n", "<br>")
    st.markdown(f'<div class="ava-report-card">{safe_report}</div>', unsafe_allow_html=True)

    with st.expander("Edit report text before downloading"):
        st.session_state.report_edited = st.text_area(
            "Report text",
            value=st.session_state.report_edited or st.session_state.report,
            height=260,
            label_visibility="collapsed",
        )
        st.caption("Downloads below use this edited text.")

    final_text = st.session_state.report_edited or st.session_state.report

    st.caption("Download this report:")
    txt_col, pdf_col, docx_col = st.columns(3)

    file_stub = f"{st.session_state.assessment_key}_assistant_report"

    with txt_col:
        st.download_button(
            "Text file",
            data=final_text,
            file_name=f"{file_stub}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with pdf_col:
        pdf_bytes = report_files.build_pdf_bytes(
            final_text, assessment["title"], chart_image_bytes=st.session_state.report_chart
        )
        st.download_button(
            "PDF",
            data=pdf_bytes,
            file_name=f"{file_stub}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with docx_col:
        docx_bytes = report_files.build_docx_bytes(
            final_text, assessment["title"], chart_image_bytes=st.session_state.report_chart
        )
        st.download_button(
            "Word document",
            data=docx_bytes,
            file_name=f"{file_stub}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

st.markdown(theme.footer_html(), unsafe_allow_html=True)
