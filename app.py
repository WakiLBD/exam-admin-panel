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

# CDN Config
IMG_CDN_BASE = "https://cdn.jsdelivr.net/gh/PremiumSubscriptions/premium-subscriptions-bot@main/"

# ==========================================
# 🎨 UI & UX DESIGN SYSTEM (PREMIUM)
# ==========================================
def apply_custom_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* GLOBAL THEME */
        .stApp {
            background-color: #F8F9FC;
            color: #0F172A;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        /* HEADERS */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: #1E293B;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            font-weight: 800;
        }

        /* CARDS */
        div[data-testid="stForm"], div.css-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.06);
        }
        
        /* INPUTS */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {
            background-color: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
            color: #334155;
            font-weight: 500;
            min-height: 48px;
        }
        
        .stTextInput > div > div > input:focus, 
        .stNumberInput > div > div > input:focus {
            border-color: #6366F1;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }

        /* BUTTONS */
        .stButton > button {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 12px;
            font-weight: 700;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #FFFFFF;
            padding: 10px;
            border-radius: 16px;
            box-shadow: 0 4px 10px -2px rgba(0,0,0,0.05);
        }
        .stTabs [aria-selected="true"] {
            background-color: #EEF2FF;
            color: #4F46E5;
            border-radius: 10px;
        }
        
        /* STATUS PILLS & INFO BOX */
        .id-badge {
            background-color: #ECFDF5;
            color: #059669;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid #D1FAE5;
        }

        .info-box {
            background-color: #F0FDFA;
            border: 1px solid #CCFBF1;
            padding: 15px;
            border-radius: 12px;
            color: #0F766E;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
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
    tab_examportal, tab_ps = st.tabs(["🎓 ExamPortal Manager", "🌐 Website Manager (PS)"])

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
                ep_title = c2.text_input("📌 Title", placeholder="Course Name")
                
                c3, c4, c5 = st.columns(3)
                ep_price = c3.number_input("Price", value=150)
                ep_old = c4.number_input("Old Price", value=5000)
                ep_cat = c5.selectbox("Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])
                
                ep_img = st.text_input("🖼️ Image Name", placeholder="img.jpg")
                if ep_img: st.caption(f"Preview: {IMG_CDN_BASE}{ep_img}")
                
                if st.form_submit_button("🚀 Upload to ExamPortal"):
                    if not ep_id or not ep_title: st.warning("ID & Title Required")
                    else:
                        res = fetch_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN)
                        if res['status'] == 'success':
                            # Duplicate Check
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

        # --- SUB TAB: EXAM MASTER (RESTORED FEATURES) ---
        with sub_tab2:
            st.markdown("### 📝 Exam Management")
            
            # --- FEATURE RESTORED: DATABASE SEARCH ---
            with st.expander("🔍 Find Course ID (Search Database)", expanded=False):
                if st.button("Load All Courses"):
                    with st.spinner("Fetching data from ExamPortal..."):
                        res = fetch_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN)
                        if res['status'] == 'success':
                            # Displaying simple table as per previous code
                            st.table([{"ID": c['id'], "Title": c['title']} for c in res['content']])
                        else:
                            st.error("Could not fetch course list.")

            # --- CONTEXT LOADING ---
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

            # --- EXAM FORM (Only shows if context is loaded) ---
            if st.session_state.fetched_course_id and st.session_state.ep_context:
                ctx = st.session_state.ep_context
                
                st.markdown("---")
                
                # RESTORED: INFO BOX DESIGN
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
                    ex_title = st.text_input("📝 Exam Title", placeholder="Model Test 01")
                    
                    c1, c2, c3 = st.columns(3)
                    ex_time = c1.number_input("⏱️ Time (min)", value=60)
                    ex_ques = c2.number_input("❓ Questions", value=100)
                    ex_neg = c3.number_input("🚫 Negative Mark", value=0.25)
                    
                    st.markdown("#### 2. Access Settings")
                    is_paid = st.checkbox("💎 Mark as Premium/Paid Exam")
                    ex_pass = ""
                    if is_paid:
                        ex_pass = st.text_input("🔒 Set Password")
                        if not ex_pass: st.warning("Password required for Paid Exams")

                    st.markdown("#### 3. Question Data")
                    ex_json_str = st.text_area("📄 Paste JSON Body", height=200, placeholder='{\n  "examTitle": "Title",\n  "questions": []\n}')
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_label = "🚀 Publish Premium Exam" if is_paid else "🚀 Publish Free Exam"
                    
                    if st.form_submit_button(btn_label):
                        # Validation
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
                                
                                # Construct Exam Card
                                new_card = {
                                    "id": auto_id, "title": ex_title, "time": ex_time,
                                    "totalQuestions": ex_ques, "negativeMark": ex_neg,
                                    "questionFile": q_filename, "isPaid": is_paid
                                }
                                if is_paid: new_card["password"] = ex_pass
                                
                                # 1. Upload Question File
                                q_path = f"public/data/{ctx['id']}/{q_filename}"
                                st.write(f"📤 Uploading {q_filename}...")
                                q_res = push_data(REPO_1_OWNER, REPO_1_NAME, q_path, TOKEN_MAIN, json.loads(ex_json_str), f"Add Quest {auto_id}")
                                
                                if q_res and q_res.status_code in [200, 201]:
                                    # 2. Update List
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
    # TAB 2: PS WEBSITE MANAGER (New Feature)
    # =======================================================
    with tab_ps:
        st.markdown("### 🌐 Premium Subscriptions Manager")
        st.markdown("Updates `courses/courses.json` in `ps` repo.")
        
        # AUTO-FETCH LOGIC
        with st.status("🔄 Syncing with PS Database...", expanded=True) as status:
            ps_data = fetch_data(REPO_2_OWNER, REPO_2_NAME, PATH_2_COURSE, TOKEN_PS)
            
            if ps_data['status'] == 'success':
                current_courses = ps_data['content']
                all_ids = [c.get('id', 0) for c in current_courses if isinstance(c.get('id'), int)]
                next_id = max(all_ids) + 1 if all_ids else 100
                
                status.update(label=f"✅ Synced! Next Auto-ID: {next_id}", state="complete", expanded=False)
                
                # --- PS FORM ---
                with st.form("ps_add_form"):
                    st.markdown(f"#### 🆔 New Course ID: <span class='id-badge'>{next_id}</span>", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    ps_title = col_a.text_input("📌 Course Title", placeholder="🔥 ACS ENGINEERING 2026🔥")
                    ps_img = col_b.text_input("🖼️ Image Name", placeholder="IMG_2026.jpg")
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
                            # Construct JSON
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

if __name__ == "__main__":
    main()

