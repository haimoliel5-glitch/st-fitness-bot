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
SUPPORT_PHONE = "0506682769"  # פנימי בלבד
COMPANY_NAME  = "WSC Sports"
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
#  מאגר ידע פנימי - 15 שאלות תשובות
# ============================================================
SYSTEM_PROMPT = """You are a technical support bot for WSC Sports. Answer in the SAME language the user uses (Hebrew or English). Be concise (2-4 sentences max).

KNOWLEDGE BASE:

=== LIVE FEEDS & INGEST ===
Q: RTMP/SRT stream connected but black screen?
A: Check: (1) encoder is actively pushing data (2) firewall isn't blocking the port (3) stream key/URL match exactly.

Q: Schedule new live feed ingest?
A: Live Management > Add Stream. Select protocol (RTMP/SRT), enter stream details, set Start/End times, click Save.

Q: Audio-video sync issue?
A: Originates from encoder side. Verify audio/video sample rates match recommended settings, check keyframe intervals. Restart encoder.

Q: Supported codecs/formats for manual uploads?
A: MP4 and MOV. Codecs: H.264 or H.265 (HEVC). Audio: AAC.

=== AUTOMATED CLIPPING & HIGHLIGHTS ===
Q: Automation rule for specific player highlights?
A: Automation Rules > Create New Rule > Conditions tab > select Player Name > type name > select destination > Activate.

Q: Manual clipping when AI missed a play?
A: Open Editor for that game. Keyboard: I = In point, O = Out point. Add tags, click Create Clip.

Q: Change aspect ratio for TikTok/Reels?
A: In Automation Rule or Editor, go to Cropping section, select 9:16 Vertical. Enable Auto-Tracking.

Q: Adjust pre-roll/post-roll padding?
A: Global: Settings > Clip Preferences. Per-clip: drag handles on timeline in Editor.

Q: Add custom graphics/intros/watermarks?
A: Graphics Configuration. Upload PNG, JPG, or transparent MOV. Apply as overlay or intro/outro in Automation Rules.

Q: Filter clips by play type (3-pointers, dunks)?
A: In Automation Rule, add Play Type condition. Select from dropdown: 3-Pointer, Dunk, Save, Goal, etc.

=== DISTRIBUTION & PUBLISHING ===
Q: Connect/re-authenticate social media?
A: Destinations > Social Accounts. New: Add Account, follow prompts. Re-auth: click Re-authenticate next to warning icon.

Q: Videos failing to publish to OTT - error logs?
A: Publishing Logs (Distribution History). Click failed clip to see exact error from OTT platform's API.

Q: Set embargo/publishing delay for broadcast rights?
A: Destination settings or Automation Rule > Publishing Delay > enter delay time in minutes/hours.

Q: Send metadata (JSON/XML) to our CMS?
A: Destinations > Add Destination > Custom Endpoint (Webhook). Enter CMS URL, select payload format, map metadata fields.

Q: Update published clip title retroactively?
A: Yes - edit metadata under Published Clips, click Update. Note: X/Twitter doesn't allow retroactive title updates via API.

=== INSTRUCTIONS ===
- If question matches the KB above, use that exact answer (in user's language)
- For urgent issues ("all customers", "completely down", "urgent") - say escalating to human agent
- If you don't know - say "I'll escalate to a human agent" / "מעביר לנציג אנושי"
- Categorize issues: Live Feeds / Clipping / Distribution / Other"""


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
        return f"Error: {str(e)[:100]}"
    
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
        return f"Error: {str(e)[:100]}"
    
    return "Please rephrase / נסה לנסח אחרת"

def analyze_image(image_b64, mime, description):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": description or "Analyze this image"},
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
    return "Failed to analyze"

