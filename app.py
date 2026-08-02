import streamlit as st
import requests
import json
import base64
import time

# ==========================================
# ⚙️ GLOBAL CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="Unified Admin Panel", 
    page_icon="⚡", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- SECRETS MANAGEMENT (DUAL TOKEN SYSTEM) ---
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    TOKEN_MAIN = st.secrets["GITHUB_TOKEN_MAIN"] # For ExamPortal (WakiLBD)
    TOKEN_PS = st.secrets["GITHUB_TOKEN_PS"]     # For PS Website (PremiumSubscriptions)
except:
    # Fallback for local testing
    ADMIN_PASSWORD = "123"
    TOKEN_MAIN = "Add_Token_Here"
    TOKEN_PS = "Add_Token_Here"

# --- REPO CONSTANTS ---
# 1. ExamPortal Config
REPO_1_OWNER = 'WakiLBD'
REPO_1_NAME = 'ExamPortal'
PATH_1_COURSE = 'src/data/CourseList.json'

# 2. PS Website Config
REPO_2_OWNER = 'PremiumSubscriptions'
REPO_2_NAME = 'ps'
PATH_2_COURSE = 'courses/courses.json'

# 3. Bot Database Config
REPO_3_OWNER = 'PremiumSubscriptions'
REPO_3_NAME = 'CourseDataDB'


# CDN Config
IMG_CDN_BASE = "https://cdn.jsdelivr.net/gh/PremiumSubscriptions/premium-subscriptions-bot@main/"

