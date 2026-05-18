import streamlit as st
import requests
import os
import base64

# ============================================================
#  הגדרות
# ============================================================

API_URL = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
API_KEY = "sk-std-NYI6dMVcFMobVTH3T8hrp2s4CWCNwJDi04ZLmflNzQU"

TRAINER_NAME = "בן"
TRAINER_PHONE = "0506682769"
GYM_NAME = "ST-FITNESS"

MAX_HISTORY = 4

# ============================================================
#  HEADERS
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
#  SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""
אתה בן — מאמן הכושר האגדי של {GYM_NAME}.

הסגנון שלך:
- תמיד פתח עם מחמאה או עידוד
- השתמש באמוג'ים 💪🔥⚡🏆
- ענה בעברית
- מקסימום 3 משפטים
- סיים במשפט מוטיבציה
- אל תמציא מידע רפואי
- אם רוצים לדבר עם המאמן תגיד ללחוץ על הכפתור למטה
"""

# ============================================================
#  LOGO
# ============================================================

def get_logo_b64():

    if os.path.exists("logo.jpg"):

        with open("logo.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()

    return ""

# ============================================================
#  CLEAN HISTORY
# ============================================================

def trim_history(messages):

    cleaned = []

    for msg in messages:

        if not isinstance(msg, dict):
            continue

        if "role" not in msg or "content" not in msg:
            continue

        content = msg["content"]

        if not isinstance(content, str):
            continue

        if not content.strip():
            continue

        cleaned.append({
            "role": msg["role"],
            "content": content.strip()
        })

    system_msgs = [m for m in cleaned if m["role"] == "system"]
    normal_msgs = [m for m in cleaned if m["role"] != "system"]

    normal_msgs = normal_msgs[-MAX_HISTORY:]

    return system_msgs + normal_msgs

# ============================================================
#  API CALL
# ============================================================

def call_api(messages, retries=3):

    trimmed = trim_history(messages)

    payload = {
        "model": "gpt-4o-mini",
        "messages": trimmed,
        "temperature": 0.7,
        "max_tokens": 250
    }

    for attempt in range(retries):

        try:

            r = requests.post(
                API_URL,
                json=payload,
                headers=HEADERS,
                timeout=45
            )

            print("\n===================")
            print("STATUS:", r.status_code)
            print("TEXT:", r.text)
            print("===================\n")

            if r.status_code != 200:
                return f"⚠️ שגיאת שרת ({r.status_code})"

            try:
                data = r.json()
            except:
                return "⚠️ השרת החזיר תשובה לא תקינה"

            if (
                isinstance(data, dict)
                and "choices" in data
                and len(data["choices"]) > 0
            ):

                choice = data["choices"][0]

                if (
                    "message" in choice
                    and isinstance(choice["message"], dict)
                ):

                    content = choice["message"].get("content", "")

                    if (
                        isinstance(content, str)
                        and content.strip()
                    ):

                        return content.strip()

            # fallback אם המודל מחזיר ריק
            last_user = None

            for msg in reversed(trimmed):

                if msg["role"] == "user":
                    last_user = msg
                    break

            if last_user:

                payload["messages"] = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    last_user
                ]

        except requests.exceptions.Timeout:

            if attempt == retries - 1:
                return "⏱️ השרת עמוס כרגע, נסה שוב בעוד רגע"

        except Exception as e:

            print("ERROR:", str(e))

            if attempt == retries - 1:
                return f"❌ שגיאה: {str(e)}"

    return "🙏 לא הצלחתי לענות כרגע"

# ============================================================
#  PAGE
# ============================================================

logo_b64 = get_logo_b64()

st.set_page_config(
    page_title=f"{GYM_NAME} | בוט כושר",
    page_icon="💪",
    layout="centered"
)

# ============================================================
#  CSS
# ============================================================

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

body {{
    direction: rtl;
}}

#MainMenu,
footer,
header {{
    visibility: hidden;
}}

{bg_css}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.85);
    z-index: 0;
    pointer-events: none;
}}

.block-container {{
    position: relative;
    z-index: 1;
    padding: 0 1rem 5rem 1rem !important;
}}

.chat-wrap {{
    background: rgba(236,229,221,0.95);
    border-radius: 12px;
    padding: 10px;
}}

.msg-user {{
    background: #DCF8C6;
    padding: 10px;
    border-radius: 12px;
    margin: 8px 0 8px auto;
    max-width: 80%;
    width: fit-content;
    text-align: right;
}}

.msg-bot {{
    background: white;
    padding: 10px;
    border-radius: 12px;
    margin: 8px auto 8px 0;
    max-width: 80%;
    width: fit-content;
    text-align: right;
    border-right: 3px solid #c0392b;
}}

.msg-wrapper-user {{
    display: flex;
    justify-content: flex-end;
}}

.msg-wrapper-bot {{
    display: flex;
    justify-content: flex-start;
}}

.thinking-box {{
    background: white;
    padding: 10px 15px;
    border-radius: 12px;
    border-right: 3px solid #c0392b;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================
#  HEADER
# ============================================================

st.markdown(f"""
<h2 style='text-align:center;color:white;'>
💪 {GYM_NAME}
</h2>
""", unsafe_allow_html=True)

# ============================================================
#  SESSION
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "assistant",
            "content": f"היי 👋 ברוך הבא ל-{GYM_NAME}! איך אפשר לעזור לך היום? 💪"
        }
    ]

# ============================================================
#  CHAT DISPLAY
# ============================================================

st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    content = msg["content"]

    if msg["role"] == "user":

        st.markdown(
            f'<div class="msg-wrapper-user"><div class="msg-user">{content}</div></div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="msg-wrapper-bot"><div class="msg-bot">{content}</div></div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
#  CHAT INPUT
# ============================================================

if prompt := st.chat_input(f"שאל את {TRAINER_NAME} 💪"):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    thinking = st.empty()

    thinking.markdown(
        '<div class="msg-wrapper-bot"><div class="thinking-box">🔥 בן חושב...</div></div>',
        unsafe_allow_html=True
    )

    reply = call_api(st.session_state.messages)

    thinking.empty()

    if reply and reply.strip():

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply.strip()
        })

    else:

        st.session_state.messages.append({
            "role": "assistant",
            "content": "🙏 לא הצלחתי לענות, נסה שוב"
        })

    st.rerun()

# ============================================================
#  SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(f"## {GYM_NAME}")

    st.markdown("💪 STRENGTH › FOCUS › RESULTS")

    st.markdown(f"📞 {TRAINER_NAME}: {TRAINER_PHONE}")

    st.divider()

    if st.button("🗑 שיחה חדשה"):

        st.session_state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        st.rerun()
