# app.py
import streamlit as st
import pandas as pd
import numpy as np
import time
import io
from datetime import datetime
import matplotlib.pyplot as plt
import base64
import json

st.set_page_config(page_title="DigiKumbh — Smart Mahakumbh Assistant", layout="wide")

# ---------------------------
# DARK THEME CSS (govt-like)
# ---------------------------
dark_css = """
<style>
html, body, [class*="css"]  {
    background-color: #071427 !important;
    color: #eef6ff !important;
}
.stButton>button {
    background-color:#0b5f73;
    color: white;
}
.card {
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 14px;
}
.app-header {
    font-size:22px;
    font-weight:700;
    color:#dff3ff;
}
.small-muted { color: #9ecddf; opacity:0.8; }
.kpi { background: rgba(255,255,255,0.03); padding:10px; border-radius:10px; }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ---------------------------
# Utility functions
# ---------------------------
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_json_if_exists(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

# ---------------------------
# Initialize session state (simple in-memory DB for demo)
# ---------------------------
if "clean_reports" not in st.session_state:
    st.session_state.clean_reports = load_json_if_exists("data/cleanliness.json", [
        {"location":"Ghat A - Sector 1","issue":"Overflowing dustbin","time":now()},
        {"location":"Near Main Gate","issue":"Water puddles","time":now()}
    ])

if "lostfound" not in st.session_state:
    st.session_state.lostfound = load_json_if_exists("data/lostfound.json", [
        {"item":"Black mobile","desc":"OnePlus 8, cover","location":"Ghat B","time":now()},
    ])

if "alerts" not in st.session_state:
    st.session_state.alerts = load_json_if_exists("data/alerts.json", [
        {"type":"SOS","from":"User_123","location":"Sector 4","time":now(),"message":"Help required, injury"}
    ])

if "broadcasts" not in st.session_state:
    st.session_state.broadcasts = load_json_if_exists("data/broadcasts.json", [
        {"message":"Please follow the signage near Ghat C","time":now()}
    ])

# Sample heatmap points (lat, lon, intensity) — demo only
if "heatmap_points" not in st.session_state:
    st.session_state.heatmap_points = [
        (23.178, 75.775, 0.9),
        (23.179, 75.777, 0.7),
        (23.177, 75.776, 0.5),
        (23.176, 75.778, 0.4),
        (23.175, 75.774, 0.3)
    ]

# ---------------------------
# Sidebar / Header
# ---------------------------
st.markdown('<div class="app-header">DIGIKUMBH — Smart Mahakumbh Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="small-muted">Prototype — User & Admin demo • Govt-style dark UI</div><hr>', unsafe_allow_html=True)

role = st.sidebar.radio("Choose role", ["Devotee (User)", "Admin / Control Room", "About / Docs"])

# Quick top KPIs (left)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="kpi">Active Reports<br><b>{}</b></div>'.format(len(st.session_state.clean_reports)), unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi">Lost&Found Items<br><b>{}</b></div>'.format(len(st.session_state.lostfound)), unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi">Open Alerts<br><b>{}</b></div>'.format(len(st.session_state.alerts)), unsafe_allow_html=True)

st.write("")  # spacer

# ---------------------------
# ASK KumbhAI (mock)
# ---------------------------
def kumbhai_answer(query):
    q = query.lower()
    # small rule-based responses for demo
    if "dates" in q or "mahakumbh" in q:
        return "Simhastha 2028: Dates will be published by organizers. (Demo answer)"
    if "toilet" in q or "washroom" in q:
        return "Nearest toilets: Ghat A (200m), Ghat B (350m). Shows on map in prototype."
    if "medical" in q or "hospital" in q:
        return "Medical first aid tents available at Main Gate and Sector 4. SOS sends exact location to Control Room."
    if "darshan" in q:
        return "Live darshan link is available in the app (demo placeholder)."
    return "Sorry — demo answer: please refer to the information desk or the app's live help."

# ---------------------------
# Devotee / User flows
# ---------------------------
if role == "Devotee (User)":
    st.markdown("## 👣 Devotee — Quick actions", unsafe_allow_html=True)
    left, right = st.columns([2,1])
    with left:
        st.markdown("### Ask KumbhAI (demo)")
        q = st.text_input("Type your question (e.g., 'Where is toilet?')", key="ask_kumbhai")
        if st.button("Ask"):
            if not q:
                st.warning("Please type a question.")
            else:
                with st.spinner("KumbhAI thinking..."):
                    time.sleep(0.6)
                    ans = kumbhai_answer(q)
                st.markdown(f"**Q:** {q}")
                st.info(ans)

        st.markdown("---")
        st.markdown("### Report Cleanliness")
        with st.form(key="clean_form"):
            c_loc = st.text_input("Location (e.g., Ghat A - Sector 1)")
            c_issue = st.text_area("Describe issue (overflowing bin, water, garbage...)")
            submitted = st.form_submit_button("Submit Report")
            if submitted:
                if not c_loc or not c_issue:
                    st.error("Please fill location and description.")
                else:
                    item = {"location":c_loc, "issue":c_issue, "time":now()}
                    st.session_state.clean_reports.append(item)
                    st.success("✅ Report submitted. Admin will see this in control room.")
                    st.experimental_rerun()

        st.markdown("---")
        st.markdown("### Lost & Found — Report item")
        with st.form(key="lost_form"):
            lf_item = st.text_input("Item title (e.g., Black mobile)")
            lf_desc = st.text_area("Details (colors, marks, where lost)")
            lf_loc = st.text_input("Last seen location (Ghat / Sector)")
            lf_sub = st.form_submit_button("Submit Lost Item")
            if lf_sub:
                if not lf_item or not lf_loc:
                    st.error("Please fill item and location.")
                else:
                    st.session_state.lostfound.append({"item":lf_item,"desc":lf_desc,"location":lf_loc,"time":now()})
                    st.success("✅ Lost item submitted. Admin can monitor this.")
                    st.experimental_rerun()

        st.markdown("---")
        st.markdown("### Live Darshan (placeholder)")
        st.info("Live Darshan: [Demo video placeholder]. In real app this will embed the official stream.")
        st.button("Play demo stream (placeholder)")

    with right:
        st.markdown("### Map & Heatmap (static demo)")
        st.markdown("Click to generate current heatmap snapshot (demo).")
        if st.button("Show Heatmap"):
            # generate simple heatmap
            xs = np.random.normal(0,1,200)+2
            ys = np.random.normal(0,1,200)+2
            fig, ax = plt.subplots(figsize=(4,4))
            ax.hist2d(xs, ys, bins=30, cmap='magma')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title("Demo crowd heatmap snapshot")
            st.pyplot(fig)

        st.markdown("---")
        st.markdown("### SOS / Emergency")
        if st.button("Send SOS (demo)"):
            # simulate sending alert
            st.session_state.alerts.append({"type":"SOS","from":"DemoUser","location":"Sector X","time":now(),"message":"Demo SOS triggered"})
            st.success("✅ SOS sent. Control Room notified.")

        st.markdown("---")
        st.markdown("### My reports (recent)")
        df = pd.DataFrame(st.session_state.clean_reports).tail(6)
        st.table(df)

# ---------------------------
# Admin / Control Room flows
# ---------------------------
elif role == "Admin / Control Room":
    st.markdown("## 🛡️ Admin / Control Room", unsafe_allow_html=True)
    password = st.text_input("Enter admin passphrase (demo)", type="password")
    # for prototype keep a simple pass
    if password != "digikumbh-admin":
        st.warning("Enter admin passphrase to view control features. (demo pass: digikumbh-admin)")
    else:
        colA, colB = st.columns([2,1])
        with colA:
            st.markdown("### Live Alerts Console")
            if st.session_state.alerts:
                for i, a in enumerate(reversed(st.session_state.alerts)):
                    st.markdown(f"**{a['type']}** — {a['from']} — {a['location']} — {a['time']}")
                    st.write(a.get("message",""))
                    if st.button(f"Mark resolved #{len(st.session_state.alerts)-i}", key=f"res{i}"):
                        st.session_state.alerts.pop(len(st.session_state.alerts)-1-i)
                        st.success("Marked resolved.")
                        st.experimental_rerun()
            else:
                st.info("No active alerts.")

            st.markdown("---")
            st.markdown("### Lost & Found Monitor")
            if st.session_state.lostfound:
                lf_df = pd.DataFrame(st.session_state.lostfound)
                st.table(lf_df.tail(10))
            else:
                st.info("No lost/found entries.")

            st.markdown("---")
            st.markdown("### Cleanliness Reports")
            cr_df = pd.DataFrame(st.session_state.clean_reports)
            st.table(cr_df.tail(10))

        with colB:
            st.markdown("### Broadcast (send announcement)")
            with st.form("broadcast_form"):
                msg = st.text_area("Message to broadcast (demo)")
                send = st.form_submit_button("Broadcast")
                if send:
                    st.session_state.broadcasts.append({"message":msg,"time":now()})
                    st.success("Broadcast added (demo).")
                    st.experimental_rerun()

            st.markdown("---")
            st.markdown("### Heatmap snapshot (admin view)")
            if st.button("Generate Admin Heatmap"):
                # Create heatmap from sample points
                points = st.session_state.heatmap_points
                # Convert to grid
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                # simple scatter + intensity demo
                fig2, ax2 = plt.subplots(figsize=(5,4))
                ax2.scatter(xs, ys, s=[p[2]*500 for p in points], c='red', alpha=0.6)
                ax2.set_title("Admin heatmap demo (points demo)")
                ax2.set_xticks([])
                ax2.set_yticks([])
                st.pyplot(fig2)

            st.markdown("---")
            st.markdown("### Recent Broadcasts")
            for b in reversed(st.session_state.broadcasts[-6:]):
                st.write(f"- {b['time']} — {b['message']}")

# ---------------------------
# About / Docs
# ---------------------------
else:
    st.markdown("## 📘 About DigiKumbh (Prototype)")
    st.markdown("""
