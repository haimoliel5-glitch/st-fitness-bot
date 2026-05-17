import streamlit as st
import requests
import os
import base64

# ============================================================
#  הגדרות
# ============================================================
API_URL       = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
API_KEY       = "sk-std-m4kF_4n8sTvd3eeCguxeT3aARvJZYAp8tB-gkuBDPxA"
TRAINER_NAME  = "בן"
TRAINER_PHONE = "0506682769"
GYM_NAME      = "ST-FITNESS"
MAX_MESSAGES  = 20
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def build_system_prompt(name: str) -> str:
    return f"""
אתה בן — מאמן הכושר האגדי של {GYM_NAME}. אתה נלהב, כריזמטי, ומלא אנרגיה!
שם המתאמן שלך עכשיו הוא: {name}.

הסגנון שלך:
- תמיד פתח עם מחמאה או עידוד ("וואו {name}, שאלה מעולה!", "כל הכבוד שאתה שואל!", "אני גאה בך!")
- השתמש בהרבה אמוג'י 💪🔥⚡🏆💥
- ענה בעברית, קצר וברור
- סיים תמיד עם משפט מעודד ("קדימה אלוף!", "אתה מדהים!", "ממשיכים להתקדם!")
- פנה ל{name} בשמו לפחות פעם בכל תשובה
- אם שלחו תמונה של אוכל — נתח את הערכים התזונתיים
- אם שלחו תמונה של תרגיל — תן פידבק על הטכניקה
- אל תמציא מידע רפואי — הפנה לרופא
- אם רוצים לדבר עם המאמן — אמור ללחוץ על "העבר למאמן"
"""

# ── CSS ───────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{GYM_NAME} | בוט כושר",
    page_icon="💪",
    layout="centered"
)

st.markdown("""
<style>
    body { direction: rtl; }
    #MainMenu, footer, header { visibility: hidden; }

    /* רקע שחור עם דוגמת כושר */
    .stApp {
        background-color: #0a0a0a;
        background-image:
            repeating-linear-gradient(
                45deg,
                transparent,
                transparent 40px,
                rgba(192,57,43,0.04) 40px,
                rgba(192,57,43,0.04) 41px
            ),
            repeating-linear-gradient(
                -45deg,
                transparent,
                transparent 40px,
                rgba(192,57,43,0.04) 40px,
                rgba(192,57,43,0.04) 41px
            );
    }

    /* אזור הצ'אט */
    .chat-area {
        background: rgba(236,229,221,0.92);
        border-radius: 16px;
        padding: 12px;
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
        min-height: 300px;
    }

    /* כותרת */
    .wa-header {
        background: linear-gradient(135deg, #111 0%, #1a0000 100%);
        color: white;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin: -1rem -1rem 1rem -1rem;
        direction: rtl;
        border-bottom: 3px solid #c0392b;
        box-shadow: 0 2px 15px rgba(192,57,43,0.4);
    }
    .wa-name   { font-weight: bold; font-size: 17px; letter-spacing: 2px; }
    .wa-status { font-size: 12px; opacity: 0.7; color: #e74c3c; }

    /* בועות */
    .msg-user {
        background: linear-gradient(135deg, #DCF8C6, #c8f0b0);
        padding: 10px 14px;
        border-radius: 18px 4px 18px 18px;
        margin: 6px 0 6px auto;
        max-width: 78%;
        width: fit-content;
        text-align: right;
        direction: rtl;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .msg-bot {
        background: linear-gradient(135deg, #fff, #f8f8f8);
        padding: 10px 14px;
        border-radius: 4px 18px 18px 18px;
        margin: 6px auto 6px 0;
        max-width: 78%;
        width: fit-content;
        text-align: right;
        direction: rtl;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border-right: 3px solid #c0392b;
    }
    .msg-time  { font-size: 11px; color: #aaa; margin-top: 4px; }
    .msg-wrapper-user { display:flex; justify-content:flex-end; margin:4px 0; }
    .msg-wrapper-bot  { display:flex; justify-content:flex-start; margin:4px 0; }

    /* כפתורים */
    .stButton > button {
        background: linear-gradient(135deg, #c0392b, #922b21) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(192,57,43,0.4) !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(192,57,43,0.6) !important;
    }

    /* מסך פתיחה */
    .name-screen {
        background: linear-gradient(135deg, #111, #1a0000);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        color: white;
        margin-top: 1rem;
        border: 1px solid #c0392b;
        box-shadow: 0 0 30px rgba(192,57,43,0.3);
    }

    /* input */
    .stTextInput input {
        background: #1a1a1a !important;
        color: white !important;
        border: 1px solid #c0392b !important;
        border-radius: 12px !important;
        text-align: right !important;
    }

    /* סיידבר */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a, #1a0000) !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* העלאת קובץ */
    [data-testid="stFileUploader"] {
        border: 2px dashed #c0392b !important;
        border-radius: 12px !important;
        background: rgba(192,57,43,0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── פונקציות עזר ──────────────────────────────────────────
def get_logo_b64():
    if os.path.exists("logo.jpg"):
        with open("logo.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def img_to_b64(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode()

# ── מסך הזנת שם ───────────────────────────────────────────
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    logo_b64 = get_logo_b64()
    if logo_b64:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.jpg", use_container_width=True)

    st.markdown(f"""
    <div class="name-screen">
        <h1 style="color:#c0392b; font-size:2.5rem; margin:0;">💪 {GYM_NAME}</h1>
        <p style="color:#aaa; margin:8px 0 0;">STRENGTH › FOCUS › RESULTS</p>
        <p style="margin-top:1.5rem; font-size:1.1rem;">הבוט החכם של מאמן {TRAINER_NAME}</p>
        <p style="color:#888; font-size:13px;">שאל כל שאלה על כושר, תזונה ומוטיבציה 🔥</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    name_input = st.text_input("", placeholder="✍️ הכנס את שמך כדי להתחיל...", label_visibility="collapsed")

    if st.button("🔥 בוא נתחיל!"):
        if name_input.strip():
            name = name_input.strip()
            st.session_state.user_name = name
            st.session_state.messages = [
                {"role": "system", "content": build_system_prompt(name)}
            ]
            st.session_state.transferred = False
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"וואו {name}! 🔥 כל הכבוד שהצטרפת לבוט של {GYM_NAME}!\nאני כאן כדי לעזור לך לשבור שיאים! 💪⚡\nשאל אותי הכל — כושר, תזונה, מוטיבציה — אני הכל יודע!\nקדימה אלוף, יאללה! 🏆"
            })
            st.rerun()
        else:
            st.error("💪 אנא הכנס שם כדי להמשיך!")
    st.stop()

