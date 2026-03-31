import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
import time
import re
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="InterviewAI Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0b0f1a;
    --surface:   #111827;
    --surface2:  #1a2235;
    --border:    #1e2d45;
    --accent:    #00e5ff;
    --accent2:   #7c3aed;
    --green:     #10b981;
    --yellow:    #f59e0b;
    --red:       #ef4444;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --radius:    12px;
    --font-head: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ── Force ALL text visible everywhere ── */
*, *::before, *::after {
    color: var(--text);
}
p, span, div, li, td, th, label,
[data-testid="stMarkdown"],
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] span,
[data-testid="stText"],
.stMarkdown, .stMarkdown p {
    color: var(--text) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: var(--text) !important;
}

/* ── Main content text ── */
[data-testid="stMain"] *,
[data-testid="stVerticalBlock"] *,
.main .block-container * {
    color: var(--text) !important;
}

/* ── Labels (input/select/upload labels) ── */
label, .stSelectbox label, .stTextInput label,
.stTextArea label, .stNumberInput label,
.stFileUploader label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ── Metric widget ── */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: var(--text) !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: var(--font-head) !important;
}

/* ── Tab labels ── */
[data-baseweb="tab"] div,
[data-baseweb="tab"] span,
[data-baseweb="tab"] p,
button[role="tab"],
button[role="tab"] * {
    color: var(--text) !important;
}
[aria-selected="true"][data-baseweb="tab"],
[aria-selected="true"][data-baseweb="tab"] * {
    color: #fff !important;
}

/* ── Expander header ── */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] details summary p {
    color: var(--text) !important;
}

/* ── Selectbox dropdown text ── */
[data-baseweb="select"] *,
[data-baseweb="menu"] *,
[role="listbox"] * {
    color: var(--text) !important;
    background: var(--surface2) !important;
}
[data-baseweb="select"] [data-testid="stMarkdown"] p {
    color: var(--text) !important;
}

/* ── Number input arrows ── */
.stNumberInput button svg { fill: var(--text) !important; }

/* ── Chat message text ── */
[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span {
    color: var(--text) !important;
}

/* ── Info / Warning / Success / Error text ── */
[data-testid="stAlert"] *,
[data-testid="stAlert"] p {
    color: var(--text) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Headings ── */
h1, h2, h3, h4, h5, h6, .syne {
    font-family: var(--font-head) !important;
    color: var(--text) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2) 0%, #5b21b6 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-head) !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: 0.6rem 1.4rem !important;
    transition: transform .15s, box-shadow .15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs / Textareas ── */
.stTextInput > div > div > input,
.stTextArea > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.15) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    transition: border-color .2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: .75rem !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    border-color: rgba(0,229,255,.25) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stChatInput"] textarea { color: var(--text) !important; }
[data-testid="stChatInput"] button { color: var(--accent) !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-head) !important;
    color: var(--accent) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent2), var(--accent)) !important;
    border-radius: 999px !important;
}
[data-testid="stProgressBar"] > div {
    background: var(--border) !important;
    border-radius: 999px !important;
}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
}