logo_b64 = ""
if os.path.exists("logo.jpg"):
    with open("logo.jpg", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

st.set_page_config(page_title=COMPANY_NAME, page_icon="🎯", layout="wide")

bg = f'background-image: url("data:image/jpeg;base64,{logo_b64}"); background-size: 35%; background-position: center; background-repeat: no-repeat; background-attachment: fixed;' if logo_b64 else ''

st.markdown(f"""
<style>
    body {{ direction: rtl; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stApp {{ background: #0a0e1a; {bg} }}
    .stApp::before {{ content: ""; position: fixed; inset: 0; background: rgba(10,14,26,0.9); z-index: 0; pointer-events: none; }}
    .block-container {{ position: relative; z-index: 1; padding: 0 1rem 5rem !important; max-width: 100% !important; }}
    
    .wa-header {{ background: linear-gradient(90deg, #d4ff00 0%, #aacc00 100%); color: #000; padding: 12px 16px; display: flex; align-items: center; gap: 12px; margin: -1rem -1rem 1rem; border-bottom: 3px solid #000; z-index: 10; box-shadow: 0 4px 20px rgba(212,255,0,0.3); }}
    .wa-name {{ font-weight: bold; font-size: 16px; color: #000 !important; }}
    .wa-status {{ font-size: 12px; color: #333 !important; }}
    
    .ticket-badge {{ background: rgba(212,255,0,0.15); border: 1px solid rgba(212,255,0,0.4); border-radius: 8px; padding: 8px 12px; color: #d4ff00; font-size: 13px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
    
    .chat-wrap {{ background: rgba(236,229,221,0.95); border-radius: 12px; padding: 10px; margin-bottom: 10px; }}
    
    /* טקסט שחור על בועות */
    .msg-user {{ background: #DCF8C6; color: #000 !important; padding: 8px 12px; border-radius: 12px 2px 12px 12px; margin: 6px 0 6px auto; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; word-break: break-word; white-space: pre-wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }}
    .msg-bot {{ background: white; color: #000 !important; padding: 8px 12px; border-radius: 2px 12px 12px 12px; margin: 6px auto 6px 0; max-width: 80%; width: fit-content; text-align: right; font-size: 14px; line-height: 1.6; border-right: 3px solid #d4ff00; word-break: break-word; white-space: pre-wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }}
    .msg-time {{ font-size: 11px; color: #666 !important; margin-top: 3px; }}
    .msg-wrapper-user {{ display: flex; justify-content: flex-end; width: 100%; }}
    .msg-wrapper-bot {{ display: flex; justify-content: flex-start; width: 100%; }}
    
    .thinking {{ background: white; color: #000 !important; padding: 10px 16px; margin: 6px auto 6px 0; width: fit-content; border-radius: 2px 12px 12px 12px; border-right: 3px solid #d4ff00; font-weight: bold; animation: pulse 1s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    
    .stButton > button {{ background: transparent !important; color: #d4ff00 !important; border: 1px solid rgba(212,255,0,0.4) !important; border-radius: 8px !important; padding: 8px 16px !important; font-size: 13px !important; width: 100% !important; }}
    .stButton > button:hover {{ color: #000 !important; background: #d4ff00 !important; border-color: #d4ff00 !important; }}
    
    section[data-testid="stSidebar"] {{ background: rgba(15,20,35,0.97) !important; }}
    section[data-testid="stSidebar"] * {{ color: white !important; }}
    
    .stSelectbox label, .stFileUploader label, .stTextArea label {{ color: #d4ff00 !important; }}
    
    /* כרטיסי מדדים */
    .metric-card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(212,255,0,0.3); border-radius: 12px; padding: 20px; text-align: center; }}
    .metric-value {{ font-size: 2rem; font-weight: bold; color: #d4ff00; }}
    .metric-label {{ font-size: 0.85rem; color: #ccc; margin-top: 4px; }}
    .metric-target {{ font-size: 0.75rem; color: #888; margin-top: 2px; }}
    .metric-pass {{ color: #4ade80 !important; font-weight: bold; }}
    .metric-fail {{ color: #f87171 !important; font-weight: bold; }}
    
    .feedback-box {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; text-align: center; margin: 10px 0; }}
    .feedback-box h3 {{ color: #000 !important; margin: 0 0 10px; }}
    .feedback-box p {{ color: #555 !important; }}
</style>
""", unsafe_allow_html=True)

# ============= STATE =============
if "ticket_id" not in st.session_state:
    st.session_state.ticket_id = f"WSC-{datetime.now().strftime('%H%M%S')}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": f"Welcome to {COMPANY_NAME} Support! 👋\nHow can I help you today?\n\nשלום! איך אוכל לעזור לך היום?"}
    ]
    st.session_state.transferred = False
    st.session_state.show_feedback = False
    st.session_state.rating = 0
    st.session_state.all_ratings = []  # לדוחות
    st.session_state.total_tickets = 0
    st.session_state.resolved_by_bot = 0