# ==========================================
# 🎨 UI & UX DESIGN SYSTEM (PREMIUM & ROBUST)
# ==========================================
def apply_custom_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* 1. FORCE LIGHT MODE & FONT SMOOTHING (Mac/Windows sync) */
        :root {
            color-scheme: light only !important;
        }
        
        .stApp, html, body {
            background-color: #F8F9FC !important;
            color: #0F172A !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            
            /* iPhone Notch & Bottom Bar Fixes */
            min-height: 100dvh !important; 
            min-height: -webkit-fill-available !important; 
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left) !important;
        }
        
        /* HEADERS */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            color: #1E293B !important;
        }
        
        /* 2. GRADIENT TEXT WITH VENDOR PREFIXES (Older Safari/Android support) */
        .gradient-text {
            color: #6366F1 !important; /* Fallback */
            background: -webkit-linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
        }

        /* 3. CARDS NORMALIZATION */
        div[data-testid="stForm"], div.css-card {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 20px !important;
            padding: 30px !important;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.06) !important;
        }
        
        /* 4. INPUTS NORMALIZATION (Removes iOS default shadow and styles) */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {
            appearance: none !important;
            -webkit-appearance: none !important;
            background-color: #FFFFFF !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            color: #334155 !important;
            font-weight: 500 !important;
            min-height: 48px !important;
            box-shadow: none !important;
        }
        
        .stTextInput > div > div > input:focus, 
        .stNumberInput > div > div > input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
            outline: none !important;
        }

        /* 5. BUTTONS NORMALIZATION (Cross-browser identical look) */
        .stButton > button {
            appearance: none !important;
            -webkit-appearance: none !important;
            background: -webkit-linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 12px 28px !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            -webkit-tap-highlight-color: transparent !important; /* Removes blue tap flash on Android */
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4) !important;
        }

        /* 6. TABS & STATUS PILLS (Locking colors against inversion) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background-color: #FFFFFF !important;
            padding: 10px !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 10px -2px rgba(0,0,0,0.05) !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #EEF2FF !important;
            color: #4F46E5 !important;
            border-radius: 10px !important;
        }
        
        .id-badge {
            background-color: #ECFDF5 !important;
            color: #059669 !important;
            padding: 4px 12px !important;
            border-radius: 20px !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            border: 1px solid #D1FAE5 !important;
        }

        .info-box {
            background-color: #F0FDFA !important;
            border: 1px solid #CCFBF1 !important;
            padding: 15px !important;
            border-radius: 12px !important;
            color: #0F766E !important;
            font-weight: 600 !important;
            margin-bottom: 15px !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ ROBUST API ENGINE (MODULAR)
# ==========================================
def get_headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

def fetch_data(owner, repo, path, token):
    """Generic fetch function for any repo"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        res = requests.get(url, headers=get_headers(token))
        if res.status_code == 200:
            data = res.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return {"status": "success", "content": json.loads(content), "sha": data['sha']}
        else:
            return {"status": "error", "msg": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def push_data(owner, repo, path, token, content_obj, message, sha=None):
    """Generic push function for any repo"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        json_str = json.dumps(content_obj, indent=2, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": message,
            "content": encoded,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha
            
        res = requests.put(url, headers=get_headers(token), data=json.dumps(payload))
        return res
    except Exception as e:
        st.error(f"Push Error: {e}")
        return None

# ==========================================
# 🧠 LOGIC: EXAM ANALYSIS (ExamPortal)
# ==========================================
def analyze_exam_context(course_id):
    path = f"public/data/{course_id}/exams.json"
    res = fetch_data(REPO_1_OWNER, REPO_1_NAME, path, TOKEN_MAIN)
    
    next_idx = 1
    passwords = set()
    existing_list = []
    sha = None
    file_status = "new"
    
    if res['status'] == 'success':
        file_status = "exists"
        sha = res['sha']
        existing_list = res['content']
        if existing_list:
            last_item = existing_list[-1]
            last_id = last_item.get('id', 'e0')
            num = ''.join(filter(str.isdigit, last_id))
            if num: next_idx = int(num) + 1
        
        for ex in existing_list:
            if ex.get('password'): passwords.add(ex['password'])
            
    return next_idx, list(passwords), sha, existing_list, file_status

# ==========================================
# 🖥️ MAIN APPLICATION
# ==========================================
def main():
    apply_custom_design()
    
    # --- SESSION STATE INITIALIZATION ---
    if 'auth' not in st.session_state: st.session_state.auth = False
    if 'ep_context' not in st.session_state: st.session_state.ep_context = {}
    if 'fetched_course_id' not in st.session_state: st.session_state.fetched_course_id = None
    
    # --- AUTHENTICATION ---
    if not st.session_state.auth:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<h1 style='text-align: center; color:#4F46E5;'>🔒 Admin Access</h1>", unsafe_allow_html=True)
            with st.form("login"):
                pwd = st.text_input("Security Key", type="password")
                if st.form_submit_button("Enter Dashboard"):
                    if pwd == ADMIN_PASSWORD:
                        st.session_state.auth = True
                        st.rerun()
                    else:
                        st.error("⛔ Access Denied")
        return

    # --- DASHBOARD HEADER ---
    col_head, col_logout = st.columns([5,1])
    with col_head:
        st.markdown("<div class='gradient-text'>Unified Admin Panel</div>", unsafe_allow_html=True)
        st.caption("Managing: 🎓 ExamPortal & 🌐 PS Website")
    with col_logout:
        if st.button("Log Out"):
            st.session_state.auth = False
            st.rerun()

    st.markdown("---")

    # --- TABS SYSTEM ---
    tab_examportal, tab_ps, tab_bot = st.tabs(["🎓 ExamPortal Manager", "🌐 Website Manager (PS)", "🤖 Bot Manager"])

    # =======================================================
    # TAB 1: EXAM PORTAL MANAGER
    # =======================================================
    with tab_examportal:
        sub_tab1, sub_tab2 = st.tabs(["📘 Add Course", "📝 Exam Master"])
        
        # --- SUB TAB: NEW COURSE ---
        with sub_tab1:
            st.info("Adds new course to `src/data/CourseList.json` (ExamPortal)")
            with st.form("ep_course_form"):
                c1, c2 = st.columns(2)
                ep_id = c1.text_input("🆔 ID", placeholder="med-25").strip()
                ep_title = c2.text_input("📌 Title", placeholder="Course Name").strip()
                
                c3, c4, c5 = st.columns(3)
                ep_price = c3.number_input("Price", value=150)
                ep_old = c4.number_input("Old Price", value=5000)
                ep_cat = c5.selectbox("Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])
                
                ep_img = st.text_input("🖼️ Image Name", placeholder="img.jpg").strip()
                if ep_img: st.caption(f"Preview: {IMG_CDN_BASE}{ep_img}")
                
                if st.form_submit_button("🚀 Upload to ExamPortal"):
                    if not ep_id or not ep_title: st.warning("ID & Title Required")
                    else:
                        res = fetch_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN)
                        if res['status'] == 'success':
                            is_duplicate = any(c['id'] == ep_id for c in res['content'])
                            if is_duplicate:
                                st.error(f"⛔ Course ID '{ep_id}' already exists!")
                            else:
                                new_entry = {
                                    "id": ep_id, "title": ep_title, "price": ep_price,
                                    "oldPrice": ep_old, "category": ep_cat, 
                                    "image": f"{IMG_CDN_BASE}{ep_img}"
                                }
                                updated_list = [new_entry] + res['content']
                                push_res = push_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN, updated_list, f"Add {ep_title}", res['sha'])
                                if push_res and push_res.status_code in [200, 201]:
                                    st.balloons()
                                    st.success(f"✅ Added {ep_title} to ExamPortal")
                                else:
                                    st.error("Push failed")
                        else:
                            st.error("Failed to fetch current list")

        # --- SUB TAB: EXAM MASTER ---
        with sub_tab2:
            st.markdown("### 📝 Exam Management")
            
            with st.expander("🔍 Find Course ID (Search Database)", expanded=False):
                if st.button("Load All Courses"):
                    with st.spinner("Fetching data from ExamPortal..."):
                        res = fetch_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN)
                        if res['status'] == 'success':
                            st.table([{"ID": c['id'], "Title": c['title']} for c in res['content']])
                        else:
                            st.error("Could not fetch course list.")

            col_search, col_btn = st.columns([3, 1])
            target_id = col_search.text_input("Target Course ID", placeholder="e.g. med25").strip()
            
            if col_btn.button("📥 Load Context"):
                if target_id:
                    idx, pws, sha, curr_list, status = analyze_exam_context(target_id)
                    st.session_state.ep_context = {
                        "id": target_id, "next_idx": idx, "pw_hist": pws,
                        "sha": sha, "existing_list": curr_list, "status": status
                    }
                    st.session_state.fetched_course_id = target_id
                    st.toast(f"Loaded Context for {target_id}", icon="✅")
                else:
                    st.error("Please enter a Course ID.")

            if st.session_state.fetched_course_id and st.session_state.ep_context:
                ctx = st.session_state.ep_context
                st.markdown("---")
                
                st.markdown(f"""
                <div class="info-box">
                    <span>📂 Folder: {ctx['id']}</span>
                    <span>•</span>
                    <span>🔢 Next ID: <b>e{ctx['next_idx']}</b></span>
                    <span>•</span>
                    <span>📄 File: q{ctx['next_idx']}.json</span>
                </div>
                """, unsafe_allow_html=True)

                if ctx['pw_hist']:
                    st.caption(f"🔑 **Previously Used Passwords:** {', '.join(ctx['pw_hist'])}")

                with st.form("ep_exam_form"):
                    st.markdown("#### 1. Exam Details")
                    ex_title = st.text_input("📝 Exam Title", placeholder="Model Test 01").strip()
                    
                    c1, c2, c3 = st.columns(3)
                    ex_time = c1.number_input("⏱️ Time (min)", value=60)
                    ex_ques = c2.number_input("❓ Questions", value=100)
                    ex_neg = c3.number_input("🚫 Negative Mark", value=0.25)
                    
                    st.markdown("#### 2. Access Settings")
                    is_paid = st.checkbox("💎 Mark as Premium/Paid Exam")
                    ex_pass = ""
                    if is_paid:
                        ex_pass = st.text_input("🔒 Set Password").strip()
                        if not ex_pass: st.warning("Password required for Paid Exams")

                    st.markdown("#### 3. Question Data")
                    ex_json_str = st.text_area("📄 Paste JSON Body", height=200, placeholder='{\n  "examTitle": "Title",\n  "questions": []\n}').strip()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_label = "🚀 Publish Premium Exam" if is_paid else "🚀 Publish Free Exam"
                    
                    if st.form_submit_button(btn_label):
                        errors = []
                        if not ex_title: errors.append("Title missing")
                        if is_paid and not ex_pass: errors.append("Password missing")
                        if not ex_json_str: errors.append("JSON missing")
                        try: json.loads(ex_json_str)
                        except: errors.append("Invalid JSON")
                        
                        if errors:
                            for e in errors: st.error(f"❌ {e}")
                        else:
                            with st.status("⚙️ Processing Update...", expanded=True) as status:
                                auto_id = f"e{ctx['next_idx']}"
                                q_filename = f"q{ctx['next_idx']}.json"
                                
                                new_card = {
                                    "id": auto_id, "title": ex_title, "time": ex_time,
                                    "totalQuestions": ex_ques, "negativeMark": ex_neg,
                                    "questionFile": q_filename, "isPaid": is_paid
                                }
                                if is_paid: new_card["password"] = ex_pass
                                
                                q_path = f"public/data/{ctx['id']}/{q_filename}"
                                st.write(f"📤 Uploading {q_filename}...")
                                q_res = push_data(REPO_1_OWNER, REPO_1_NAME, q_path, TOKEN_MAIN, json.loads(ex_json_str), f"Add Quest {auto_id}")
                                
                                if q_res and q_res.status_code in [200, 201]:
                                    st.write("📝 Updating Exam List...")
                                    l_path = f"public/data/{ctx['id']}/exams.json"
                                    final_list = (ctx['existing_list'] or []) + [new_card]
                                    l_res = push_data(REPO_1_OWNER, REPO_1_NAME, l_path, TOKEN_MAIN, final_list, f"Update List {auto_id}", ctx['sha'])
                                    
                                    if l_res and l_res.status_code in [200, 201]:
                                        status.update(label="🎉 Success!", state="complete", expanded=False)
                                        st.balloons()
                                        st.success(f"Exam {auto_id} Published!")
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        status.update(label="❌ List Update Failed", state="error")
                                else:
                                    status.update(label="❌ Question Upload Failed", state="error")

    # =======================================================
    # TAB 2: PS WEBSITE MANAGER
    # =======================================================
    with tab_ps:
        st.markdown("### 🌐 Premium Subscriptions Manager")
        st.markdown("Updates `courses/courses.json` in `ps` repo.")
        
        with st.status("🔄 Syncing with PS Database...", expanded=True) as status:
            ps_data = fetch_data(REPO_2_OWNER, REPO_2_NAME, PATH_2_COURSE, TOKEN_PS)
            
            if ps_data['status'] == 'success':
                current_courses = ps_data['content']
                all_ids = [c.get('id', 0) for c in current_courses if isinstance(c.get('id'), int)]
                next_id = max(all_ids) + 1 if all_ids else 100
                
                status.update(label=f"✅ Synced! Next Auto-ID: {next_id}", state="complete", expanded=False)
                
                with st.form("ps_add_form"):
                    st.markdown(f"#### 🆔 New Course ID: <span class='id-badge'>{next_id}</span>", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    ps_title = col_a.text_input("📌 Course Title", placeholder="🔥 ACS ENGINEERING 2026🔥").strip()
                    ps_img = col_b.text_input("🖼️ Image Name", placeholder="IMG_2026.jpg").strip()
                    if ps_img: st.caption(f"Preview: {IMG_CDN_BASE}{ps_img}")

                    col_c, col_d, col_e = st.columns(3)
                    ps_price = col_c.number_input("💰 Price", value=350)
                    ps_old = col_d.number_input("📉 Original Price", value=5000)
                    ps_dur = col_e.number_input("⏳ Duration (Months)", value=2.5, step=0.5)

                    col_f, col_g = st.columns(2)
                    ps_grade = col_f.selectbox("🎓 Grade", ["HSC-27 Academic", "HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])
                    ps_type = col_g.selectbox("🏷️ Course Type", ['ACS', 'UDVASH', 'Physics Hunters', 'Bondi Pathshala', 'RTDS', 'Battle of Biology', 'Alchemy', 'CPS'])

                    col_h, col_i = st.columns(2)
                    ps_stud = col_h.number_input("👥 Students", value=1000, step=100)
                    ps_rate = col_i.slider("⭐ Rating", 1, 5, 5)

                    st.markdown("---")
                    
                    if st.form_submit_button("🚀 Publish to PS Website"):
                        if not ps_title or not ps_img:
                            st.warning("Title & Image required")
                        else:
                            new_ps_course = {
                                "id": next_id,
                                "title": ps_title,
                                "grade": [ps_grade], 
                                "courseType": ps_type,
                                "price": ps_price,
                                "originalPrice": ps_old,
                                "duration": f"{ps_dur} months",
                                "students": ps_stud,
                                "rating": ps_rate,
                                "image": f"{IMG_CDN_BASE}{ps_img}"
                            }

                            updated_ps_list = [new_ps_course] + current_courses
                            
                            with st.spinner("🚀 Pushing to Repo..."):
                                res_push = push_data(REPO_2_OWNER, REPO_2_NAME, PATH_2_COURSE, TOKEN_PS, updated_ps_list, f"Add {next_id}", ps_data['sha'])
                                
                                if res_push and res_push.status_code in [200, 201]:
                                    st.balloons()
                                    st.success(f"✅ Added: {ps_title}")
                                    with st.expander("View Payload"): st.json(new_ps_course)
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("Push failed")
            else:
                st.error(f"❌ Could not sync with PS. Check Token. ({ps_data.get('msg')})")

    # =======================================================
    # TAB 3: BOT MANAGER (CourseDataDB)
    # =======================================================
    with tab_bot:
        st.markdown("### 🤖 Telegram Bot Database Manager")
        bot_tab_batch, bot_tab_course = st.tabs(["📁 Batch Management", "📚 Course Management"])

        # ---------------------------------------------------
        # 1. BATCH MANAGEMENT WINDOW
        # ---------------------------------------------------
        with bot_tab_batch:
            st.markdown("#### 📁 ব্যাচ কন্ট্রোল প্যানেল")
            
            if 'show_add_batch' not in st.session_state:
                st.session_state.show_add_batch = False

            if not st.session_state.show_add_batch:
                if st.button("➕ Add New Batch"):
                    st.session_state.show_add_batch = True
                    st.rerun()
            
            if st.session_state.show_add_batch:
                with st.container():
                    st.markdown("<div class='css-card'>", unsafe_allow_html=True)
                    st.markdown("#### ✨ Create New Batch")
                    
                    b_type = st.selectbox("Batch Type", ["HSC batch", "Admission batch"])
                    b_name = st.text_input("Name:", placeholder="🔥HSC 2028 All Courses🔥").strip()
                    b_year = st.text_input("Year:", placeholder="28 (শুধু ২ ডিজিট দিন)", max_chars=2).strip()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    
                    if c1.button("✅ Save", use_container_width=True):
                        if not b_name or not b_year:
                            st.warning("⚠️ Name এবং Year দেওয়া বাধ্যতামূলক!")
                        else:
                            prefix = "hsc" if b_type == "HSC batch" else "admission"
                            filename = f"{prefix}{b_year}.json"
                            
                            check_res = fetch_data(REPO_3_OWNER, REPO_3_NAME, filename, TOKEN_PS)
                            if check_res['status'] == 'success':
                                st.error(f"❌ এই নামের ব্যাচ ({filename}) আগে থেকেই ডাটাবেসে আছে! দয়া করে অন্য ব্যাচ তৈরি করুন।")
                            else:
                                new_content = {
                                    "name": b_name,
                                    "type": "folder",
                                    "children": {}
                                }
                                with st.spinner("ব্যাচ তৈরি করা হচ্ছে..."):
                                    push_res = push_data(REPO_3_OWNER, REPO_3_NAME, filename, TOKEN_PS, new_content, f"Create new batch {filename}")
                                    
                                    if push_res and push_res.status_code in [200, 201]:
                                        st.success(f"✅ {filename} সফলভাবে তৈরি হয়েছে!")
                                        st.session_state.show_add_batch = False
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error("❌ ফাইল তৈরি করতে সমস্যা হয়েছে!")
                    
                    if c2.button("🚫 Cancel", use_container_width=True):
                        st.session_state.show_add_batch = False
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### 📦 Existing Batches")
            with st.spinner("ডাটাবেস থেকে ব্যাচ লোড হচ্ছে..."):
                root_res = requests.get(f"https://api.github.com/repos/{REPO_3_OWNER}/{REPO_3_NAME}/contents/", headers=get_headers(TOKEN_PS))
                
                if root_res.status_code == 200:
                    json_files = [f for f in root_res.json() if f['name'].endswith('.json')]
                    
                    for f in json_files:
                        file_res = fetch_data(REPO_3_OWNER, REPO_3_NAME, f['name'], TOKEN_PS)
                        if file_res['status'] == 'success':
                            content = file_res['content']
                            sha = file_res['sha']
                            batch_title = content.get('name', f['name'])
                            
                            with st.container():
                                st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                                
                                edit_key = f"edit_{f['name']}"
                                if edit_key not in st.session_state:
                                    st.session_state[edit_key] = False
                                
                                if not st.session_state[edit_key]:
                                    col_title, col_btn = st.columns([4, 1])
                                    col_title.markdown(f"**{batch_title}**  `({f['name']})`")
                                    if col_btn.button("✏️ Edit", key=f"btn_{f['name']}"):
                                        st.session_state[edit_key] = True
                                        st.rerun()
                                else:
                                    new_name = st.text_input(f"Edit Name for {f['name']}:", value=batch_title, key=f"inp_{f['name']}").strip()
                                    ec1, ec2 = st.columns(2)
                                    
                                    if ec1.button("✅ Save", key=f"save_{f['name']}"):
                                        content['name'] = new_name
                                        with st.spinner("আপডেট করা হচ্ছে..."):
                                            push_res = push_data(REPO_3_OWNER, REPO_3_NAME, f['name'], TOKEN_PS, content, f"Update name for {f['name']}", sha)
                                            if push_res and push_res.status_code in [200, 201]:
                                                st.success("✅ নাম সফলভাবে সেভ হয়েছে!")
                                                st.session_state[edit_key] = False
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("❌ আপডেট ফেইল হয়েছে!")
                                    
                                    if ec2.button("🚫 Cancel", key=f"cancel_{f['name']}"):
                                        st.session_state[edit_key] = False
                                        st.rerun()
                                        
                                st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("GitHub থেকে ফাইল ফেচ করা সম্ভব হয়নি। টোকেন চেক করুন।")

        # ---------------------------------------------------
        # 2. COURSE MANAGEMENT WINDOW (Dynamic Infinite Tree)
        # ---------------------------------------------------
        with bot_tab_course:
            def get_current_node():
                if not st.session_state.bot_nav_path:
                    return None
                node = st.session_state.bot_current_file_content
                for key in st.session_state.bot_nav_path[1:]:
                    node = node['children'][key]
                return node

            if 'bot_nav_path' not in st.session_state:
                st.session_state.bot_nav_path = []
            if 'bot_edit_course' not in st.session_state:
                st.session_state.bot_edit_course = None
            if 'bot_add_course' not in st.session_state:
                st.session_state.bot_add_course = False
            if 'bot_add_folder' not in st.session_state:
                st.session_state.bot_add_folder = False

            path = st.session_state.bot_nav_path

            if len(path) > 0:
                if st.button("⬅️ ফিরে যান (Back)", use_container_width=False, type="secondary"):
                    st.session_state.bot_nav_path.pop()
                    st.session_state.bot_edit_course = None
                    st.session_state.bot_add_course = False
                    st.session_state.bot_add_folder = False
                    st.rerun()
                st.markdown("---")

            if len(path) == 0:
                st.markdown("#### 🌐 রুট ফোল্ডার সিলেক্ট করুন")
                with st.spinner("ডাটাবেস লোড হচ্ছে..."):
                    root_res = requests.get(f"https://api.github.com/repos/{REPO_3_OWNER}/{REPO_3_NAME}/contents/", headers=get_headers(TOKEN_PS))
                    if root_res.status_code == 200:
                        files = [f for f in root_res.json() if f['name'].endswith('.json')]
                        for f in files:
                            file_res = fetch_data(REPO_3_OWNER, REPO_3_NAME, f['name'], TOKEN_PS)
                            if file_res['status'] == 'success':
                                c_name = file_res['content'].get('name', f['name'])
                                if st.button(f"📁 {c_name}", key=f"nav_root_{f['name']}"):
                                    st.session_state.bot_nav_path.append(f['name'])
                                    st.session_state.bot_current_file_content = file_res['content']
                                    st.session_state.bot_current_file_sha = file_res['sha']
                                    st.session_state.bot_current_filename = f['name']
                                    st.rerun()
                    else:
                        st.error("Failed to load root folders.")
            
            else:
                current_node = get_current_node()
                st.markdown(f"#### 📂 {current_node.get('name', 'Folder')}")

                children = current_node.get('children', {})
                
                has_folders = any(child.get('type') == 'folder' for child in children.values())
                has_courses = any(child.get('type') == 'course' for child in children.values())
                
                for child_key, child in children.items():
                    if child.get('type') == 'folder':
                        if st.button(f"📁 {child.get('name', child_key)}", key=f"nav_{child_key}"):
                            st.session_state.bot_nav_path.append(child_key)
                            st.session_state.bot_edit_course = None
                            st.session_state.bot_add_course = False
                            st.session_state.bot_add_folder = False
                            st.rerun()
                    
                    elif child.get('type') == 'course':
                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2 = st.columns([4, 1])
                        col1.markdown(f"**📚 {child.get('name', child_key)}**")
                        if col2.button("✏️ Edit", key=f"edit_btn_{child_key}"):
                            st.session_state.bot_edit_course = child_key
                            st.session_state.bot_add_course = False
                            st.session_state.bot_add_folder = False
                            st.rerun()
                        
                        if st.session_state.bot_edit_course == child_key:
                            with st.container():
                                st.markdown("<div class='css-card'>", unsafe_allow_html=True)
                                st.markdown(f"##### ✏️ Editing: {child.get('name')}")
                                
                                e_name = st.text_input("Course Name", value=child.get('name', '') or '').strip()
                                e_price = st.number_input("Price (TK)", value=int(child.get('price', 0)))
                                e_group = st.text_input("Group Link", value=child.get('groupLink', '') or '').strip()
                                e_payment = st.text_input("Payment Link", value=child.get('paymentLink', '') or '').strip()
                                e_image = st.text_input("Image Link", value=child.get('imageLink', '') or '').strip()
                                e_desc = st.text_area("Description", value=child.get('description', '') or '', height=150).strip()
                                
                                ec1, ec2 = st.columns(2)
                                if ec1.button("✅ Save Changes", key=f"save_{child_key}"):
                                    current_node['children'][child_key].update({
                                        "name": e_name,
                                        "price": e_price,
                                        "groupLink": e_group,
                                        "paymentLink": e_payment,
                                        "imageLink": e_image,
                                        "description": e_desc
                                    })
                                    with st.spinner("Saving to database..."):
                                        push_res = push_data(REPO_3_OWNER, REPO_3_NAME, st.session_state.bot_current_filename, TOKEN_PS, st.session_state.bot_current_file_content, f"Update course {child_key}", st.session_state.bot_current_file_sha)
                                        if push_res and push_res.status_code in [200, 201]:
                                            st.success("✅ Saved perfectly!")
                                            st.session_state.bot_current_file_sha = push_res.json()['content']['sha']
                                            st.session_state.bot_edit_course = None
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to save.")
                                            
                                if ec2.button("🚫 Cancel", key=f"cancel_{child_key}"):
                                    st.session_state.bot_edit_course = None
                                    st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)
                                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("---")
                
                btn_col1, btn_col2 = st.columns(2)
                
                if not has_courses:
                    with btn_col1:
                        if not st.session_state.bot_add_folder:
                            if st.button("➕ Add New Sub-Folder", use_container_width=True):
                                st.session_state.bot_add_folder = True
                                st.session_state.bot_add_course = False
                                st.session_state.bot_edit_course = None
                                st.rerun()

                if not has_folders:
                    with btn_col2:
                        if not st.session_state.bot_add_course:
                            if st.button("➕ Add New Course Here", use_container_width=True):
                                st.session_state.bot_add_course = True
                                st.session_state.bot_add_folder = False
                                st.session_state.bot_edit_course = None
                                st.rerun()

                if st.session_state.bot_add_folder:
                    with st.container():
                        st.markdown("<div class='css-card'>", unsafe_allow_html=True)
                        st.markdown("##### 📁 Create New Sub-Folder")
                        
                        f_key = st.text_input("Folder ID/Key (Unique, No Spaces)", placeholder="e.g. math_series").strip()
                        f_name = st.text_input("Folder Display Name", placeholder="🧮 Math Series").strip()
                        
                        fc1, fc2 = st.columns(2)
                        if fc1.button("✅ Create Folder", key="save_folder"):
                            if not f_key or not f_name:
                                st.warning("⚠️ ID and Name are required!")
                            elif " " in f_key:
                                st.error("❌ ID cannot contain spaces!")
                            elif f_key in children:
                                st.error("❌ This ID already exists!")
                            else:
                                current_node['children'][f_key] = {
                                    "name": f_name,
                                    "type": "folder",
                                    "children": {}
                                }
                                with st.spinner("Adding new folder..."):
                                    push_res = push_data(REPO_3_OWNER, REPO_3_NAME, st.session_state.bot_current_filename, TOKEN_PS, st.session_state.bot_current_file_content, f"Add folder {f_key}", st.session_state.bot_current_file_sha)
                                    if push_res and push_res.status_code in [200, 201]:
                                        st.success("✅ Folder added successfully!")
                                        st.session_state.bot_current_file_sha = push_res.json()['content']['sha']
                                        st.session_state.bot_add_folder = False
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to add folder.")
                                        
                        if fc2.button("🚫 Cancel", key="cancel_add_folder"):
                            st.session_state.bot_add_folder = False
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                if st.session_state.bot_add_course:
                    with st.container():
                        st.markdown("<div class='css-card'>", unsafe_allow_html=True)
                        st.markdown("##### ✨ Create New Course")
                        
                        n_key = st.text_input("Course ID/Key (Unique, No Spaces)", placeholder="e.g. acs28_phy_c1").strip()
                        n_name = st.text_input("Course Name").strip()
                        n_price = st.number_input("Price (TK)", value=100)
                        n_group = st.text_input("Group Link").strip()
                        n_payment = st.text_input("Payment Link").strip()
                        n_image = st.text_input("Image Link").strip()
                        n_desc = st.text_area("Description", height=150).strip()
                        
                        nc1, nc2 = st.columns(2)
                        if nc1.button("✅ Add Course", key="save_new_course"):
                            if not n_key or not n_name:
                                st.warning("⚠️ ID and Name are required!")
                            elif " " in n_key:
                                st.error("❌ ID cannot contain spaces!")
                            elif n_key in children:
                                st.error("❌ This ID already exists!")
                            else:
                                current_node['children'][n_key] = {
                                    "name": n_name,
                                    "type": "course",
                                    "price": n_price,
                                    "groupLink": n_group,
                                    "paymentLink": n_payment,
                                    "imageLink": n_image,
                                    "description": n_desc
                                }
                                with st.spinner("Adding new course..."):
                                    push_res = push_data(REPO_3_OWNER, REPO_3_NAME, st.session_state.bot_current_filename, TOKEN_PS, st.session_state.bot_current_file_content, f"Add course {n_key}", st.session_state.bot_current_file_sha)
                                    if push_res and push_res.status_code in [200, 201]:
                                        st.success("✅ Added successfully!")
                                        st.session_state.bot_current_file_sha = push_res.json()['content']['sha']
                                        st.session_state.bot_add_course = False
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to add course.")
                                        
                        if nc2.button("🚫 Cancel", key="cancel_add_course"):
                            st.session_state.bot_add_course = False
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
