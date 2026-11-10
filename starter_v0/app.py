"""Streamlit UI for the Research Agent (AI-Native UI design system).

Chay tu thu muc starter_v0/:
    streamlit run app.py

Logic agent tai su dung tu chat.py. File nay chi lo giao dien.
Design tokens lay tu design_system.md (ui-ux-pro-max):
  primary #7C3AED, accent #0891B2, background #FAF5FF, foreground #1E1B4B,
  heading Space Grotesk, body DM Sans.
"""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

st.set_page_config(page_title="Research Agent", layout="wide")

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
SAMPLE_QUESTIONS = [
    "Tin tức mới nhất về OpenAI trong tuần này",
    "Lấy các bài đăng gần đây của tài khoản nasa",
    "Tìm các bài đăng mới nhất nói về Claude Code",
    "Tìm giúp mình thông tin về dự án đó",  # thieu thong tin -> agent nen hoi lai
]

# ---------------------------------------------------------------- styles ----
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --color-primary: #7C3AED;
  --color-on-primary: #FFFFFF;
  --color-secondary: #A78BFA;
  --color-accent: #0891B2;
  --color-background: #FAF5FF;
  --color-foreground: #1E1B4B;
  --color-card: #FFFFFF;
  --color-muted: #ECEEF9;
  --color-muted-foreground: #475569;
  --color-border: #DDD6FE;
  --color-ring: #7C3AED;
  --radius: 14px;
  --font-heading: 'Space Grotesk', 'DM Sans', system-ui, sans-serif;
  --font-body: 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

html, body, .stApp, [data-testid="stAppViewContainer"], .stMarkdown, p, li, label, input, textarea, button {
  font-family: var(--font-body) !important;
}
h1, h2, h3, h4, .ra-title, .ra-welcome h2 {
  font-family: var(--font-heading) !important;
  letter-spacing: -0.01em;
  color: var(--color-foreground);
}

/* Minimal chrome: an footer + menu, header trong suot */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 880px; padding-top: 2.2rem; padding-bottom: 6rem; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--color-card);
  border-right: 1px solid var(--color-border);
}

/* Hero header */
.ra-hero { margin-bottom: 1.2rem; }
.ra-title { font-size: 2rem; font-weight: 700; margin: 0 0 .5rem 0; }
.ra-title span { color: var(--color-primary); }
.ra-chips { display: flex; flex-wrap: wrap; gap: .5rem; }
.ra-chip {
  display: inline-flex; align-items: center; gap: .4rem;
  padding: .25rem .7rem; border-radius: 999px;
  background: var(--color-card); border: 1px solid var(--color-border);
  color: var(--color-muted-foreground); font-size: .8rem; font-weight: 500;
  overflow-wrap: anywhere;
}
.ra-chip b { color: var(--color-foreground); font-weight: 600; }
.ra-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-accent); }

/* Welcome (empty state) */
.ra-welcome {
  background: var(--color-card); border: 1px solid var(--color-border);
  border-radius: var(--radius); padding: 1.4rem 1.5rem; margin: .5rem 0 1rem 0;
}
.ra-welcome h2 { font-size: 1.25rem; margin: 0 0 .3rem 0; }
.ra-welcome p { margin: 0; color: var(--color-muted-foreground); }

/* Chat bubbles */
[data-testid="stChatMessage"] {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: .9rem 1.1rem;
  margin-bottom: .8rem;
  box-shadow: 0 1px 2px rgba(30, 27, 75, .04);
}
/* user message: tint nhe */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: #F3EEFF;
  border-color: var(--color-secondary);
}
[data-testid="stChatMessage"] p { line-height: 1.65; }

/* Tool call card */
[data-testid="stExpander"] {
  border: 1px solid var(--color-border) !important;
  border-left: 4px solid var(--color-accent) !important;
  border-radius: 12px !important;
  background: #FFFFFF;
  margin-top: .5rem;
}
[data-testid="stExpander"] summary { cursor: pointer; font-weight: 500; }
[data-testid="stExpander"] summary:hover { background: var(--color-muted); }