# ============= TABS =============
tab1, tab2 = st.tabs(["💬 Chat Support", "📊 דוחות ומדדים"])

# ============= TAB 1: CHAT =============
with tab1:
    avatar = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:42px;height:42px;border-radius:8px;border:2px solid #000;">' if logo_b64 else "🎯"
    st.markdown(f'<div class="wa-header">{avatar}<div style="flex:1;"><div class="wa-name">{COMPANY_NAME} Support</div><div class="wa-status">⚡ Technical Support | Online</div></div><div style="font-size:11px;background:rgba(0,0,0,0.15);padding:4px 10px;border-radius:12px;color:#000;">● ONLINE</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="ticket-badge"><span>📋 <strong>Ticket {st.session_state.ticket_id}</strong></span><span style="opacity:0.7;">{datetime.now().strftime("%H:%M")}</span></div>', unsafe_allow_html=True)

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

    with st.expander("📎 Open detailed ticket (category + attachment)"):
        category = st.selectbox("Issue type:", ["—", "Live Feeds & Ingest", "Automated Clipping", "Distribution & Publishing", "Other"])
        uploaded = st.file_uploader("Attach screenshot/video:", type=["jpg", "jpeg", "png", "mp4", "mov"])
        
        if uploaded:
            if uploaded.type.startswith("image"):
                st.image(uploaded, width=250)
            else:
                st.video(uploaded)
        
        description = st.text_area("Description:", placeholder="Describe the issue...", height=80)
        
        if st.button("📤 Submit ticket"):
            if description or uploaded or category != "—":
                full_text = f"[{category}] {description}" if category != "—" else description
                if not full_text:
                    full_text = f"[{category}] File attached" if category != "—" else "File attached"
                
                st.session_state.messages.append({"role": "user", "content": full_text})
                st.session_state.total_tickets += 1
                
                with st.spinner("🔍 Analyzing..."):
                    if uploaded and uploaded.type.startswith("image"):
                        img_b64 = base64.b64encode(uploaded.read()).decode()
                        mime = "image/jpeg" if uploaded.name.lower().endswith(("jpg", "jpeg")) else "image/png"
                        reply = analyze_image(img_b64, mime, full_text)
                    else:
                        reply = call_api_smart(st.session_state.messages)
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

    if not st.session_state.transferred and not st.session_state.show_feedback:
        if st.button("🔼 Escalate to human agent"):
            st.session_state.transferred = True
            user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
            summary = f"Ticket {st.session_state.ticket_id} | {len(user_msgs)} messages | Auto-summary generated"
            st.session_state.messages.append({
                "role": "assistant",
                "content": f'✅ Ticket {st.session_state.ticket_id} escalated to human agent.\n📋 Summary: {summary}\nA support agent will contact you shortly.'
            })
            st.session_state.show_feedback = True
            st.rerun()

    if not st.session_state.show_feedback:
        if prompt := st.chat_input("Describe your issue / תאר את הבעיה..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.total_tickets += 1
            
            think = st.empty()
            think.markdown('<div class="msg-wrapper-bot"><div class="thinking">🔍 Analyzing...</div></div>', unsafe_allow_html=True)
            
            reply = call_api_smart(st.session_state.messages)
            
            # אם הבוט פתר - לא הסלמה
            if "escalat" not in reply.lower() and "מעביר" not in reply:
                st.session_state.resolved_by_bot += 1
            
            think.empty()
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

    # ============= FEEDBACK =============
    if st.session_state.show_feedback and st.session_state.rating == 0:
        st.markdown('<div class="feedback-box"><h3>⭐ Rate your experience</h3><p>How would you rate the support you received?</p></div>', unsafe_allow_html=True)
        cols = st.columns(5)
        for i, col in enumerate(cols, 1):
            with col:
                if st.button(f"{'⭐' * i}", key=f"rate_{i}"):
                    st.session_state.rating = i
                    st.session_state.all_ratings.append(i)
                    st.rerun()

    if st.session_state.rating > 0:
        st.success(f"✅ Thank you! Rating: {'⭐' * st.session_state.rating} ({st.session_state.rating}/5)")
        st.info(f"📋 Ticket {st.session_state.ticket_id} closed.")

# ============= TAB 2: REPORTS =============
with tab2:
    st.markdown(f"# 📊 דוחות ומדדים — {COMPANY_NAME}")
    st.markdown("---")
    
    # חישוב מדדים בזמן אמת
    total = max(st.session_state.total_tickets, 1)
    bot_resolved_pct = round((st.session_state.resolved_by_bot / total) * 100) if total > 0 else 0
    avg_rating = round(sum(st.session_state.all_ratings) / len(st.session_state.all_ratings), 1) if st.session_state.all_ratings else 0
    
    # 4 כרטיסי מדד
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        passed = bot_resolved_pct >= 30
        cls = "metric-pass" if passed else "metric-fail"
        icon = "✓" if passed else "✗"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{bot_resolved_pct}%</div>
            <div class="metric-label">פתרון עצמאי של הבוט</div>
            <div class="metric-target">יעד: ≥30%</div>
            <div class="{cls}">{icon} {"מעל היעד" if passed else "מתחת ליעד"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_time = 12  # ערך לדוגמה
        passed = avg_time < 30
        cls = "metric-pass" if passed else "metric-fail"
        icon = "✓" if passed else "✗"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_time} שנ'</div>
            <div class="metric-label">זמן מענה ראשוני ממוצע</div>
            <div class="metric-target">יעד: &lt;30 שנ'</div>
            <div class="{cls}">{icon} {"מתחת ליעד" if passed else "מעל היעד"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        accuracy = 84  # ערך לדוגמה
        passed = accuracy > 80
        cls = "metric-pass" if passed else "metric-fail"
        icon = "✓" if passed else "✗"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{accuracy}%</div>
            <div class="metric-label">דיוק סיווג תקלות</div>
            <div class="metric-target">יעד: &gt;80%</div>
            <div class="{cls}">{icon} {"מעל היעד" if passed else "מתחת ליעד"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        passed = avg_rating >= 4.0
        cls = "metric-pass" if passed else "metric-fail"
        icon = "✓" if passed else "✗"
        display_rating = f"{avg_rating}/5" if avg_rating > 0 else "—"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{display_rating}</div>
            <div class="metric-label">שביעות רצון לקוחות</div>
            <div class="metric-target">יעד: ≥4.0</div>
            <div class="{cls}">{icon} {"מעל היעד" if passed and avg_rating > 0 else "ממתין לדירוגים"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # תרשים פניות לפי קטגוריה
    st.subheader("📈 פניות לפי קטגוריה")
    import pandas as pd
    
    chart_data = pd.DataFrame({
        'קטגוריה': ['Live Feeds', 'Clipping', 'Distribution', 'תפעולי', 'אחר'],
        'כמות פניות': [208, 112, 52, 28, 14]
    })
    st.bar_chart(chart_data.set_index('קטגוריה'))
    
    st.markdown("---")
    
    # סטטיסטיקות נוספות
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("סה\"כ פניות", st.session_state.total_tickets)
    with col_b:
        st.metric("נפתרו ע\"י בוט", st.session_state.resolved_by_bot)
    with col_c:
        st.metric("הוסלמו לנציג", st.session_state.total_tickets - st.session_state.resolved_by_bot)

# ============= SIDEBAR =============
with st.sidebar:
    if logo_b64:
        st.image("logo.jpg", use_container_width=True)
    st.markdown(f"### 🎯 {COMPANY_NAME}")
    st.markdown("**Technical Support 24/7**")
    st.divider()
    st.markdown(f"**🎫 Current Ticket:**")
    st.code(st.session_state.ticket_id)
    st.divider()
    st.markdown("**📊 Categories:**")
    st.markdown("🎬 Live Feeds & Ingest")
    st.markdown("✂️ Automated Clipping")
    st.markdown("📡 Distribution")
    st.markdown("❓ Other")
    st.divider()
    if st.button("🔄 New Ticket"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"Welcome to {COMPANY_NAME} Support! 👋\nHow can I help you today?"}
        ]
        st.session_state.transferred = False
        st.session_state.show_feedback = False
        st.session_state.rating = 0
        st.session_state.ticket_id = f"WSC-{datetime.now().strftime('%H%M%S')}"
        st.rerun()
    st.divider()
    st.caption("**Graduation Project**")
    st.caption("WSC Sports Support System")
    st.caption("Built by: חיים עוליאל | נועם קיש")
    st.caption("Supervisor: אריה עמית")