/* ── Alerts ── */
.stAlert { border-radius: var(--radius) !important; }
.stWarning { background: rgba(245,158,11,.12) !important; border-color: var(--yellow) !important; }
.stSuccess { background: rgba(16,185,129,.12) !important; border-color: var(--green) !important; }
.stInfo    { background: rgba(0,229,255,.08) !important;  border-color: var(--accent) !important; }
.stError   { background: rgba(239,68,68,.12) !important;  border-color: var(--red) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Sidebar section labels ── */
.sidebar-section {
    font-family: var(--font-head);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.25rem 0 .5rem;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    padding: .2rem .7rem;
    border-radius: 999px;
    font-family: var(--font-head);
    font-size: .8rem;
    font-weight: 700;
}
.score-great  { background: rgba(16,185,129,.2);  color: #10b981; }
.score-ok     { background: rgba(245,158,11,.2);  color: #f59e0b; }
.score-poor   { background: rgba(239,68,68,.2);   color: #ef4444; }

/* ── Typing dots ── */
@keyframes blink { 0%,80%,100%{opacity:0} 40%{opacity:1} }
.dot { display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--accent); margin:0 2px; animation: blink 1.4s infinite; }
.dot:nth-child(2){animation-delay:.2s}
.dot:nth-child(3){animation-delay:.4s}

/* ── Tabs ── */
[data-baseweb="tab-list"] { background: var(--surface2) !important; border-radius: var(--radius) !important; padding: 4px !important; }
[data-baseweb="tab"] { background: transparent !important; border-radius: 8px !important; color: var(--muted) !important; }
[aria-selected="true"][data-baseweb="tab"] { background: var(--accent2) !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def extract_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    return "\n".join(p.extract_text() or "" for p in reader.pages)

def extract_txt(file) -> str:
    return file.read().decode("utf-8", errors="ignore")

def score_color(s: int) -> str:
    if s >= 75: return "score-great"
    if s >= 45: return "score-ok"
    return "score-poor"

def build_system_prompt(resume: str, job_desc: str, interview_type: str,
                         difficulty: str, total_rounds: int) -> str:
    return f"""You are **InterviewAI Pro** — an expert, emotionally-intelligent interviewer.

## Context
- **Resume**: {resume[:3000]}
- **Job Description**: {job_desc[:2000]}
- **Interview Type**: {interview_type}
- **Difficulty**: {difficulty}
- **Total Rounds**: {total_rounds}

## Behaviour Rules
1. Ask ONE focused question at a time. Never ask multiple questions in one turn.
2. After each candidate answer, provide:
   - A brief (1–2 sentence) **reaction** to what they said (encouraging but honest).
   - A **JSON block** wrapped in ```json ... ``` containing:
     {{"score": <int 0-100>, "feedback": "<concise tip>", "next_question": "<your next question>"}}
3. Tailor questions to the resume + job description. Reference specific skills/projects.
4. Interview type guides question style:
   - **Technical**: coding, system design, problem-solving
   - **Behavioral**: STAR-method situations (teamwork, conflict, leadership)
   - **HR/Culture**: motivation, salary expectations, culture fit
   - **Mixed**: rotate all three types
5. Difficulty: {difficulty} — adjust vocabulary and depth accordingly.
6. When the round is complete (after ~5–6 substantive answers), output the JSON with "round_complete": true and an overall "round_summary" string.
7. Always stay professional, warm, and constructive.
"""

def call_gemini(api_key: str, messages: list, system: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system,
        )
        history = []
        for m in messages[:-1]:
            history.append({"role": m["role"], "parts": [m["content"]]})
        chat = model.start_chat(history=history)
        resp = chat.send_message(messages[-1]["content"])
        return resp.text
    except Exception as e:
        return f"⚠️ API Error: {e}"

def parse_ai_response(raw: str):
    """Split AI prose from embedded JSON block."""
    prose, data = raw, {}
    match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
    if match:
        prose = raw[:match.start()].strip()
        try:
            data = json.loads(match.group(1))
        except Exception:
            data = {}
    return prose, data

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "messages": [],
    "started": False,
    "current_round": 1,
    "scores": [],           # list of per-answer scores
    "feedbacks": [],        # list of tip strings
    "round_scores": [],     # avg score per round
    "resume_text": "",
    "system_prompt": "",
    "question_count": 0,
    "total_rounds": 1,
    "interview_type": "Mixed",
    "difficulty": "Medium",
    "job_role": "",
    "start_time": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo / brand
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 .5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
                    background:linear-gradient(135deg,#00e5ff,#7c3aed);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            InterviewAI Pro
        </div>
        <div style="color:#64748b; font-size:.75rem; letter-spacing:.1em; margin-top:2px;">
            AI-POWERED MOCK INTERVIEWS
        </div>
    </div>
    <hr style="margin:.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    # ── API Key ──
    st.markdown('<div class="sidebar-section">🔑 Gemini API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("", type="password", placeholder="AIza...", label_visibility="collapsed")

    # ── Upload ──
    st.markdown('<div class="sidebar-section">📄 Resume / CV</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("", type=["pdf", "txt"], label_visibility="collapsed")
    if resume_file:
        st.success(f"✅ {resume_file.name}")

    # ── Job details ──
    st.markdown('<div class="sidebar-section">💼 Job Details</div>', unsafe_allow_html=True)
    job_role = st.text_input("", placeholder="e.g. Senior Software Engineer", label_visibility="collapsed")
    job_desc = st.text_area("", placeholder="Paste the full job description here…",
                             height=120, label_visibility="collapsed")

    # ── Settings ──
    st.markdown('<div class="sidebar-section">⚙️ Interview Settings</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        total_rounds = st.number_input("Rounds", min_value=1, max_value=5, value=1)
    with col_b:
        q_per_round = st.number_input("Qs/Round", min_value=3, max_value=10, value=5)

    interview_type = st.selectbox("Interview Type",
        ["Mixed", "Technical", "Behavioral", "HR / Culture Fit"])
    difficulty = st.selectbox("Difficulty",
        ["Easy", "Medium", "Hard", "Expert"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Start / Reset ──
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Start", use_container_width=True)
    with col2:
        reset_btn = st.button("🔄 Reset", use_container_width=True)

    if reset_btn:
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    if start_btn:
        if not api_key:
            st.error("Add your Gemini API key.")
        elif not resume_file:
            st.warning("Upload your resume.")
        elif not job_desc.strip():
            st.warning("Paste a job description.")
        else:
            with st.spinner("Analysing your resume…"):
                if resume_file.type == "application/pdf":
                    resume_text = extract_pdf(resume_file)
                else:
                    resume_text = extract_txt(resume_file)

            st.session_state.resume_text = resume_text
            st.session_state.total_rounds = total_rounds
            st.session_state.interview_type = interview_type
            st.session_state.difficulty = difficulty
            st.session_state.job_role = job_role
            st.session_state.question_count = q_per_round
            st.session_state.system_prompt = build_system_prompt(
                resume_text, job_desc, interview_type, difficulty, total_rounds
            )
            st.session_state.started = True
            st.session_state.start_time = datetime.now()
            st.session_state.messages = []
            st.session_state.scores = []
            st.session_state.feedbacks = []
            st.session_state.round_scores = []
            st.session_state.current_round = 1

            # Kick off with opening message from AI
            opening = call_gemini(
                api_key,
                [{"role": "user",
                  "content": f"Please start the interview. Greet me warmly, confirm the role ({job_role or 'the position'}) and difficulty ({difficulty}), and ask your first question."}],
                st.session_state.system_prompt,
            )
            prose, _ = parse_ai_response(opening)
            st.session_state.messages.append({"role": "model", "content": prose})
            st.rerun()

    # ── Resume preview ──
    if resume_file and not st.session_state.started:
        with st.expander("👁 Preview Resume Text"):
            if resume_file.type == "application/pdf":
                st.write(extract_pdf(resume_file)[:1500] + "…")
            else:
                st.write(extract_txt(resume_file)[:1500] + "…")

# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────
if not st.session_state.started:
    # ── Landing / hero ──
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem 2rem;">
        <div style="font-family:'Syne',sans-serif; font-size:3rem; font-weight:800; line-height:1.1;
                    background:linear-gradient(135deg,#e2e8f0 20%,#00e5ff 60%,#7c3aed 100%);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Ace Your Next Interview
        </div>
        <p style="color:#64748b; font-size:1.1rem; margin-top:1rem; max-width:560px; margin-left:auto; margin-right:auto;">
            Upload your resume, paste the JD, and let AI conduct a hyper-personalised mock interview — with real-time scoring and expert feedback.
        </p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("🎯", "Personalised Questions", "Tailored to your resume and the exact job description"),
        ("📊", "Live Scoring", "Each answer is scored 0–100 with actionable feedback"),
        ("🔄", "Multi-Round", "Simulate full interview loops up to 5 rounds"),
        ("📝", "Final Report", "Detailed performance breakdown after every round"),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        col.markdown(f"""
        <div style="background:#111827; border:1px solid #1e2d45; border-radius:12px;
                    padding:1.25rem; text-align:center; height:160px;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-family:'Syne',sans-serif; font-weight:700; margin:.5rem 0 .3rem;
                        font-size:.95rem;">{title}</div>
            <div style="color:#64748b; font-size:.82rem; line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👈 Fill in the sidebar and click **Start** to begin your interview.")

else:
    # ─────────────────────────────────────────
    #  ACTIVE INTERVIEW
    # ─────────────────────────────────────────

    # ── Top status bar ──
    avg_score = int(sum(st.session_state.scores) / len(st.session_state.scores)) \
                if st.session_state.scores else 0
    elapsed = ""
    if st.session_state.start_time:
        secs = int((datetime.now() - st.session_state.start_time).total_seconds())
        elapsed = f"{secs//60}m {secs%60}s"

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("📍 Round", f"{st.session_state.current_round} / {st.session_state.total_rounds}")
    sc2.metric("❓ Q&As", len([m for m in st.session_state.messages if m["role"] == "user"]))
    sc3.metric("⭐ Avg Score", f"{avg_score} / 100" if avg_score else "—")
    sc4.metric("⏱ Time", elapsed or "—")

    # ── Round progress ──
    q_answered = len([m for m in st.session_state.messages if m["role"] == "user"])
    progress_val = min(q_answered / max(st.session_state.question_count, 1), 1.0)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:1rem; margin:.5rem 0 1rem;">
        <span style="color:#64748b; font-size:.8rem; white-space:nowrap;">
            Round {st.session_state.current_round} Progress
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_val)

    # ── Tab layout ──
    tab_chat, tab_feedback, tab_report = st.tabs(
        ["💬 Interview", "📊 Live Feedback", "📋 Report"]
    )

    # ── CHAT TAB ──
    with tab_chat:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                role = "assistant" if msg["role"] == "model" else "user"
                avatar = "🤖" if role == "assistant" else "🧑‍💻"
                with st.chat_message(role, avatar=avatar):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Type your answer…"):
            # Add user turn
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            # AI response
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                placeholder.markdown(
                    '<span class="dot"></span><span class="dot"></span><span class="dot"></span>',
                    unsafe_allow_html=True,
                )
                raw = call_gemini(
                    api_key,
                    st.session_state.messages,
                    st.session_state.system_prompt,
                )
                prose, data = parse_ai_response(raw)
                placeholder.markdown(prose)

            st.session_state.messages.append({"role": "model", "content": prose})

            # Harvest score / feedback
            if "score" in data:
                st.session_state.scores.append(data["score"])
            if "feedback" in data:
                st.session_state.feedbacks.append(data["feedback"])

            # Round complete?
            if data.get("round_complete"):
                round_avg = int(sum(st.session_state.scores[-st.session_state.question_count:]) /
                                max(len(st.session_state.scores[-st.session_state.question_count:]), 1))
                st.session_state.round_scores.append(round_avg)

                if st.session_state.current_round < st.session_state.total_rounds:
                    st.session_state.current_round += 1
                    st.success(f"✅ Round {st.session_state.current_round - 1} complete! "
                               f"Avg score: {round_avg}/100 — Starting round {st.session_state.current_round}…")
                else:
                    st.balloons()
                    st.success("🎉 Interview complete! Check the **Report** tab for your full analysis.")

            st.rerun()

    # ── FEEDBACK TAB ──
    with tab_feedback:
        if not st.session_state.feedbacks:
            st.info("Answer a question to see feedback here.")
        else:
            st.markdown("### 📈 Answer-by-Answer Breakdown")
            for i, (score, tip) in enumerate(
                zip(st.session_state.scores, st.session_state.feedbacks), 1
            ):
                cls = score_color(score)
                with st.expander(f"Answer #{i}  —  Score: {score}/100", expanded=(i == len(st.session_state.scores))):
                    st.markdown(f'<span class="score-badge {cls}">{score} / 100</span>', unsafe_allow_html=True)
                    st.markdown(f"**💡 Tip:** {tip}")
                    st.progress(score / 100)

            # Mini chart using columns as bars
            if len(st.session_state.scores) > 1:
                st.markdown("### 📊 Score Trend")
                bar_cols = st.columns(len(st.session_state.scores))
                for col, s in zip(bar_cols, st.session_state.scores):
                    colour = "#10b981" if s >= 75 else "#f59e0b" if s >= 45 else "#ef4444"
                    col.markdown(
                        f'<div style="background:{colour}; height:{int(s*1.2)}px; '
                        f'border-radius:4px 4px 0 0; margin:0 2px;" title="{s}/100"></div>'
                        f'<div style="text-align:center;font-size:.7rem;color:#64748b;">{s}</div>',
                        unsafe_allow_html=True,
                    )

    # ── REPORT TAB ──
    with tab_report:
        if not st.session_state.scores:
            st.info("Complete at least one answer to generate a report.")
        else:
            overall = int(sum(st.session_state.scores) / len(st.session_state.scores))
            cls = score_color(overall)

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#111827,#1a2235);
                        border:1px solid #1e2d45; border-radius:16px;
                        padding:2rem; text-align:center; margin-bottom:1.5rem;">
                <div style="font-family:'Syne',sans-serif; font-size:.8rem;
                            letter-spacing:.15em; color:#64748b; margin-bottom:.5rem;">
                    OVERALL INTERVIEW SCORE
                </div>
                <div style="font-family:'Syne',sans-serif; font-size:4rem; font-weight:800;
                            background:linear-gradient(135deg,#00e5ff,#7c3aed);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    {overall}<span style="font-size:2rem;">/100</span>
                </div>
                <span class="score-badge {cls}" style="margin-top:.5rem; display:inline-block;">
                    {"Excellent 🏆" if overall>=75 else "Needs Work 📈" if overall>=45 else "Keep Practising 💪"}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Per-round summary
            if st.session_state.round_scores:
                st.markdown("#### Round Scores")
                rcols = st.columns(len(st.session_state.round_scores))
                for i, (col, rs) in enumerate(zip(rcols, st.session_state.round_scores), 1):
                    col.metric(f"Round {i}", f"{rs}/100")

            # Strengths / areas of improvement (simple heuristic)
            high = [(i+1, s) for i, s in enumerate(st.session_state.scores) if s >= 75]
            low  = [(i+1, s) for i, s in enumerate(st.session_state.scores) if s < 50]

            col_s, col_i = st.columns(2)
            with col_s:
                st.markdown("#### ✅ Strengths")
                if high:
                    for q, s in high:
                        st.markdown(f"- **Q{q}** — scored {s}/100")
                else:
                    st.markdown("Keep working — you'll get there!")

            with col_i:
                st.markdown("#### 🔧 Improvement Areas")
                if low:
                    for q, s in low:
                        tip = st.session_state.feedbacks[q-1] if q-1 < len(st.session_state.feedbacks) else ""
                        st.markdown(f"- **Q{q}** ({s}/100): {tip}")
                else:
                    st.markdown("Great job overall!")

            # All tips
            with st.expander("📝 All Feedback Tips"):
                for i, tip in enumerate(st.session_state.feedbacks, 1):
                    st.markdown(f"**Q{i}:** {tip}")

            # Generate AI final summary
            if st.button("🤖 Generate Full AI Report"):
                with st.spinner("Generating detailed report…"):
                    summary_prompt = (
                        f"The interview is complete. Scores: {st.session_state.scores}. "
                        f"Please write a comprehensive performance review including: "
                        f"1) Executive summary  2) Top 3 strengths  3) Top 3 areas to improve  "
                        f"4) Recommended resources  5) Overall hire/no-hire recommendation."
                    )
                    msgs = st.session_state.messages + [{"role": "user", "content": summary_prompt}]
                    report = call_gemini(api_key, msgs, st.session_state.system_prompt)
                    prose, _ = parse_ai_response(report)
                    st.markdown(prose)