**DigiKumbh** — Smart Mahakumbh Assistant  
Prototype highlights:
- Dual-role demo: *Devotee* & *Admin/Control Room*.  
- Features demo: Ask KumbhAI (mock), Report Cleanliness, Lost & Found, SOS, Live Darshan placeholder, Map+Heatmap demo, Admin alerts, Broadcast.  
- Demo uses local in-memory data (session_state) or optional `data/*.json` files in repo root if present.  
- Intended as a prototype to show UI/UX & feature flow.  
    """)
    st.markdown("### How to run (Streamlit) — quick")
    st.code("""
# 1) Create virtualenv, install:
pip install -r requirements.txt

# 2) Run:
streamlit run app.py
    """)
    st.markdown("### Notes")
    st.markdown("- Admin passphrase (demo): `digikumbh-admin` (only for prototype).")
    st.markdown("- To persist demo data between restarts, add `data/cleanliness.json`, `data/lostfound.json`, `data/alerts.json` files in repo root (same structure as sample shown while using app).")

# ---------------------------
# Save JSON helpers (optional)
# ---------------------------
# Provide a small 'Export demo data' option in footer for judges to download current state
st.markdown("<hr>", unsafe_allow_html=True)
if st.button("Download current demo data (JSON)"):
    export = {
        "clean_reports": st.session_state.clean_reports,
        "lostfound": st.session_state.lostfound,
        "alerts": st.session_state.alerts,
        "broadcasts": st.session_state.broadcasts
    }
    b = json.dumps(export, indent=2)
    st.download_button(label="Download JSON", data=b, file_name="digikumbh_demo_data.json", mime="application/json")
