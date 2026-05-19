import streamlit as st
import requests
import os
import base64
from datetime import datetime

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

# system prompt קצר מאוד — חוסך טוקנים שלא ילכו ל-reasoning
SYSTEM_PROMPT = f"אתה בוט תמיכה של {COMPANY_NAME}. ענה בעברית, קצר (2 משפטים). אבחן: וידאו/אודיו/פלטפורמה/אחר."

def call_api_smart(messages):
    """
    פתרון לבועות ריקות (אותו פתרון כמו במאמן):
    - max_tokens גבוה (4000) - לתת מקום ל-reasoning tokens + תשובה
    - היסטוריה מינימלית (3 הודעות) - להימנע מהצטברות
    - 2 ניסיונות
    """
    system = [m for m in messages if m["role"] == "system"]
    others = [m for m in messages if m["role"] != "system"]
    recent = system + others[-3:]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": recent,
        "max_tokens": 4000
    }
    
    # ניסיון 1
    try:
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=90)
        data = r.json()
        if "choices" in data:
            content = data["choices"][0]["message"].get("content", "")
            if content and content.strip():
                return content.strip()
    except Exception as e:
        return f"שגיאה: {str(e)[:100]}"
    
    # ניסיון 2 - רק השאלה האחרונה
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

def analyze_image(image_b64, mime, description):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": description or "תנתח את התמונה ואבחן את התקלה"},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}}
            ]}
        ],
        "max_tokens": 4000
    }
    try:
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=90)
        data = r.json()
        if "choices" in data:
            content = data["choices"][0]["message"].get("content", "")
            if content and content.strip():
                return content.strip()
    except:
        pass
    return "לא הצלחתי לנתח את התמונה, נסה שוב"

logo_b64 = ""
if os.path.exists("logo.jpg"):
    with open("logo.jpg", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

st.set_page_config(page_title=COMPANY_NAME, page_icon="🎯", layout="centered")

bg = f'background-image: url("data:image/jpeg;base64,{logo_b64}"); background-size: 45%; background-position: center; background-repeat: no-repeat; background-attachment: fixed;' if logo_b64 else ''

st.markdown(f"""
<style>
    body {{ direction: rtl; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stApp {{ background: #0a0e1a; {bg} }}
    .stApp::before {{ content: ""; position: fixed; inset: 0; background: rgba(10,14,26,0.88); z-index: 0; pointer-events: none; }}
    .block-container {{ position: relative; z-index: 1; padding: 0 1rem 5rem !important; max-width: 100% !important; }}
    
    .wa-header {{ background: linear-gradient(90deg, #d4ff00 0%, #aacc00 100%); color: #000; padding: 12px 16px; display: flex; align-items: center; gap: 12px; margin: -1rem -1rem 1rem; border-bottom: 3px solid #000; z-index: 10; box-shadow: 0 4px 20px rgba(212,255,0,0.3); }}
    .wa-name {{ font-weight: bold; font-size: 16px; color: #000; }}
    .wa-status {{ font-size: 12px; color: #333; }}
    
    .ticket-badge {{ background: rgba(212,255,0,0.15); border: 1px solid rgba(212,255,0,0.4); border-radius: 8px; padding: 8px 12px; color: #d4ff00; font-size: 13px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
    
    .chat-wrap {{ background: rgba(236,229,221,0.95); border-radius: 12px; padding: 10px; margin-bottom: 10px; }}
    .msg-user {{ background: #DCF8C6; padding: 8px 12px; border-radius: 12px 2px 12px 12px; margin: 6px 0 6px auto; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; word-break: break-word; white-space: pre-wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }}
    .msg-bot {{ background: white; padding: 8px 12px; border-radius: 2px 12px 12px 12px; margin: 6px auto 6px 0; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; border-right: 3px solid #d4ff00; word-break: break-word; white-space: pre-wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }}
    .msg-time {{ font-size: 11px; color: #999; margin-top: 3px; }}
    .msg-wrapper-user {{ display: flex; justify-content: flex-end; width: 100%; }}
    .msg-wrapper-bot {{ display: flex; justify-content: flex-start; width: 100%; }}
    
    .thinking {{ background: white; padding: 10px 16px; margin: 6px auto 6px 0; width: fit-content; border-radius: 2px 12px 12px 12px; border-right: 3px solid #d4ff00; font-weight: bold; color: #000; animation: pulse 1s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    
    .stButton > button {{ background: transparent !important; color: #d4ff00 !important; border: 1px solid rgba(212,255,0,0.4) !important; border-radius: 8px !important; padding: 8px 16px !important; font-size: 13px !important; width: 100% !important; }}
    .stButton > button:hover {{ color: #000 !important; background: #d4ff00 !important; border-color: #d4ff00 !important; }}
    
    section[data-testid="stSidebar"] {{ background: rgba(15,20,35,0.97) !important; }}
    section[data-testid="stSidebar"] * {{ color: white !important; }}
    
    .stSelectbox label, .stFileUploader label, .stTextArea label {{ color: #d4ff00 !important; }}
    
    .feedback-box {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; text-align: center; margin: 10px 0; }}
    .feedback-box h3 {{ color: #000; margin: 0 0 10px; }}
</style>
""", unsafe_allow_html=True)

if "ticket_id" not in st.session_state:
    st.session_state.ticket_id = f"WSC-{datetime.now().strftime('%H%M%S')}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": f"שלום! 👋 אני בוט התמיכה של {COMPANY_NAME}.\nתאר את התקלה ואשמח לעזור 🎯"}
    ]
    st.session_state.transferred = False
    st.session_state.show_feedback = False
    st.session_state.rating = 0

