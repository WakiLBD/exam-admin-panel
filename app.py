import streamlit as st
import requests
import json
import base64
import time

# ==========================================
# 🎨 UI & UX DESIGN SYSTEM (ULTRA PREMIUM)
# ==========================================
def apply_custom_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* -----------------------
           1. GLOBAL THEME
           ----------------------- */
        .stApp {
            background-color: #0B0F19; /* Ultra Dark Blue/Black */
            color: #E0E0E0;
            font-family: 'Inter', sans-serif;
        }
        
        /* -----------------------
           2. HEADERS & TYPOGRAPHY
           ----------------------- */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }
        
        /* Gradient Text Effect for Headers */
        h1 {
            background: linear-gradient(90deg, #8B5CF6 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0px 4px 20px rgba(139, 92, 246, 0.3);
        }
        
        h3 {
            color: #A0AEC0;
            font-size: 1.1rem !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 20px !important;
        }

        /* -----------------------
           3. GLASSMORPHISM CARDS
           ----------------------- */
        /* Form Container Styling */
        div[data-testid="stForm"] {
            background: #151921;
            border: 1px solid #2D3748;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 50px -12px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        div[data-testid="stForm"]:hover {
            border-color: #4A5568;
            box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.6);
        }

        /* -----------------------
           4. MODERN INPUT FIELDS
           ----------------------- */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div, 
        .stTextArea > div > div > textarea {
            background-color: #0D1117; 
            color: #FFFFFF; 
            border-radius: 12px; 
            border: 2px solid #232936;
            padding: 10px 15px;
            font-size: 15px;
            transition: all 0.3s ease;
        }

        /* Focus Glow Effect */
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #8B5CF6; /* Purple Border */
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1); /* Soft Purple Ring */
        }

        /* -----------------------
           5. PREMIUM BUTTONS (GRADIENT)
           ----------------------- */
        .stButton > button {
            background: linear-gradient(92.88deg, #10B981 9.16%, #3B82F6 43.89%, #8B5CF6 64.72%);
            color: white;
            border: none;
            padding: 12px 32px;
            border-radius: 50px; /* Capsule Shape */
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.5px;
            width: 100%;
            text-transform: uppercase;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 20px -10px rgba(59, 130, 246, 0.5);
        }

        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 20px 30px -10px rgba(139, 92, 246, 0.6);
            filter: brightness(1.1);
        }
        
        .stButton > button:active {
            transform: scale(0.98);
        }

        /* -----------------------
           6. TABS & BADGES
           ----------------------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px;
            border-bottom: none;
            background-color: #11141B;
            padding: 10px;
            border-radius: 15px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 45px;
            border-radius: 10px;
            background-color: transparent;
            color: #718096;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background-color: #2D3748;
            color: #63B3ED; /* Light Blue Text */
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        /* Status Messages (Capsule Style) */
        .stSuccess, .stError, .stInfo, .stWarning {
            border-radius: 15px;
            border: none;
            font-weight: 500;
        }
        .stSuccess { background-color: rgba(16, 185, 129, 0.1); border: 1px solid #059669; color: #34D399; }
        .stError { background-color: rgba(239, 68, 68, 0.1); border: 1px solid #DC2626; color: #F87171; }
        .stInfo { background-color: rgba(59, 130, 246, 0.1); border: 1px solid #2563EB; color: #60A5FA; }

        /* Expander Styling */
        .streamlit-expanderHeader {
            background-color: #1A202C;
            border-radius: 10px;
            color: #E2E8F0;
            font-weight: 600;
        }
        
        /* Table Styling */
        div[data-testid="stTable"] {
            background-color: #161920;
            border-radius: 10px;
            overflow: hidden;
            font-size: 14px;
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
    GITHUB_TOKEN = "YOUR_TOKEN" # Local Test
    ADMIN_PASSWORD = "123"

# ⚠️ আপনার তথ্য (অবশ্যই চেক করবেন)
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
    st.set_page_config(page_title="ExamPortal Admin Pro", page_icon="⚡", layout="centered")
    apply_custom_design()

    # --- SESSION STATE ---
    if 'auth' not in st.session_state: st.session_state.auth = False
    if 'fetched_course_id' not in st.session_state: st.session_state.fetched_course_id = None
    if 'exam_context' not in st.session_state: st.session_state.exam_context = {}

    # --- LOGIN SCREEN ---
    if not st.session_state.auth:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>🔐 Secure Admin Access</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #718096;'>Enter your credentials to manage the Exam Portal</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            pwd = st.text_input("Security Key", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Unlock Dashboard")
            
            if submit:
                if pwd == ADMIN_PASSWORD:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("⛔ Access Denied: Invalid Security Key")
        return

    # --- DASHBOARD HEADER ---
    st.markdown("<h1>🚀 ExamPortal Command Center</h1>", unsafe_allow_html=True)
    st.caption("STATUS: 🟢 SYSTEM ONLINE | 🔒 ENCRYPTED CONNECTION")
    
    # Custom Tabs with Icons
    tab_course, tab_exam = st.tabs(["📘 Course Manager", "📝 Exam Master"])

    # =======================================================
    # TAB 1: ADD NEW COURSE
    # =======================================================
    with tab_course:
        st.markdown("<h3>Create New Course</h3>", unsafe_allow_html=True)
        
        with st.form("new_course_form"):
            st.markdown("**1. Basic Information**")
            col1, col2 = st.columns(2)
            c_id = col1.text_input("Course ID (Unique)", placeholder="e.g. med25").strip()
            c_title = col2.text_input("Course Title", placeholder="🔥 Medical Admission 2025")
            
            st.markdown("**2. Pricing & Category**")
            col3, col4 = st.columns(2)
            c_price = col3.number_input("New Price (Tk)", value=150)
            c_old = col4.number_input("Old Price (Tk)", value=5000)
            c_cat = st.selectbox("Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])

            st.markdown("**3. Assets**")
            c_img = st.text_input("Image Filename", placeholder="img.jpg (Auto-linked to CDN)")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✨ Publish Course to Live")

            if submitted:
                if not c_id or not c_title:
                    st.warning("⚠️ ID and Title are required!")
                else:
                    res = get_file_content(COURSE_LIST_PATH)
                    if res.status_code == 200:
                        data = res.json()
                        content = base64.b64decode(data['content']).decode('utf-8')
                        current_list = json.loads(content)
                        
                        is_duplicate = any(c['id'] == c_id for c in current_list)
                        
                        if is_duplicate:
                            st.error(f"⛔ STOP! Course ID '{c_id}' already exists!")
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
                                st.success(f"✅ Course '{c_title}' Added to TOP!")
                            else:
                                st.error(f"Failed: {push_res.json()}")

    # =======================================================
    # TAB 2: EXAM MASTER
    # =======================================================
    with tab_exam:
        st.markdown("<h3>Exam Management System</h3>", unsafe_allow_html=True)

        # --- CONTEXT FINDER SECTION ---
        with st.expander("🔍 Find Course ID (Database Search)", expanded=False):
            if st.button("Load All Courses"):
                with st.spinner("Connecting to Database..."):
                    res = get_file_content(COURSE_LIST_PATH)
                    if res.status_code == 200:
                        clist = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                        st.table([{"ID": c['id'], "Title": c['title']} for c in clist])

        col_search, col_btn = st.columns([3, 1])
        target_course_id = col_search.text_input("Target Course ID", placeholder="Paste Course ID here (e.g. med25)")
        
        if col_btn.button("📥 Load Context"):
            if target_course_id:
                next_idx, pw_hist, sha, ex_list, status = analyze_exam_context(target_course_id)
                st.session_state.exam_context = {
                    "id": target_course_id, "next_idx": next_idx, "pw_hist": pw_hist,
                    "sha": sha, "existing_list": ex_list, "status": status
                }
                st.session_state.fetched_course_id = target_course_id
                st.success(f"System Ready! Mode: {status.upper()}")
            else:
                st.warning("Please enter a Course ID.")

        # --- DYNAMIC FORM ---
        ctx = st.session_state.exam_context
        if st.session_state.fetched_course_id and ctx:
            
            st.markdown("---")
            # Smart Info Chips
            c1, c2, c3 = st.columns(3)
            c1.info(f"📂 **Folder:** `{ctx['id']}`")
            c2.info(f"🔢 **Auto ID:** `e{ctx['next_idx']}`")
            c3.info(f"📄 **File:** `q{ctx['next_idx']}.json`")

            # Password History Badge
            if ctx['pw_hist']:
                st.caption(f"🔑 **History:** {', '.join(ctx['pw_hist'])}")
            
            with st.form("exam_add_form"):
                st.markdown("**1. Exam Configuration**")
                e_title = st.text_input("Exam Title", placeholder="HSTU Model Test 01")
                
                c1, c2, c3 = st.columns(3)
                e_time = c1.number_input("Time (min)", value=60)
                e_ques = c2.number_input("Total Questions", value=100)
                e_neg = c3.number_input("Negative Mark", value=0.25)

                st.markdown("**2. Access Control**")
                is_paid = st.checkbox("💎 Premium / Paid Exam")
                e_pass = ""
                if is_paid:
                    e_pass = st.text_input("Set Password", placeholder="Enter secret access code")
                    if not e_pass: st.warning("⚠️ Password Required")

                st.markdown("**3. Question Data (JSON)**")
                q_json_str = st.text_area("Paste JSON Content", height=200, placeholder='{\n  "examTitle": "...",\n  "questions": [...]\n}')

                st.markdown("<br>", unsafe_allow_html=True)
                verify_submit = st.form_submit_button("🚀 Validate & Upload Exam")

                if verify_submit:
                    errors = []
                    if not e_title: errors.append("Title is missing.")
                    if is_paid and not e_pass: errors.append("Password missing.")
                    if not q_json_str: errors.append("JSON missing.")
                    
                    try: json.loads(q_json_str)
                    except json.JSONDecodeError as e: errors.append(f"Invalid JSON: {e}")

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
                            st.write(f"📤 Uploading Question File...")
                            q_res = upload_file(q_path, q_json_str, f"Add Exam Question {auto_id}")
                            
                            if q_res.status_code not in [200, 201]:
                                status.update(label="❌ Upload Failed", state="error")
                                st.error(f"GitHub Error: {q_res.json()}")
                            else:
                                st.write("✅ Question Uploaded! Updating Index...")
                                
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