/* Buttons */
.stButton > button {
  cursor: pointer;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-foreground);
  text-align: left;
  transition: background-color 180ms ease, border-color 180ms ease, transform 180ms ease;
}
.stButton > button:hover {
  background: var(--color-muted);
  border-color: var(--color-primary);
  color: var(--color-foreground);
}
.stButton > button:active { transform: translateY(1px); }

/* Chat input */
[data-testid="stChatInput"] { border-radius: var(--radius); }
[data-testid="stChatInput"] textarea { font-size: 1rem; }

/* Focus ro rang cho ban phim */
button:focus-visible, textarea:focus-visible, input:focus-visible,
summary:focus-visible, a:focus-visible, [tabindex]:focus-visible {
  outline: 3px solid var(--color-ring) !important;
  outline-offset: 2px !important;
}

/* Typing indicator (3-dot pulse) */
.ra-typing {
  display: inline-flex; align-items: center; gap: .55rem;
  padding: .55rem .9rem; border-radius: 999px;
  background: var(--color-card); border: 1px solid var(--color-border);
  color: var(--color-muted-foreground); font-size: .9rem;
}
.ra-typing i {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--color-primary); display: inline-block;
  animation: ra-pulse 1.2s infinite ease-in-out;
}
.ra-typing i:nth-child(2) { animation-delay: .15s; }
.ra-typing i:nth-child(3) { animation-delay: .3s; }
@keyframes ra-pulse {
  0%, 80%, 100% { opacity: .25; transform: scale(.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* Waiting-for-user note */
.ra-wait {
  margin-top: .6rem; padding: .5rem .8rem; border-radius: 10px;
  background: #ECFEFF; border: 1px solid #A5F3FC; color: #164E63; font-size: .9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.2rem; }
  .ra-title { font-size: 1.5rem; }
  .ra-welcome { padding: 1rem; }
}

/* Ton trong prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
  .ra-typing i { opacity: .7; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TYPING_HTML = (
    '<div class="ra-typing" role="status" aria-live="polite">'
    "<i></i><i></i><i></i><span>Agent đang xử lý...</span></div>"
)
WAIT_HTML = '<div class="ra-wait">Agent đang chờ bạn trả lời câu hỏi trên.</div>'


# --------------------------------------------------------------- helpers ----
@st.cache_resource(show_spinner=False)
def get_provider(name: str):
    return make_provider(name)


def new_session(cfg: dict[str, Any]) -> None:
    """Tao hoi thoai + file transcript moi."""
    artifact_version = build_artifact_version(
        cfg["version"], Path(cfg["system_prompt"]), Path(cfg["tools"])
    )
    provider = get_provider(cfg["provider"])
    selected_model = cfg["model"] or getattr(provider, "default_model", None)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [safe_slug(cfg["version"]), safe_slug(cfg["provider"]), "ui", timestamp]
    )
    st.session_state.transcript_path = (
        ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    )
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": cfg["provider"],
        "model": selected_model,
        "system_prompt": cfg["system_prompt"],
        "tools": cfg["tools"],
        "history_window": cfg["window"],
        "max_tool_rounds": cfg["max_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source": "streamlit_ui",
        "turns": [],
    }
    st.session_state.history = []  # lich su gui cho model
    st.session_state.display = []  # lich su hien thi tren UI
    st.session_state.config = cfg


def render_events(events: list[dict[str, Any]]) -> None:
    for ev in events:
        args = json.dumps(ev.get("args", {}), ensure_ascii=False)
        short = args if len(args) <= 70 else args[:67] + "..."
        with st.expander(f"{ev.get('tool')}  {short}"):
            st.caption("Arguments")
            st.json(ev.get("args", {}))
            st.caption("Result")
            text = json.dumps(ev.get("result"), ensure_ascii=False, default=str)
            if len(text) > 6000:
                st.code(text[:6000] + "\n...<truncated>", language="json")
            else:
                st.json(ev.get("result"))


def chip(label: str, value: Any) -> str:
    return (
        f'<span class="ra-chip"><span class="ra-dot"></span>'
        f"{html.escape(label)} <b>{html.escape(str(value))}</b></span>"
    )


# --------------------------------------------------------------- sidebar ----
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model (để trống = mặc định)", value="").strip() or None
    version = st.text_input("Version label", value="v3").strip() or "v0"
    window = st.number_input("History window (cặp user/assistant)", 1, 20, 5)
    max_rounds = st.number_input("Max tool rounds", 1, 10, 4)
    system_prompt_path = st.text_input(
        "System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md")
    )
    tools_path = st.text_input("Tools yaml", value=str(ARTIFACTS_DIR / "tools.yaml"))

    cfg = {
        "provider": provider_name,
        "model": model,
        "version": version,
        "window": int(window),
        "max_rounds": int(max_rounds),
        "system_prompt": system_prompt_path,
        "tools": tools_path,
    }

    if st.button("Reset hội thoại", use_container_width=True):
        new_session(cfg)
        st.rerun()

    st.divider()
    st.subheader("Câu hỏi mẫu")
    for i, q in enumerate(SAMPLE_QUESTIONS):
        if st.button(q, key=f"side_{i}", use_container_width=True):
            st.session_state.pending = q

# Doi cau hinh -> tu dong mo hoi thoai moi (de transcript ghi dung version/provider)
if "config" not in st.session_state or st.session_state.config != cfg:
    try:
        new_session(cfg)
    except Exception as exc:
        st.error(f"Không khởi tạo được session: {type(exc).__name__}: {exc}")
        st.stop()

# ------------------------------------------------------------------ main ----
tr = st.session_state.transcript
st.markdown(
    '<div class="ra-hero"><h1 class="ra-title">Research <span>Agent</span></h1>'
    '<div class="ra-chips">'
    + chip("version", tr.get("artifact_version", cfg["version"]))
    + chip("provider", tr["provider"])
    + chip("model", tr["model"])
    + "</div></div>",
    unsafe_allow_html=True,
)

# Empty state: hien khi chua co tin nhan
welcome = st.empty()
if not st.session_state.display:
    with welcome.container():
        st.markdown(
            '<div class="ra-welcome"><h2>Bạn muốn nghiên cứu gì hôm nay?</h2>'
            "<p>Agent tự chọn tool phù hợp (tìm web, đọc URL, xem bài đăng...) "
            "và hiển thị từng bước để bạn kiểm chứng. Thử một câu hỏi mẫu:</p></div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, q in enumerate(SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"welcome_{i}", use_container_width=True):
                st.session_state.pending = q

for m in st.session_state.display:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("events"):
            render_events(m["events"])
        if m.get("status") == "waiting_for_user":
            st.markdown(WAIT_HTML, unsafe_allow_html=True)

prompt = st.chat_input("Nhập yêu cầu nghiên cứu...") or st.session_state.pop(
    "pending", None
)

if prompt:
    welcome.empty()
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.display.append({"role": "user", "content": prompt})

    # Doc lai file moi luot: sua prompt/tools khong can restart app
    system_prompt = Path(cfg["system_prompt"]).read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(Path(cfg["tools"])))
    provider = get_provider(cfg["provider"])

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, cfg["window"]),
        {"role": "user", "content": prompt},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": len(tr["turns"]) + 1,
        "started_at": now_iso(),
        "user": prompt,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        typing = st.empty()
        typing.markdown(TYPING_HTML, unsafe_allow_html=True)
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=cfg["model"],
                max_tool_rounds=cfg["max_rounds"],
            )
            turn_record.update(result)
            answer = result["assistant_text"]
            events = result["tool_events"]
            status = result["status"]
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.history.append({"role": "assistant", "content": answer})
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            turn_record.update({"status": "provider_error", "error": err})
            answer, events, status = f"Lỗi: {err}", [], "provider_error"
        typing.empty()

        st.markdown(answer)
        if events:
            render_events(events)
        if status == "waiting_for_user":
            st.markdown(WAIT_HTML, unsafe_allow_html=True)

    st.session_state.display.append(
        {"role": "assistant", "content": answer, "events": events, "status": status}
    )
    turn_record["ended_at"] = now_iso()
    tr["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, tr)
    st.sidebar.caption(f"Transcript: `{st.session_state.transcript_path.name}`")