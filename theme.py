"""
theme.py

Visual identity for the AI Voice Assistant.

Design idea: the interface tints itself to match the kind of conversation
Ava is having. Each assessment type has its own accent color, which shows
up in the header badge, the sidebar, the buttons, and the left edge of
Ava's chat bubbles. Everything else stays quiet: one warm neutral
background, one ink text color, one pair of typefaces.

Palette
    ink       #1C2B33   primary text, dark surfaces
    paper     #F8F7F3   page background
    panel     #FFFFFF   cards, sidebar
    hairline  #E3E0D8   borders and dividers
    slate     #5B6B74   secondary text

    accent - finance    #2E6B65   deep teal
    accent - business   #4C5B8A   slate indigo
    accent - health     #5B8C5A   sage green
    accent - sales      #B67B3D   warm ochre
    accent - general    #7C6A96   muted plum
    accent - default    #3A4750   neutral ink blue, used before a topic is chosen
"""

INK = "#1C2B33"
PAPER = "#EFECE2"
PANEL = "#FFFFFF"
HAIRLINE = "#E3E0D8"
SLATE = "#5B6B74"

ACCENTS = {
    "finance": "#2E6B65",
    "business": "#4C5B8A",
    "health": "#5B8C5A",
    "sales": "#B67B3D",
    "general": "#7C6A96",
}
DEFAULT_ACCENT = "#3A4750"


def accent_for(assessment_key: str | None) -> str:
    if not assessment_key:
        return DEFAULT_ACCENT
    return ACCENTS.get(assessment_key, DEFAULT_ACCENT)


def inject_css(accent: str) -> str:
    """Return a <style> block, parameterized by the current accent color."""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

:root {{
    --ink: {INK};
    --paper: {PAPER};
    --panel: {PANEL};
    --hairline: {HAIRLINE};
    --slate: {SLATE};
    --accent: {accent};
}}

/* base page */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: var(--ink);
}}
[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(1100px 550px at 12% -8%, color-mix(in srgb, var(--accent) 14%, transparent), transparent 60%),
        linear-gradient(180deg, #F4F1E7 0%, #E9E5D8 100%);
    background-attachment: fixed;
}}
[data-testid="stHeader"] {{
    background: transparent;
}}

/* hide default streamlit chrome padding at top so our header sits flush */
[data-testid="stMainBlockContainer"] {{
    padding-top: 1.5rem;
    max-width: 760px;
}}

/* our custom top band */
.ava-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.4rem;
    background: var(--ink);
    border-radius: 14px;
    margin-bottom: 1.6rem;
}}
.ava-header-left {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
}}
.ava-mark {{
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}
.ava-mark svg {{ display: block; }}
.ava-wordmark {{
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 1.35rem;
    color: var(--paper);
    line-height: 1.1;
}}
.ava-tagline {{
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9FB0B6;
    margin-top: 2px;
}}
.ava-mode-badge {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--ink);
    background: var(--accent);
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    white-space: nowrap;
}}

/* headings */
h1, h2, h3, .ava-section-title {{
    font-family: 'Source Serif 4', serif !important;
    color: var(--ink) !important;
}}

/* sidebar */
[data-testid="stSidebar"] {{
    background: var(--panel);
    border-right: 1px solid var(--hairline);
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    font-family: 'Source Serif 4', serif !important;
}}

/* buttons */
.stButton > button, .stDownloadButton > button {{
    background: var(--ink);
    color: var(--paper);
    border: none;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    transition: background 0.15s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background: var(--accent);
    color: var(--ink);
}}

/* select box */
[data-baseweb="select"] {{
    border-radius: 8px !important;
}}

/* chat bubbles (custom markup rendered in app.py) */
.chat-row {{
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.9rem;
}}
.chat-row-user {{
    flex-direction: row-reverse;
}}
.avatar-badge {{
    width: 30px;
    height: 30px;
    min-width: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--paper);
    background: var(--accent);
}}
.avatar-user {{
    background: var(--slate);
}}
.bubble {{
    padding: 0.7rem 1rem;
    border-radius: 10px;
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 80%;
}}
.bubble-assistant {{
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--accent);
}}
.bubble-user {{
    background: #EFEDE7;
    color: var(--ink);
}}