avatar = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:42px;height:42px;border-radius:8px;border:2px solid #000;">' if logo_b64 else "🎯"
st.markdown(f'<div class="wa-header">{avatar}<div style="flex:1;"><div class="wa-name">{COMPANY_NAME} Support</div><div class="wa-status">⚡ תמיכה טכנית | מחובר</div></div><div style="font-size:11px;background:rgba(0,0,0,0.15);padding:4px 10px;border-radius:12px;color:#000;">● ONLINE</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ticket-badge"><span>📋 <strong>פנייה {st.session_state.ticket_id}</strong></span><span style="opacity:0.7;">{datetime.now().strftime("%H:%M")}</span></div>', unsafe_allow_html=True)

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

with st.expander("📎 פתח פנייה מסווגת (קטגוריה + קובץ)"):
    category = st.selectbox("סוג התקלה:", ["—", "בעיה בוידאו", "בעיה באודיו", "בעיה בפלטפורמה", "שאלה תפעולית", "אחר"])
    uploaded = st.file_uploader("צרף צילום מסך / וידאו:", type=["jpg", "jpeg", "png", "mp4", "mov"])
    
    if uploaded:
        if uploaded.type.startswith("image"):
            st.image(uploaded, width=250)
        else:
            st.video(uploaded)
    
    description = st.text_area("תיאור:", placeholder="תאר את התקלה...", height=80)
    
    if st.button("📤 שלח פנייה"):
        if description or uploaded or category != "—":
            full_text = f"[{category}] {description}" if category != "—" else description
            if not full_text:
                full_text = f"[{category}] שליחת קובץ" if category != "—" else "שליחת קובץ"
            
            st.session_state.messages.append({"role": "user", "content": full_text})
            
            with st.spinner("🔍 מנתח..."):
                if uploaded and uploaded.type.startswith("image"):
                    img_b64 = base64.b64encode(uploaded.read()).decode()
                    mime = "image/jpeg" if uploaded.name.lower().endswith(("jpg", "jpeg")) else "image/png"
                    reply = analyze_image(img_b64, mime, full_text)
                else:
                    reply = call_api_smart(st.session_state.messages)
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

if not st.session_state.transferred and not st.session_state.show_feedback:
    if st.button(f"🔼 הסלם לנציג תמיכה אנושי"):
        st.session_state.transferred = True
        user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        summary = f"פנייה {st.session_state.ticket_id} | {len(user_msgs)} הודעות"
        wa = f"https://wa.me/972{SUPPORT_PHONE[1:]}?text=שלום,+פנייה+{st.session_state.ticket_id}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": f'הפנייה מועברת לנציג 🔼\n📋 תקציר: {summary}\n<a href="{wa}" target="_blank" style="color:#d4ff00;font-weight:bold;">💬 לחץ כאן</a>'
        })
        st.session_state.show_feedback = True
        st.rerun()

if not st.session_state.show_feedback:
    if prompt := st.chat_input("תאר את התקלה... 🎯"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        think = st.empty()
        think.markdown('<div class="msg-wrapper-bot"><div class="thinking">🔍 מנתח תקלה...</div></div>', unsafe_allow_html=True)
        
        reply = call_api_smart(st.session_state.messages)
        
        think.empty()
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

if st.session_state.show_feedback and st.session_state.rating == 0:
    st.markdown('<div class="feedback-box"><h3>⭐ דרג את חוויית השירות</h3></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, col in enumerate(cols, 1):
        with col:
            if st.button(f"{'⭐' * i}", key=f"rate_{i}"):
                st.session_state.rating = i
                st.rerun()

if st.session_state.rating > 0:
    st.success(f"✅ תודה! דירוג: {'⭐' * st.session_state.rating} ({st.session_state.rating}/5)")

with st.sidebar:
    if logo_b64:
        st.image("logo.jpg", use_container_width=True)
    st.markdown(f"### 🎯 {COMPANY_NAME}")
    st.markdown("**Technical Support 24/7**")
    st.divider()
    st.markdown(f"**🎫 פנייה:**")
    st.code(st.session_state.ticket_id)
    st.markdown(f"📞 {SUPPORT_PHONE}")
    st.divider()
    st.markdown("**📊 קטגוריות:**")
    st.markdown("🎬 וידאו | 🔊 אודיו")
    st.markdown("💻 פלטפורמה | ❓ תפעולי")
    st.divider()
    if st.button("🔄 פנייה חדשה"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"שלום! 👋 ברוך הבא ל-{COMPANY_NAME}.\nתאר את התקלה 🎯"}
        ]
        st.session_state.transferred = False
        st.session_state.show_feedback = False
        st.session_state.rating = 0
        st.session_state.ticket_id = f"WSC-{datetime.now().strftime('%H%M%S')}"
        st.rerun()
    st.divider()
    st.caption("**פרויקט גמר**")
    st.caption("חיים עוליאל | נועם קיש")
    st.caption("בהנחיית: אריה עמית")
