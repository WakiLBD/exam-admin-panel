import streamlit as st
import requests
import json
import base64
import time

# ==========================================
# 🎨 UI & UX DESIGN SYSTEM (LIGHT & PREMIUM)
# ==========================================
def apply_custom_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* -----------------------
           1. GLOBAL THEME (LIGHT)
           ----------------------- */
        .stApp {
            background-color: #F8F9FC; /* Soft Blue-Grey Light Background */
            color: #1E293B; /* Slate 800 for Text */
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        /* -----------------------
           2. TYPOGRAPHY & HEADERS
           ----------------------- */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: #0F172A;
        }
        
        /* Gradient Text for Main Title */
        .gradient-text {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
        }

        /* -----------------------
           3. MODERN CARDS (SHADOWS)
           ----------------------- */
        div[data-testid="stForm"], div.css-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05); /* Soft Premium Shadow */
            transition: transform 0.2s ease;
        }
        
        /* -----------------------
           4. INPUT FIELDS (FIXED HEIGHT & PADDING)
           ----------------------- */
        /* General Input Styling */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stTextArea > div > div > textarea {
            background-color: #FFFFFF; 
            color: #1E293B; 
            border-radius: 12px; 
            border: 2px solid #E2E8F0; 
            padding: 10px 15px; /* Adjusted padding */
            font-weight: 500;
            min-height: 45px; /* Fixed height for consistency */
            transition: all 0.2s ease;
        }

        /* -----------------------
           🔥 SPECIFIC FIX FOR SELECTBOX (CATEGORY) 🔥
           ----------------------- */
        /* Targeting the container of the selectbox to fix text cutting */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            color: #1E293B !important;
            min-height: 45px !important; /* Matches other inputs */
            display: flex !important;
            align-items: center !important; /* Vertically center text */
        }

        /* Focus Effect (Teal/Purple) */
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox div[data-baseweb="select"] > div:focus-within {
            border-color: #8B5CF6 !important; 
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1) !important; 
        }

        /* -----------------------
           5. BUTTONS (VIBRANT GRADIENTS)
           ----------------------- */
        .stButton > button {
            background: linear-gradient(135deg, #0EA5E9 0%, #3B82F6 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 16px;
            font-weight: 700;
            font-size: 16px;
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.5);
        }

        /* -----------------------
           6. TABS & ALERTS
           ----------------------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #FFFFFF;
            padding: 8px;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 10px;
            background-color: transparent;
            color: #64748B;
            font-weight: 600;
            border: none;
        }

        .stTabs [aria-selected="true"] {
            background-color: #EFF6FF;
            color: #3B82F6;
        }
        
        /* Custom Info Box */
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
# ⚙️ CONFIGURATION & HELPERS
# ==========================================
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    GITHUB_TOKEN = "YOUR_TOKEN" 
    ADMIN_PASSWORD = "123"

REPO_OWNER = 'WakiLBD'   
REPO_NAME = 'ExamPortal'      
BRANCH = 'main'
COURSE_LIST_PATH = 'src/data/CourseList.json'
IMG_BASE_URL = "https://cdn.jsdelivr.net/gh/PremiumSubscriptions/premium-subscriptions-bot@main/"

headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# -------------------------------------------
# 🛠️ GITHUB API HELPERS
# -------------------------------------------
def get_file_content(path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    res = requests.get(url, headers=headers)
    return res

def upload_file(path, content_str, message, sha=None):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    encoded = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    payload = {"message": message, "content": encoded, "branch": BRANCH}
    if sha: payload['sha'] = sha
    res = requests.put(url, headers=headers, data=json.dumps(payload))
    return res

# ==========================================
# 🧠 LOGIC: EXAM ANALYSIS
# ==========================================
def analyze_exam_context(course_id):
    path = f"public/data/{course_id}/exams.json"
    res = get_file_content(path)
    
    next_idx = 1
    passwords = set()
    existing_list = []
    sha = None
    file_status = "new"

    if res.status_code == 200:
        file_status = "exists"
        data = res.json()
        sha = data['sha']
        try:
            content = base64.b64decode(data['content']).decode('utf-8')
            existing_list = json.loads(content)
            
            if existing_list:
                last_item = existing_list[-1]
                last_id_str = last_item.get('id', 'e0')
                num_part = ''.join(filter(str.isdigit, last_id_str))
                if num_part:
                    next_idx = int(num_part) + 1
            
            for exam in existing_list:
                if exam.get('isPaid') and exam.get('password'):
                    passwords.add(exam.get('password'))
                    
        except Exception as e:
            return None, None, None, None, f"Corrupted File: {e}"

    return next_idx, list(passwords), sha, existing_list, file_status

# ==========================================
# 🖥️ MAIN UI
# ==========================================
def main():
    # Force Light Theme in Config
    st.set_page_config(page_title="ExamPortal Admin", page_icon="🚀", layout="centered", initial_sidebar_state="collapsed")
    apply_custom_design()

    # --- SESSION STATE ---
    if 'auth' not in st.session_state: st.session_state.auth = False
    if 'fetched_course_id' not in st.session_state: st.session_state.fetched_course_id = None
    if 'exam_context' not in st.session_state: st.session_state.exam_context = {}

    # --- LOGIN SCREEN ---
    if not st.session_state.auth:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center;">
            <h1 class="gradient-text">Admin Login</h1>
            <p style="color: #64748B;">Secure Access for ExamPortal Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("login_form"):
                pwd = st.text_input("🔑 Access Key", type="password", placeholder="Enter Password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Access Dashboard")
                
                if submit:
                    if pwd == ADMIN_PASSWORD:
                        st.session_state.auth = True
                        st.rerun()
                    else:
                        st.error("Invalid Credentials")
        return

    # --- DASHBOARD HEADER ---
    c1, c2 = st.columns([4,1])
    with c1:
        st.markdown('<div class="gradient-text">ExamPortal Admin</div>', unsafe_allow_html=True)
        st.caption("🟢 SYSTEM ACTIVE | 🛡️ SECURE CONNECTION")
    with c2:
        if st.button("Log Out"):
            st.session_state.auth = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Custom Tabs
    tab_course, tab_exam = st.tabs(["📘 Course Manager", "📝 Exam Master"])

    # =======================================================
    # TAB 1: ADD NEW COURSE
    # =======================================================
    with tab_course:
        st.markdown("### ✨ Create New Course")
        st.markdown("Add new courses to the homepage list. Use unique IDs.")
        
        with st.form("new_course_form"):
            st.markdown("#### 1. Course Identity")
            col1, col2 = st.columns(2)
            c_id = col1.text_input("🆔 Unique Course ID", placeholder="e.g. med-25").strip()
            c_title = col2.text_input("📌 Course Title", placeholder="Medical Admission 2025")
            
            st.markdown("#### 2. Pricing & Metadata")
            col3, col4, col5 = st.columns(3)
            c_price = col3.number_input("💰 New Price (Tk)", value=150)
            c_old = col4.number_input("📉 Old Price (Tk)", value=5000)
            c_cat = col5.selectbox("📂 Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])

            st.markdown("#### 3. Visuals")
            c_img = st.text_input("🖼️ Image Filename", placeholder="image_name.png")
            if c_img:
                st.info(f"🔗 Link Preview: `{IMG_BASE_URL}{c_img}`")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Publish Course")

            if submitted:
                if not c_id or not c_title:
                    st.warning("⚠️ Please fill in the ID and Title fields.")
                else:
                    res = get_file_content(COURSE_LIST_PATH)
                    if res.status_code == 200:
                        data = res.json()
                        content = base64.b64decode(data['content']).decode('utf-8')
                        current_list = json.loads(content)
                        
                        is_duplicate = any(c['id'] == c_id for c in current_list)
                        
                        if is_duplicate:
                            st.error(f"⛔ Conflict: Course ID '{c_id}' is already taken!")
                        else:
                            new_obj = {
                                "id": c_id, "title": c_title, "price": c_price, 
                                "oldPrice": c_old, "category": c_cat,
                                "image": f"{IMG_BASE_URL}{c_img}"
                            }
                            updated_list = [new_obj] + current_list
                            updated_json = json.dumps(updated_list, indent=2, ensure_ascii=False)
                            
                            push_res = upload_file(COURSE_LIST_PATH, updated_json, f"Add Course: {c_title}", data['sha'])
                            if push_res.status_code in [200, 201]:
                                st.balloons()
                                st.success(f"✅ Success! Course '{c_title}' is live.")
                            else:
                                st.error(f"Failed: {push_res.json()}")

    # =======================================================
    # TAB 2: EXAM MASTER
    # =======================================================
    with tab_exam:
        st.markdown("### 📝 Exam Management")
        
        # --- CONTEXT FINDER SECTION ---
        with st.expander("🔍 Find Course ID (Search Database)", expanded=False):
            if st.button("Load All Courses"):
                with st.spinner("Fetching data..."):
                    res = get_file_content(COURSE_LIST_PATH)
                    if res.status_code == 200:
                        clist = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                        st.table([{"ID": c['id'], "Title": c['title']} for c in clist])

        col_search, col_btn = st.columns([3, 1])
        target_course_id = col_search.text_input("Target Course ID", placeholder="Enter ID to load exams (e.g. med25)")
        
        if col_btn.button("📥 Load Context"):
            if target_course_id:
                next_idx, pw_hist, sha, ex_list, status = analyze_exam_context(target_course_id)
                st.session_state.exam_context = {
                    "id": target_course_id, "next_idx": next_idx, "pw_hist": pw_hist,
                    "sha": sha, "existing_list": ex_list, "status": status
                }
                st.session_state.fetched_course_id = target_course_id
                st.toast(f"Loaded Context for {target_course_id}", icon="✅")
            else:
                st.error("Course ID is required.")

        # --- DYNAMIC FORM ---
        ctx = st.session_state.exam_context
        if st.session_state.fetched_course_id and ctx:
            
            st.markdown("---")
            
            # Custom Info Card
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
            
            with st.form("exam_add_form"):
                st.markdown("#### 1. Exam Details")
                e_title = st.text_input("📝 Exam Title", placeholder="e.g. HSTU Model Test 01")
                
                c1, c2, c3 = st.columns(3)
                e_time = c1.number_input("⏱️ Time (min)", value=60)
                e_ques = c2.number_input("❓ Questions", value=100)
                e_neg = c3.number_input("🚫 Negative Mark", value=0.25)

                st.markdown("#### 2. Access Settings")
                is_paid = st.checkbox("💎 Mark as Premium/Paid Exam")
                e_pass = ""
                if is_paid:
                    e_pass = st.text_input("🔒 Set Password", placeholder="Enter secret code")
                    if not e_pass: st.warning("⚠️ Password is mandatory for paid exams")

                st.markdown("#### 3. Question Data")
                q_json_str = st.text_area("📄 Paste JSON Body", height=200, placeholder='{\n  "examTitle": "Title",\n  "questions": []\n}')

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Dynamic Button Color based on Paid status (Visual Cue)
                btn_label = "🚀 Validate & Publish Premium Exam" if is_paid else "🚀 Validate & Publish Free Exam"
                verify_submit = st.form_submit_button(btn_label)

                if verify_submit:
                    errors = []
                    if not e_title: errors.append("Title is missing.")
                    if is_paid and not e_pass: errors.append("Password is missing.")
                    if not q_json_str: errors.append("JSON content is missing.")
                    
                    try: json.loads(q_json_str)
                    except json.JSONDecodeError as e: errors.append(f"Invalid JSON Format: {e}")

                    if errors:
                        for err in errors: st.error(f"❌ {err}")
                    else:
                        with st.status("⚙️ Processing Atomic Update...", expanded=True) as status:
                            auto_id = f"e{ctx['next_idx']}"
                            q_filename = f"q{ctx['next_idx']}.json"
                            
                            new_exam_card = {
                                "id": auto_id, "title": e_title, "time": e_time,
                                "totalQuestions": e_ques, "negativeMark": e_neg,
                                "questionFile": q_filename, "isPaid": is_paid
                            }
                            if is_paid: new_exam_card["password"] = e_pass

                            # Step 1: Upload Question
                            q_path = f"public/data/{ctx['id']}/{q_filename}"
                            st.write(f"📤 Uploading Question File ({q_filename})...")
                            q_res = upload_file(q_path, q_json_str, f"Add Exam Question {auto_id}")
                            
                            if q_res.status_code not in [200, 201]:
                                status.update(label="❌ Upload Failed", state="error")
                                st.error(f"GitHub Error: {q_res.json()}")
                            else:
                                st.write("✅ Question Uploaded! Updating Exam List...")
                                
                                # Step 2: Update List
                                list_path = f"public/data/{ctx['id']}/exams.json"
                                final_list = (ctx['existing_list'] or []) + [new_exam_card]
                                final_list_json = json.dumps(final_list, indent=2, ensure_ascii=False)
                                
                                l_res = upload_file(list_path, final_list_json, f"Update List {auto_id}", ctx['sha'])
                                
                                if l_res.status_code in [200, 201]:
                                    status.update(label="🎉 Exam Live!", state="complete", expanded=False)
                                    st.balloons()
                                    st.success(f"Exam **{auto_id}** is now LIVE!")
                                    st.session_state.fetched_course_id = None
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    status.update(label="⚠️ List Update Failed", state="error")
                                    st.error(f"Error: {l_res.json()}")

if __name__ == "__main__":
    main()