/* report card */
.ava-report-card {{
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-top: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-top: 0.6rem;
}}

/* small caption / disclaimer text */
.ava-caption {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--slate);
}}

/* landing screen intro */
.ava-landing-intro {{
    margin-bottom: 1.4rem;
}}
.ava-landing-intro p {{
    color: var(--slate);
    font-size: 0.98rem;
    line-height: 1.6;
    max-width: 46rem;
}}

/* assessment picker cards on the landing screen */
.ava-card {{
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-left: 4px solid var(--card-accent, var(--accent));
    border-radius: 10px;
    padding: 1.1rem 1.2rem 0.4rem 1.2rem;
    margin-bottom: 0.9rem;
    height: 100%;
}}
.ava-card-title {{
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--ink);
    margin-bottom: 0.35rem;
}}
.ava-card-desc {{
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--slate);
    line-height: 1.5;
    margin-bottom: 0.7rem;
}}

/* progress indicator during a conversation */
.ava-progress-wrap {{
    margin: 0.2rem 0 1.1rem 0;
}}
.ava-progress-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.35rem;
    display: flex;
    justify-content: space-between;
}}
[data-testid="stProgress"] > div > div > div {{
    background-color: var(--accent) !important;
}}
[data-testid="stProgress"] > div > div {{
    background-color: var(--hairline) !important;
}}

/* sidebar polish */
[data-testid="stSidebar"] .block-container {{
    padding-top: 1.6rem;
}}
.ava-sidebar-mark {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.2rem;
}}
.ava-sidebar-mark .ava-mark {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
}}
.ava-sidebar-mark span {{
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--ink);
}}
[data-testid="stSidebar"] hr {{
    border-color: var(--hairline);
    margin: 1.1rem 0;
}}

/* footer credit line */
.ava-footer {{
    margin-top: 2.4rem;
    padding-top: 1rem;
    border-top: 1px solid var(--hairline);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--slate);
}}
.ava-footer a {{
    color: var(--accent);
    text-decoration: none;
}}
.ava-footer a:hover {{
    text-decoration: underline;
}}
</style>
"""


def sidebar_mark_html() -> str:
    """Small logo mark shown at the top of the sidebar, echoing the header."""
    mark_svg = (
        '<svg width="14" height="14" viewBox="0 0 16 16" fill="none">'
        '<rect x="1" y="6" width="2" height="4" rx="1" fill="#F8F7F3"/>'
        '<rect x="5" y="3" width="2" height="10" rx="1" fill="#F8F7F3"/>'
        '<rect x="9" y="1" width="2" height="14" rx="1" fill="#F8F7F3"/>'
        '<rect x="13" y="5" width="2" height="6" rx="1" fill="#F8F7F3"/>'
        "</svg>"
    )
    return f"""
<div class="ava-sidebar-mark">
    <div class="ava-mark">{mark_svg}</div>
    <span>Ava</span>
</div>
"""


def progress_html(label: str, right_label: str) -> str:
    return f"""
<div class="ava-progress-label"><span>{label}</span><span>{right_label}</span></div>
"""


def footer_html() -> str:
    return """
<div class="ava-footer">
    <span>Built by Khan Zaid</span>
    <span>&middot;</span>
    <a href="mailto:khanzack355@gmail.com">khanzack355@gmail.com</a>
</div>
"""


def header_html(mode_label: str | None) -> str:
    """Return the HTML for the top band, showing the active assessment mode."""
    badge = f'<div class="ava-mode-badge">{mode_label}</div>' if mode_label else ""
    mark_svg = (
        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none">'
        '<rect x="1" y="6" width="2" height="4" rx="1" fill="#F8F7F3"/>'
        '<rect x="5" y="3" width="2" height="10" rx="1" fill="#F8F7F3"/>'
        '<rect x="9" y="1" width="2" height="14" rx="1" fill="#F8F7F3"/>'
        '<rect x="13" y="5" width="2" height="6" rx="1" fill="#F8F7F3"/>'
        "</svg>"
    )
    return f"""
<div class="ava-header">
    <div class="ava-header-left">
        <div class="ava-mark">{mark_svg}</div>
        <div>
            <div class="ava-wordmark">Ava</div>
            <div class="ava-tagline">AI Voice Assistant</div>
        </div>
    </div>
    {badge}
</div>
"""
