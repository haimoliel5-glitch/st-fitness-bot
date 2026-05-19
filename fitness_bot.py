import streamlit as st
import requests
import os
import base64

# ============================================================
#  הגדרות
# ============================================================
API_URL       = "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
API_KEY       = "sk-std-NYI6dMVcFMobVTH3T8hrp2s4CWCNwJDi04ZLmflNzQU"
SUPPORT_NAME  = "נציג"
SUPPORT_PHONE = "0506682769"
COMPANY_NAME  = "WSC Sports"
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = f"אתה בוט תמיכה טכנית של {COMPANY_NAME}. ענה בעברית, מקצועי וקצר. אבחן: וידאו/אודיו/פלטפורמה/אחר."

def call_api_smart(messages):
    system = [m for m in messages if m["role"] == "system"]
    others = [m for m in messages if m["role"] != "system"]
    recent = system + others[-3:]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": recent,
        "max_tokens": 4000
    }
    
    try:
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=90)
        data = r.json()
        if "choices" in data:
            content = data["choices"][0]["message"].get("content", "")
            if content and content.strip():
                return content.strip()
    except Exception as e:
        return f"שגיאה: {str(e)[:100]}"
    
    try:
        payload["messages"] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            messages[-1]
        ]
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=90)
        data = r.json()
        if "choices" in data:
            content = data["choices"][0]["message"].get("content", "")
            if content and content.strip():
                return content.strip()
    except Exception as e:
        return f"שגיאה: {str(e)[:100]}"
    
    return "נסה לנסח את השאלה אחרת 🙏"

logo_b64 = ""
if os.path.exists("logo.jpg"):
    with open("logo.jpg", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

st.set_page_config(page_title=COMPANY_NAME, page_icon="🎯", layout="centered")

bg = f'background-image: url("data:image/jpeg;base64,{logo_b64}"); background-size: 50%; background-position: center; background-repeat: no-repeat; background-attachment: fixed;' if logo_b64 else ''

st.markdown(f"""
<style>
    body {{ direction: rtl; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stApp {{ background: #0a0e1a; {bg} }}
    .stApp::before {{ content: ""; position: fixed; inset: 0; background: rgba(10,14,26,0.85); z-index: 0; pointer-events: none; }}
    .block-container {{ position: relative; z-index: 1; padding: 0 1rem 5rem !important; max-width: 100% !important; }}
    
    .wa-header {{ background: rgba(20,30,50,0.97); color: white; padding: 12px 16px; display: flex; align-items: center; gap: 12px; margin: -1rem -1rem 1rem; border-bottom: 3px solid #0066ff; z-index: 10; }}
    .wa-name {{ font-weight: bold; font-size: 16px; }}
    .wa-status {{ font-size: 12px; color: #4a9eff; }}
    
    .chat-wrap {{ background: rgba(236,229,221,0.95); border-radius: 12px; padding: 10px; margin-bottom: 10px; }}
    .msg-user {{ background: #DCF8C6; padding: 8px 12px; border-radius: 12px 2px 12px 12px; margin: 6px 0 6px auto; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; word-break: break-word; white-space: pre-wrap; }}
    .msg-bot {{ background: white; padding: 8px 12px; border-radius: 2px 12px 12px 12px; margin: 6px auto 6px 0; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; border-right: 3px solid #0066ff; word-break: break-word; white-space: pre-wrap; }}
    .msg-time {{ font-size: 11px; color: #999; margin-top: 3px; }}
    .msg-wrapper-user {{ display: flex; justify-content: flex-end; width: 100%; }}
    .msg-wrapper-bot {{ display: flex; justify-content: flex-start; width: 100%; }}
    
    .thinking {{ background: white; padding: 10px 16px; margin: 6px auto 6px 0; width: fit-content; border-radius: 2px 12px 12px 12px; border-right: 3px solid #0066ff; font-weight: bold; color: #0066ff; animation: pulse 1s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    
    .stButton > button {{ background: transparent !important; color: #888 !important; border: 1px solid #555 !important; border-radius: 20px !important; padding: 6px 16px !important; font-size: 12px !important; width: 100% !important; }}
    .stButton > button:hover {{ color: #0066ff !important; border-color: #0066ff !important; }}
    
    section[data-testid="stSidebar"] {{ background: rgba(15,20,35,0.97) !important; }}
    section[data-testid="stSidebar"] * {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

avatar = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:42px;height:42px;border-radius:50%;border:2px solid #0066ff;">' if logo_b64 else "🎯"
st.markdown(f'<div class="wa-header">{avatar}<div><span class="wa-name">{COMPANY_NAME}</span><span class="wa-status">⚡ תמיכה טכנית | מחובר</span></div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": f"שלום! 👋 ברוך הבא לתמיכה הטכנית של {COMPANY_NAME}!\nתאר את התקלה ואשמח לעזור 🎯"}
    ]
    st.session_state.transferred = False

st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    c = msg["content"]
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-wrapper-user"><div class="msg-user">{c}<div class="msg-time">✓✓</div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-wrapper-bot"><div class="msg-bot">{c}<div class="msg-time">🎯 {COMPANY_NAME}</div></div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.transferred:
    if st.button(f"🔼 הסלם ל{SUPPORT_NAME} אנושי"):
        st.session_state.transferred = True
        wa = f"https://wa.me/972{SUPPORT_PHONE[1:]}?text=שלום,+אני+לקוח+של+{COMPANY_NAME}+וצריך+עזרה"
        st.session_state.messages.append({"role": "assistant", "content": f'בוודאי! <a href="{wa}" target="_blank" style="color:#0066ff;font-weight:bold;">💬 לחץ כאן</a>'})
        st.rerun()

if prompt := st.chat_input(f"תאר את התקלה... 🎯"):
    st.session_state.transferred = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    think = st.empty()
    think.markdown('<div class="msg-wrapper-bot"><div class="thinking">🔍 מנתח תקלה...</div></div>', unsafe_allow_html=True)
    
    reply = call_api_smart(st.session_state.messages)
    
    think.empty()
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

with st.sidebar:
    if logo_b64:
        st.image("logo.jpg", use_container_width=True)
    st.markdown(f"### {COMPANY_NAME}")
    st.markdown("🎯 Technical Support 24/7")
    st.markdown(f"📞 תמיכה: {SUPPORT_PHONE}")
    st.divider()
    if st.button("🗑 פנייה חדשה"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"שלום! 👋 ברוך הבא ל-{COMPANY_NAME}!\nתאר את התקלה 🎯"}
        ]
        st.session_state.transferred = False
        st.rerun()
