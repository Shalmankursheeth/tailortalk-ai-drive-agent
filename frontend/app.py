"""
TailorTalk — Streamlit Frontend
Premium chat UI for the Google Drive AI Agent.
"""

import streamlit as st
import requests
import os
import re

st.set_page_config(
    page_title="TailorTalk • Drive Assistant",
    page_icon="🗂️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://tailortalk-ai-drive-agent.onrender.com/")

# ── Session state ─────────────────────────────────────────────────────────────
for _k, _v in [("messages", []), ("is_processing", False), ("input_key", 0)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #06070f; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── HEADER ── */
.tt-header {
  text-align: center;
  padding: 2.4rem 1rem 0.6rem;
}
.tt-brand {
  display: inline-flex;
  align-items: center;
  gap: 13px;
  margin-bottom: 8px;
}
.tt-icon {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem;
  box-shadow: 0 0 28px rgba(99,102,241,0.5);
}
.tt-name {
  font-family: 'Syne', sans-serif;
  font-weight: 800; font-size: 1.8rem;
  background: linear-gradient(130deg, #a5b4fc 0%, #e0e7ff 60%, #c4b5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.03em;
}
.tt-sub {
  color: #353760;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-weight: 600;
  margin-bottom: 1.6rem;
}
.tt-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #1c1e30 50%, transparent 100%);
  margin: 0 0 1.6rem;
}

/* ── WELCOME CARD ── */
.welcome-card {
  background: linear-gradient(145deg, #0d0e1c 0%, #0a0b16 100%);
  border: 1px solid #191b2e;
  border-radius: 18px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.welcome-card h3 {
  color: #3d4070;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 600;
  margin-bottom: 1.2rem;
}
.chip-grid {
  display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
}
.chip {
  background: #0f1022;
  border: 1px solid #212440;
  border-radius: 22px;
  padding: 7px 15px;
  font-size: 0.79rem;
  color: #6366f1;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.chip:hover { background: #141629; border-color: #6366f1; }

/* ── CHAT MESSAGES ── */
.chat-wrap {
  display: flex; flex-direction: column; gap: 6px;
  margin-bottom: 1.2rem;
}

/* User bubble */
.user-row { display: flex; justify-content: flex-end; margin: 3px 0; }
.user-bubble {
  background: linear-gradient(140deg, #2d2a7a 0%, #1a1754 100%);
  border: 1px solid rgba(99,102,241,0.28);
  border-radius: 20px 20px 5px 20px;
  padding: 11px 17px;
  max-width: 78%;
  color: #c7d2fe;
  font-size: 0.91rem;
  line-height: 1.58;
  word-break: break-word;
  box-shadow: 0 2px 12px rgba(99,102,241,0.12);
}

/* AI bubble */
.ai-row {
  display: flex;
  justify-content: flex-start;
  align-items: flex-end;
  gap: 9px;
  margin: 3px 0;
}
.ai-avatar {
  width: 30px; height: 30px; min-width: 30px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.78rem;
  margin-bottom: 2px;
  box-shadow: 0 2px 10px rgba(99,102,241,0.35);
}
.ai-bubble {
  background: #0c0d1c;
  border: 1px solid #181a2e;
  border-radius: 20px 20px 20px 5px;
  padding: 12px 17px;
  max-width: 83%;
  color: #cac8e0;
  font-size: 0.91rem;
  line-height: 1.7;
  word-break: break-word;
}
.ai-bubble a {
  color: #818cf8;
  text-decoration: none;
  font-weight: 500;
}
.ai-bubble a:hover { text-decoration: underline; }
.ai-bubble strong { color: #a5b4fc; font-weight: 600; }
.ai-bubble code {
  background: #111328;
  border: 1px solid #252850;
  border-radius: 5px;
  padding: 1px 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.81rem;
  color: #7dd3fc;
}

/* ── FILE CARDS (rendered inside .ai-bubble) ── */
.file-card {
  background: #111326;
  border: 1px solid #1f2240;
  border-radius: 14px;
  padding: 14px 16px;
  margin-top: 10px;
  transition: border-color 0.18s, transform 0.15s;
}
.file-card:hover {
  border-color: #6366f1;
  transform: translateY(-2px);
}
.file-row {
  display: flex;
  align-items: center;
  gap: 13px;
}
.file-emoji {
  width: 44px; height: 44px; min-width: 44px;
  background: linear-gradient(135deg, #1e1f3a, #252660);
  border: 1px solid #2a2d55;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.file-info { flex: 1; min-width: 0; }
.file-name {
  color: #dde4ff;
  font-weight: 600;
  font-size: 0.92rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.file-type {
  color: #4d5180;
  font-size: 0.77rem;
  margin-top: 3px;
}
.file-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 13px;
}
.file-date { color: #3d4070; font-size: 0.75rem; }
.open-btn {
  background: linear-gradient(135deg, #6366f1, #7c3aed);
  color: #fff !important;
  text-decoration: none !important;
  padding: 7px 14px;
  border-radius: 9px;
  font-size: 0.79rem;
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(99,102,241,0.3);
  transition: opacity 0.15s;
  white-space: nowrap;
}
.open-btn:hover { opacity: 0.88; }
.files-header {
  color: #3d4070;
  font-size: 0.77rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 4px;
}

/* ── TYPING INDICATOR ── */
.typing-row {
  display: flex; align-items: flex-end; gap: 9px; margin: 3px 0;
}
.typing-bubble {
  background: #0c0d1c;
  border: 1px solid #181a2e;
  border-radius: 20px 20px 20px 5px;
  padding: 13px 18px;
  display: flex; gap: 6px; align-items: center;
}
.dot {
  width: 7px; height: 7px;
  background: #6366f1; border-radius: 50%;
  animation: blink 1.2s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%,80%,100% { opacity: 0.15; transform: scale(0.85); }
  40%          { opacity: 1;    transform: scale(1.2);  }
}

/* ── INPUT BAR ── */
[data-testid="stTextInput"] > div > div {
  background: #0c0d1c !important;
  border: 1.5px solid #1a1c30 !important;
  border-radius: 14px !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] > div > div:focus-within {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.14) !important;
}
[data-testid="stTextInput"] input {
  color: #ddd8f8 !important;
  font-size: 0.92rem !important;
  background: transparent !important;
  border: none !important;
  padding: 0.76rem 1.1rem !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input::placeholder { color: #272a48 !important; }

.stButton > button {
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-size: 0.86rem !important;
  letter-spacing: 0.01em !important;
  transition: opacity 0.15s, transform 0.1s !important;
}
.stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

/* ── FOOTER ── */
.tt-footer {
  text-align: center;
  color: #1a1c2e;
  font-size: 0.7rem;
  margin-top: 1.2rem;
  padding-bottom: 0.8rem;
  letter-spacing: 0.06em;
}
            .ai-row {
  display: flex;
  justify-content: flex-start;
  align-items: flex-end;
  gap: 9px;
  margin: 8px 0;
}

.ai-avatar {
  width: 30px;
  height: 30px;
  min-width: 30px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
}

.ai-bubble {
  background: #0c0d1c;
  border: 1px solid #181a2e;
  border-radius: 20px 20px 20px 5px;
  padding: 12px 17px;
  max-width: 83%;
  color: #cac8e0;
  font-size: 0.91rem;
  line-height: 1.7;
}

.file-card {
  background: #111326;
  border: 1px solid #1f2240;
  border-radius: 14px;
  padding: 14px 16px;
  margin-top: 10px;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 13px;
}

.file-emoji {
  width: 44px;
  height: 44px;
  min-width: 44px;
  background: linear-gradient(135deg, #1e1f3a, #252660);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.file-name {
  color: #dde4ff;
  font-weight: 600;
  font-size: 0.92rem;
}

.file-type {
  color: #4d5180;
  font-size: 0.77rem;
}

.file-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 13px;
}

.open-btn {
  background: linear-gradient(135deg, #6366f1, #7c3aed);
  color: white !important;
  text-decoration: none !important;
  padding: 7px 14px;
  border-radius: 9px;
  font-size: 0.79rem;
  font-weight: 600;
}

</style>

""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

MIME_EMOJI = {
    "📄 PDF": "📄",
    "📝 Google Doc": "📝",
    "📊 Google Sheet": "📊",
    "📑 Google Slides": "📑",
    "📁 Folder": "📁",
    "🖼️ JPEG Image": "🖼️",
    "🖼️ PNG Image": "🖼️",
    "📃 Text File": "📃",
    "📄 Word Doc": "📄",
    "📊 Excel File": "📊",
    "📑 PowerPoint": "📑",
    "🗜️ ZIP Archive": "🗜️",
}


def get_emoji(type_label: str) -> str:
    for key, emoji in MIME_EMOJI.items():
        if key in type_label or type_label.startswith(emoji):
            return emoji
    return "📎"


def md_to_html(text: str) -> str:
    """Convert markdown subset to safe HTML."""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Markdown links
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',
        r'<a href="\2" target="_blank">\1</a>',
        text
    )
    # Bare URLs not already wrapped
    text = re.sub(
        r'(?<!["\(])(https?://[^\s<>"]+)',
        r'<a href="\1" target="_blank">\1</a>',
        text
    )
    text = text.replace('\n', '<br>')
    return text


def parse_file_cards(text: str) -> list[dict] | None:
    """
    Parse the agent's markdown response into a list of file dicts.
    Returns None if the response doesn't contain file listings.
    """
    # Detect if the response has a file listing pattern
    if "**" not in text or ("Open in Drive" not in text and "🔗" not in text):
        return None

    files = []
    # Split on double newlines to get file blocks
    blocks = re.split(r'\n{2,}', text.strip())

    current = {}
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        for line in lines:
            # Skip header like "Found N file(s):"
            if re.match(r'^Found \*\*\d+', line):
                continue
            # File name line: **Name**
            m = re.match(r'^\*\*(.+?)\*\*$', line)
            if m:
                if current.get("name"):
                    files.append(current)
                current = {"name": m.group(1), "type": "", "modified": "", "link": ""}
                continue
            # Type + date line: emoji Type · Modified: date
            if "·" in line and not line.startswith("["):
                parts = line.split("·")
                if parts:
                    current["type"] = parts[0].strip()
                for p in parts:
                    if "Modified:" in p:
                        current["modified"] = p.replace("Modified:", "").strip()
                continue
            # Link line
            link_m = re.search(r'\[.*?\]\((https?://[^\)]+)\)', line)
            if link_m:
                current["link"] = link_m.group(1)

    if current.get("name"):
        files.append(current)

    return files if files else None


def render_message(content: str) -> str:
    """
    Render an assistant message as either premium file cards
    or a standard markdown bubble.
    """
    files = parse_file_cards(content)

    if files:
        count_line = ""
        m = re.search(r'Found \*\*(\d+) file', content)
        count = m.group(1) if m else str(len(files))
        header = (
            f'<div class="files-header">🗂 {count} file{"s" if int(count) != 1 else ""} found</div>'
        )
        cards = ""
        for f in files:
            emoji = get_emoji(f.get("type", ""))
            name  = f.get("name", "Unknown")
            ftype = f.get("type", "File")
            date  = f.get("modified", "")
            link  = f.get("link", "#")

            open_part = (
                f'<a href="{link}" target="_blank" class="open-btn">Open ↗</a>'
                if link and link != "#"
                else '<span style="color:#3d4070;font-size:0.78rem">No link</span>'
            )

            cards += f"""
<div class="file-card">
  <div class="file-row">
    <div class="file-emoji">{emoji}</div>
    <div class="file-info">
      <div class="file-name">{name}</div>
      <div class="file-type">{ftype}</div>
    </div>
  </div>
  <div class="file-footer">
    <div class="file-date">{date}</div>
    {open_part}
  </div>
</div>"""

        return header + cards

    # Plain text / markdown response
    return md_to_html(content)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tt-header">
  <div class="tt-brand">
    <div class="tt-icon">🗂</div>
    <span class="tt-name">TailorTalk</span>
  </div>
  <div class="tt-sub">AI-Powered Google Drive Discovery</div>
</div>
<div class="tt-divider"></div>
""", unsafe_allow_html=True)

SUGGESTIONS = [
    ("📄", "Show all PDFs"),
    ("💰", "Find finance files"),
    ("🖼️", "List all images"),
    ("📊", "Find spreadsheets"),
    ("📝", "Show Google Docs"),
    ("🕐", "Files from this year"),
]

# ── Welcome state ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    chips = "".join(f'<span class="chip">{i} {l}</span>' for i, l in SUGGESTIONS)
    st.markdown(
        f'<div class="welcome-card"><h3>Try asking about your Drive</h3>'
        f'<div class="chip-grid">{chips}</div></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for idx, (icon, label) in enumerate(SUGGESTIONS):
        if cols[idx % 3].button(f"{icon} {label}", key=f"sug_{idx}"):
            st.session_state.pending_msg = label
            st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
if st.session_state.messages:
    parts = ['<div class="chat-wrap">']

    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]

        if role == "user":
            parts.append(
                f'<div class="user-row">'
                f'<div class="user-bubble">{content}</div>'
                f'</div>'
            )
        else:
            rendered = render_message(content)
            parts.append(
                f'<div class="ai-row">'
                f'<div class="ai-avatar">🤖</div>'
                f'<div class="ai-bubble">{rendered}</div>'
                f'</div>'
            )

    if st.session_state.is_processing:
        parts.append(
            '<div class="typing-row">'
            '<div class="ai-avatar">🤖</div>'
            '<div class="typing-bubble">'
            '<div class="dot"></div>'
            '<div class="dot"></div>'
            '<div class="dot"></div>'
            '</div></div>'
        )

    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

# ── Handle suggestion click ───────────────────────────────────────────────────
if "pending_msg" in st.session_state and not st.session_state.is_processing:
    pending = st.session_state.pop("pending_msg")
    st.session_state.messages.append({"role": "user", "content": pending})
    st.session_state.is_processing = True
    st.session_state.pending_api_call = pending
    st.rerun()

# ── Execute API call ──────────────────────────────────────────────────────────
if st.session_state.is_processing and "pending_api_call" in st.session_state:
    user_msg = st.session_state.pop("pending_api_call")
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_msg, "history": st.session_state.messages[:-1]},
            timeout=60,
        )
        answer = (
            resp.json().get("response", "No response.")
            if resp.status_code == 200
            else f"⚠️ Backend error {resp.status_code}"
        )
    except requests.exceptions.ConnectionError:
        answer = (
            "⚠️ **Cannot connect to backend.**\n\n"
            "Make sure FastAPI is running:\n"
            "`uvicorn main:app --reload --port 8000`"
        )
    except requests.exceptions.Timeout:
        answer = "⚠️ Request timed out. The Drive search took too long — try again."
    except Exception as e:
        answer = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.is_processing = False
    st.rerun()

# ── Input bar ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
in_col, send_col, clr_col = st.columns([6, 1.3, 0.9])

with in_col:
    user_input = st.text_input(
        "msg",
        placeholder="Find financial reports, list PDFs, search invoices…",
        label_visibility="collapsed",
        key=f"input_{st.session_state.input_key}",
        disabled=st.session_state.is_processing,
    )

with send_col:
    send_clicked = st.button(
        "Send ↑",
        disabled=st.session_state.is_processing,
        key="send_btn",
        use_container_width=True,
    )

with clr_col:
    if st.button("🗑", key="clr_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_processing = False
        st.session_state.input_key += 1
        st.rerun()

if send_clicked and user_input and user_input.strip() and not st.session_state.is_processing:
    msg = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": msg})
    st.session_state.is_processing = True
    st.session_state.pending_api_call = msg
    st.session_state.input_key += 1
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tt-footer">TailorTalk · LangGraph + LangChain + Groq · Google Drive API v3</div>',
    unsafe_allow_html=True,
)
import re


def parse_file_cards(text):

    if "**" not in text:
        return None

    files = []

    blocks = re.split(r'\n{2,}', text.strip())

    current = {}

    for block in blocks:

        lines = [
            l.strip()
            for l in block.strip().splitlines()
            if l.strip()
        ]

        for line in lines:

            m = re.match(r'^\*\*(.+?)\*\*$', line)

            if m:

                if current.get("name"):
                    files.append(current)

                current = {
                    "name": m.group(1),
                    "type": "",
                    "modified": "",
                    "link": ""
                }

                continue

            if "Modified:" in line:
                current["modified"] = (
                    line.replace("Modified:", "")
                    .strip()
                )

            if "PDF" in line:
                current["type"] = "📄 PDF"

            if "Spreadsheet" in line:
                current["type"] = "📊 Spreadsheet"

            link_match = re.search(
                r'\((https?://[^\)]+)\)',
                line
            )

            if link_match:
                current["link"] = link_match.group(1)

    if current.get("name"):
        files.append(current)

    return files if files else None



def render_ai_message(content):

    files = parse_file_cards(content)

    if not files:

        return f'''
        <div class="ai-row">
            <div class="ai-avatar">🤖</div>

            <div class="ai-bubble">
                {content}
            </div>
        </div>
        '''

    cards = ""

    for f in files:

        cards += f"""
        <div class="file-card">

            <div class="file-row">

                <div class="file-emoji">
                    📄
                </div>

                <div>
                    <div class="file-name">
                        {f['name']}
                    </div>

                    <div class="file-type">
                        {f['type']}
                    </div>
                </div>

            </div>

            <div class="file-footer">

                <div>
                    {f['modified']}
                </div>

                <a
                    href="{f['link']}"
                    target="_blank"
                    class="open-btn"
                >
                    Open ↗
                </a>

            </div>

        </div>
        """

    return f'''
    <div class="ai-row">

        <div class="ai-avatar">
            🤖
        </div>

        <div class="ai-bubble">

            {cards}

        </div>

    </div>
    '''
