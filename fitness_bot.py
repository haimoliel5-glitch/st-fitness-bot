import streamlit as st
import requests
import os
import base64

# ============================================================
#  הגדרות
# ============================================================
API_URL       = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
API_KEY       = "sk-std-NYI6dMVcFMobVTH3T8hrp2s4CWCNwJDi04ZLmflNzQU"
TRAINER_NAME  = "בן"
TRAINER_PHONE = "0506682769"
GYM_NAME      = "ST-FITNESS"
MAX_MESSAGES  = 6
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = f"""
אתה בן — מאמן הכושר האגדי של {GYM_NAME}. אתה נלהב, כריזמטי, ומלא אנרגיה!
הסגנון שלך:
- תמיד פתח עם מחמאה או עידוד ("שאלה מעולה!", "כל הכבוד שאתה שואל!")
- השתמש בהרבה אמוג'י 💪🔥⚡🏆💥
- ענה בעברית, קצר וברור — מקסימום 3-4 משפטים
- סיים תמיד עם משפט מעודד ("קדימה אלוף!", "אתה מדהים!", "ממשיכים!")
- אם שלחו תמונת אוכל — נתח קלוריות בקצרה
- אם שלחו תמונת תרגיל — תן פידבק קצר על טכניקה
- אל תמציא מידע רפואי — הפנה לרופא
- אם רוצים לדבר עם המאמן — אמור ללחוץ על הכפתור למטה
"""

# ── לוגו כרקע ─────────────────────────────────────────────
def get_logo_b64():
    if os.path.exists("logo.jpg"):
        with open("logo.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_logo_b64()

st.set_page_config(
    page_title=f"{GYM_NAME} | בוט כושר",
    page_icon="💪",
    layout="centered"
)

bg_css = ""
if logo_b64:
    bg_css = f"""
    .stApp {{
        background-color: #111111;
        background-image: url("data:image/jpeg;base64,{logo_b64}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 50%;
        background-attachment: fixed;
    }}
    """

st.markdown(f"""
<style>
    body {{ direction: rtl; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    {bg_css}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0,0,0,0.85);
        z-index: 0;
        pointer-events: none;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding: 0 1rem 5rem 1rem !important;
        max-width: 100% !important;
    }}

    /* כותרת */
    .wa-header {{
        background: rgba(20,20,20,0.97);
        color: white;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin: -1rem -1rem 1rem -1rem;
        direction: rtl;
        border-bottom: 3px solid #c0392b;
        position: relative;
        z-index: 10;
    }}
    .wa-name   {{ font-weight: bold; font-size: 16px; color: white; display: block; }}
    .wa-status {{ font-size: 12px; color: #e74c3c; display: block; }}

    /* אזור שיחה */
    .chat-wrap {{
        background: rgba(236,229,221,0.95);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }}

    /* בועות */
    .msg-user {{
        background: #DCF8C6;
        padding: 8px 12px;
        border-radius: 12px 2px 12px 12px;
        margin: 6px 0 6px auto;
        max-width: 80%;
        width: fit-content;
        text-align: right;
        direction: rtl;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        word-break: break-word;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
        display: block;
    }}
    .msg-bot {{
        background: white;
        padding: 8px 12px;
        border-radius: 2px 12px 12px 12px;
        margin: 6px auto 6px 0;
        max-width: 80%;
        width: fit-content;
        text-align: right;
        direction: rtl;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        border-right: 3px solid #c0392b;
        word-break: break-word;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
        display: block;
    }}
    .msg-time {{ font-size: 11px; color: #999; margin-top: 3px; display: block; }}
    .msg-wrapper-user {{ display: flex; justify-content: flex-end; margin: 4px 0; width: 100%; }}
    .msg-wrapper-bot  {{ display: flex; justify-content: flex-start; margin: 4px 0; width: 100%; }}

    /* ספינר */
    .thinking-box {{
        background: white;
        border-radius: 2px 12px 12px 12px;
        padding: 10px 16px;
        margin: 6px auto 6px 0;
        width: fit-content;
        border-right: 3px solid #c0392b;
        font-size: 15px;
        font-weight: bold;
        color: #c0392b;
        animation: pulse 1s infinite;
    }}
    @keyframes pulse {{
        0%   {{ opacity: 1; }}
        50%  {{ opacity: 0.4; }}
        100% {{ opacity: 1; }}
    }}

    /* כפתור העבר למאמן — עדין */
    .transfer-btn {{
        display: inline-block;
        margin: 8px auto;
        padding: 6px 16px;
        background: transparent;
        color: #888;
        border: 1px solid #555;
        border-radius: 20px;
        font-size: 12px;
        cursor: pointer;
        text-align: center;
        width: 100%;
    }}
    .transfer-btn:hover {{ color: #c0392b; border-color: #c0392b; }}

    /* כפתורים של streamlit */
    .stButton > button {{
        background: transparent !important;
        color: #888 !important;
        border: 1px solid #555 !important;
        border-radius: 20px !important;
        padding: 6px 16px !important;
        font-size: 12px !important;
        font-weight: normal !important;
        width: 100% !important;
        box-shadow: none !important;
    }}
    .stButton > button:hover {{
        color: #c0392b !important;
        border-color: #c0392b !important;
    }}

    /* סיידבר */
    section[data-testid="stSidebar"] {{
        background: rgba(15,15,15,0.97) !important;
    }}
    section[data-testid="stSidebar"] * {{ color: white !important; }}

    /* chat input */
    [data-testid="stChatInput"] {{
        background: rgba(20,20,20,0.95) !important;
        border-top: 1px solid #333 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── כותרת ─────────────────────────────────────────────────
avatar = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid #c0392b;flex-shrink:0;">' if logo_b64 else "💪"

st.markdown(f"""
<div class="wa-header">
    {avatar}
    <div style="flex:1; min-width:0;">
        <span class="wa-name">{GYM_NAME}</span>
        <span class="wa-status">⚡ בוט כושר חכם | מחובר</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── היסטוריה ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.transferred = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"היי! 👋 ברוך הבא לבוט של {GYM_NAME}! 🔥\nאני כאן לעזור לך לשבור שיאים 💪⚡\nשאל אותי הכל — כושר, תזונה, מוטיבציה!\nקדימה אלוף! 🏆"
    })