# ── כותרת ─────────────────────────────────────────────────
logo_b64 = get_logo_b64()
avatar = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #c0392b;">' if logo_b64 else "💪"

st.markdown(f"""
<div class="wa-header">
    {avatar}
    <div>
        <div class="wa-name">{GYM_NAME}</div>
        <div class="wa-status">⚡ {st.session_state.user_name} | מחובר</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── איפוס אוטומטי ─────────────────────────────────────────
user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
if len(user_msgs) >= MAX_MESSAGES:
    name = st.session_state.user_name
    st.session_state.messages = [
        {"role": "system", "content": build_system_prompt(name)},
        {"role": "assistant", "content": f"🔄 {name}, התחלנו שיחה טרייה כדי שאני אמשיך לתת לך את המיטב! קדימה, מה השאלה הבאה? 💪🔥"}
    ]

# ── הצגת הודעות ───────────────────────────────────────────
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    if msg["role"] == "user":
        content = msg["content"] if isinstance(msg["content"], str) else "📸 שלחת תמונה"
        st.markdown(f'<div class="msg-wrapper-user"><div class="msg-user">{content}<div class="msg-time">✓✓</div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-wrapper-bot"><div class="msg-bot">{msg["content"]}<div class="msg-time">💪 {TRAINER_NAME} | {GYM_NAME}</div></div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── העלאת תמונה ───────────────────────────────────────────
with st.expander("📸 שלח תמונה (אוכל / תרגיל)"):
    uploaded = st.file_uploader("בחר תמונה", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        st.image(uploaded, width=250)
        caption = st.text_input("הוסף הערה לתמונה (לא חובה):", placeholder="למשל: מה הקלוריות כאן?")
        if st.button("📤 שלח תמונה"):
            img_b64 = img_to_b64(uploaded)
            mime = "image/jpeg" if uploaded.name.endswith(("jpg","jpeg")) else "image/png"
            text = caption if caption else "תנתח את התמונה הזו מבחינת כושר/תזונה"
            st.session_state.messages.append({"role": "user", "content": f"[תמונה נשלחה] {text}"})

            with st.spinner("🔍 מנתח תמונה..."):
                try:
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": st.session_state.messages[:-1] + [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}}
                            ]
                        }],
                        "max_tokens": 2000
                    }
                    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
                    data = r.json()
                    reply = data["choices"][0]["message"]["content"] if "choices" in data else "לא הצלחתי לנתח את התמונה, נסה שוב 🙏"
                except Exception as e:
                    reply = f"שגיאה: {e}"

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# ── כפתור העבר למאמן ──────────────────────────────────────
if not st.session_state.transferred:
    if st.button("📲 העבר אותי למאמן בן"):
        st.session_state.transferred = True
        wa_link = f"https://wa.me/972{TRAINER_PHONE[1:]}?text=היי+{TRAINER_NAME},+אני+{st.session_state.user_name}+מתאמן+ב{GYM_NAME}+וצריך+עזרה"
        st.session_state.messages.append({
            "role": "assistant",
            "content": f'כל הכבוד {st.session_state.user_name} שאתה יוזם! 🏆 לחץ כאן לשיחה ישירה עם {TRAINER_NAME}: <a href="{wa_link}" target="_blank" style="color:#c0392b;font-weight:bold;font-size:16px;">💬 פתח ווצאפ עם {TRAINER_NAME}</a>'
        })
        st.rerun()

# ── קלט ───────────────────────────────────────────────────
if prompt := st.chat_input(f"שאל את {TRAINER_NAME}... 💪"):
    st.session_state.transferred = False
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🔥 בן חושב..."):
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": st.session_state.messages,
                "max_tokens": 2000
            }
            r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
            data = r.json()
            reply = data["choices"][0]["message"]["content"] if "choices" in data else f"שגיאה: {data}"
        except Exception as e:
            reply = f"שגיאת חיבור: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── סיידבר ────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    st.markdown(f"## {GYM_NAME}")
    st.markdown("💪 STRENGTH › FOCUS › RESULTS")
    st.markdown(f"📞 מאמן {TRAINER_NAME}: {TRAINER_PHONE}")
    st.divider()
    count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.caption(f"הודעות: {count}/{MAX_MESSAGES}")
    st.progress(count / MAX_MESSAGES)
    st.divider()
    if st.button("🗑 שיחה חדשה"):
        st.session_state.user_name = ""
        st.session_state.messages = []
        st.session_state.transferred = False
        st.rerun()