# איפוס אוטומטי
user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
if len(user_msgs) >= MAX_MESSAGES:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "🔄 התחלנו שיחה טרייה! קדימה, מה השאלה הבאה? 💪🔥"}
    ]

# ── הצגת הודעות ───────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    content = msg["content"] if isinstance(msg["content"], str) else "📸 תמונה"
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-wrapper-user"><div class="msg-user">{content}<span class="msg-time">✓✓</span></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-wrapper-bot"><div class="msg-bot">{content}<span class="msg-time">💪 {TRAINER_NAME} | {GYM_NAME}</span></div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── כפתור העבר למאמן — עדין ───────────────────────────────
if not st.session_state.transferred:
    if st.button(f"דבר ישירות עם {TRAINER_NAME} 💬"):
        st.session_state.transferred = True
        wa_link = f"https://wa.me/972{TRAINER_PHONE[1:]}?text=היי+{TRAINER_NAME},+אני+מתאמן+ב{GYM_NAME}+וצריך+עזרה"
        st.session_state.messages.append({
            "role": "assistant",
            "content": f'בוודאי! 🏆 לחץ כאן: <a href="{wa_link}" target="_blank" style="color:#c0392b;font-weight:bold;">💬 ווצאפ עם {TRAINER_NAME}</a>'
        })
        st.rerun()

# ── העלאת תמונה ───────────────────────────────────────────
with st.expander("📸 שלח תמונה (אוכל / תרגיל)"):
    uploaded = st.file_uploader("בחר תמונה", type=["jpg","jpeg","png"], label_visibility="collapsed")
    if uploaded:
        st.image(uploaded, width=200)
        caption = st.text_input("הערה:", placeholder="מה הקלוריות כאן?")
        if st.button("📤 שלח"):
            img_b64_up = base64.b64encode(uploaded.read()).decode()
            mime = "image/jpeg" if uploaded.name.lower().endswith(("jpg","jpeg")) else "image/png"
            text = caption if caption else "תנתח את התמונה מבחינת כושר/תזונה בקצרה"
            st.session_state.messages.append({"role": "user", "content": f"[תמונה] {text}"})
            with st.spinner("🔍 מנתח תמונה..."):
                try:
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": st.session_state.messages[:-1] + [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64_up}"}}
                            ]
                        }],
                        "max_tokens": 800
                    }
                    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
                    data = r.json()
                    reply = data["choices"][0]["message"]["content"] if "choices" in data else "לא הצלחתי לנתח 🙏"
                except Exception as e:
                    reply = f"שגיאה: {e}"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# ── קלט ───────────────────────────────────────────────────
if prompt := st.chat_input(f"שאל את {TRAINER_NAME}... 💪"):
    st.session_state.transferred = False
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ספינר מודגש
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(
        '<div class="msg-wrapper-bot"><div class="thinking-box">🔥 בן חושב...</div></div>',
        unsafe_allow_html=True
    )

    try:
        payload = {
            "model": "gpt-4o-mini",
            "messages": st.session_state.messages,
            "max_tokens": 3000
        }
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        data = r.json()
        reply = data["choices"][0]["message"]["content"] if "choices" in data else "נסה שוב 🙏"
    except Exception as e:
        reply = f"שגיאת חיבור: {e}"

    thinking_placeholder.empty()
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── סיידבר ────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    st.markdown(f"### {GYM_NAME}")
    st.markdown("💪 STRENGTH › FOCUS › RESULTS")
    st.markdown(f"📞 מאמן {TRAINER_NAME}: {TRAINER_PHONE}")
    st.divider()
    count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.caption(f"הודעות: {count}/{MAX_MESSAGES}")
    st.progress(count / MAX_MESSAGES)
    st.divider()
    if st.button("🗑 שיחה חדשה"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.transferred = False
        st.rerun()
