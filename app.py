import streamlit as st
import requests
import json
import base64
import time

# ==========================================
# 🎨 UI & UX DESIGN SYSTEM (PREMIUM LOOK)
# ==========================================
def apply_custom_design():
    st.markdown("""
    <style>
        /* Global Theme */
        .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
        
        /* Input Fields */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div, 
        .stTextArea > div > div > textarea {
            background-color: #1F2229; 
            color: #FFFFFF; 
            border-radius: 8px; 
            border: 1px solid #383B42;
        }
        .stTextInput > div > div > input:focus { border-color: #FF4B4B; }

        /* Buttons (Gradient & Animation) */
        .stButton > button {
            background: linear-gradient(135deg, #FF4B4B 0%, #FF914D 100%);
            color: white; border: none; padding: 12px 28px; border-radius: 10px;
            font-weight: 600; letter-spacing: 0.5px; width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
        }

        /* Success/Error/Info Boxes */
        .stSuccess, .stError, .stInfo { border-radius: 8px; }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 2px solid #383B42; }
        .stTabs [data-baseweb="tab"] { height: 50px; color: #A0A0A0; font-weight: 500; }
        .stTabs [aria-selected="true"] { color: #FF4B4B; border-bottom-color: #FF4B4B; }
        
        /* Card Container */
        .css-card {
            background-color: #161920; padding: 20px; border-radius: 12px;
            border: 1px solid #2D3038; margin-bottom: 20px;
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

REPO_OWNER = 'WakiLBD'  # <--- Change This
REPO_NAME = 'ExamPortal'     # <--- Change This
BRANCH = 'main'
COURSE_LIST_PATH = 'src/data/CourseList.json'
IMG_BASE_URL = "https://cdn.jsdelivr.net/gh/PremiumSubscriptions/premium-subscriptions-bot@main/"

headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# -------------------------------------------
# 🛠️ GITHUB API HELPERS (ROBUST)
# -------------------------------------------
def get_file_content(path):
    """Returns content, sha, and status code safely"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    res = requests.get(url, headers=headers)
    return res

def upload_file(path, content_str, message, sha=None):
    """Atomic Upload Function"""
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
    """
    Checks if exams.json exists.
    Returns: Next ID, Password History, Existing SHA (if any), Existing List
    """
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
            
            # Logic: Find last ID number (e3 -> 3)
            if existing_list:
                last_item = existing_list[-1]
                last_id_str = last_item.get('id', 'e0') # e.g., "e12"
                # Extract number part safely
                num_part = ''.join(filter(str.isdigit, last_id_str))
                if num_part:
                    next_idx = int(num_part) + 1
            
            # Collect Passwords
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
    st.set_page_config(page_title="ExamPortal Admin Pro", page_icon="🔥", layout="centered")
    apply_custom_design()

    # --- SESSION STATE INITIALIZATION ---
    if 'auth' not in st.session_state: st.session_state.auth = False
    if 'fetched_course_id' not in st.session_state: st.session_state.fetched_course_id = None
    if 'exam_context' not in st.session_state: st.session_state.exam_context = {}

    # --- LOGIN SCREEN ---
    if not st.session_state.auth:
        st.markdown("<br><h1 style='text-align: center; color: #FF4B4B;'>🛡️ Admin Panel</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Security Key", type="password", placeholder="••••••••")
        if st.button("Authenticate System"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else: st.error("⛔ Access Denied")
        return

    # --- DASHBOARD HEADER ---
    st.markdown("## 🔥 ExamPortal Command Center")
    st.caption("v2.5 | Robust Error Handling | Auto-Scaling ID System")

    tab_course, tab_exam = st.tabs(["📘 Course Manager", "📝 Exam Master"])

    # =======================================================
    # TAB 1: ADD NEW COURSE (PREPEND LOGIC)
    # =======================================================
    with tab_course:
        with st.container():
            st.markdown("### 🚀 Add New Course")
            
            with st.form("new_course_form"):
                col1, col2 = st.columns(2)
                c_id = col1.text_input("Course ID (Unique)", placeholder="e.g. med25").strip()
                c_price = col1.number_input("Price (Tk)", value=150)
                
                c_cat = col2.selectbox("Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])
                c_old = col2.number_input("Old Price", value=5000)
                
                c_title = st.text_input("Course Title", placeholder="🔥 Medical Admission 2025")
                c_img = st.text_input("Image File", placeholder="img.jpg (Auto-linked to CDN)")

                submitted = st.form_submit_button("💎 Publish Course")

                if submitted:
                    if not c_id or not c_title:
                        st.warning("⚠️ ID and Title are required!")
                    else:
                        # 1. Check duplicate ID Logic
                        res = get_file_content(COURSE_LIST_PATH)
                        if res.status_code == 200:
                            data = res.json()
                            content = base64.b64decode(data['content']).decode('utf-8')
                            current_list = json.loads(content)
                            
                            # ID Check
                            is_duplicate = any(c['id'] == c_id for c in current_list)
                            
                            if is_duplicate:
                                st.error(f"⛔ STOP! Course ID '{c_id}' already exists!")
                            else:
                                # Safe Prepend
                                new_obj = {
                                    "id": c_id, "title": c_title, "price": c_price, 
                                    "oldPrice": c_old, "category": c_cat,
                                    "image": f"{IMG_BASE_URL}{c_img}"
                                }
                                updated_list = [new_obj] + current_list
                                updated_json = json.dumps(updated_list, indent=2, ensure_ascii=False)
                                
                                # Push
                                push_res = upload_file(COURSE_LIST_PATH, updated_json, f"Add Course: {c_title}", data['sha'])
                                if push_res.status_code in [200, 201]:
                                    st.balloons()
                                    st.success(f"✅ Course '{c_title}' Added to TOP!")
                                else:
                                    st.error(f"Failed: {push_res.json()}")

    # =======================================================
    # TAB 2: EXAM MASTER (THE ROBUST LOGIC)
    # =======================================================
    with tab_exam:
        st.markdown("### 📝 Intelligent Exam Uploader")

        # --- STEP 1: FIND COURSE & LOAD CONTEXT ---
        with st.expander("🔍 Don't know the ID? Click to find Course IDs"):
            if st.button("Load All Courses"):
                with st.spinner("Fetching Course List..."):
                    res = get_file_content(COURSE_LIST_PATH)
                    if res.status_code == 200:
                        clist = json.loads(base64.b64decode(res.json()['content']).decode('utf-8'))
                        st.table([{"ID": c['id'], "Title": c['title']} for c in clist])

        col_search, col_btn = st.columns([3, 1])
        target_course_id = col_search.text_input("Target Course ID", placeholder="Paste Course ID here (e.g. med25)")
        
        # Context Loading Button
        if col_btn.button("📥 Fetch Context"):
            if target_course_id:
                next_idx, pw_hist, sha, ex_list, status = analyze_exam_context(target_course_id)
                st.session_state.exam_context = {
                    "id": target_course_id,
                    "next_idx": next_idx,
                    "pw_hist": pw_hist,
                    "sha": sha,
                    "existing_list": ex_list,
                    "status": status
                }
                st.session_state.fetched_course_id = target_course_id
                st.success(f"Context Loaded! Status: {status.upper()}")
            else:
                st.warning("Please enter a Course ID first.")

        # --- STEP 2: DYNAMIC FORM (ONLY SHOWS IF CONTEXT LOADED) ---
        ctx = st.session_state.exam_context
        
        if st.session_state.fetched_course_id and ctx:
            
            st.divider()
            # Info Bar
            cols = st.columns(3)
            cols[0].info(f"📂 Folder: {ctx['id']}")
            cols[1].info(f"🔢 Auto ID: e{ctx['next_idx']}")
            cols[2].info(f"📄 File: q{ctx['next_idx']}.json")

            # Password Suggestions
            if ctx['pw_hist']:
                st.caption(f"🔑 Used Passwords: {', '.join(ctx['pw_hist'])}")
            elif ctx['status'] == "new":
                st.caption("🆕 New Course - No password history.")
            else:
                st.caption("🔓 No paid exams found previously.")

            # Input Form
            with st.form("exam_add_form"):
                e_title = st.text_input("Exam Title", placeholder="HSTU Model Test 01")
                
                c1, c2, c3 = st.columns(3)
                e_time = c1.number_input("Time (min)", value=60)
                e_ques = c2.number_input("Total Questions", value=100)
                e_neg = c3.number_input("Negative Mark", value=0.25)

                # Payment Logic
                is_paid = st.checkbox("💲 Is this a PAID Exam?")
                e_pass = ""
                if is_paid:
                    e_pass = st.text_input("Set Password", placeholder="Enter secret code")
                    if not e_pass:
                        st.warning("⚠️ Password is required for Paid Exams!")

                # Question JSON
                st.markdown("#### 📄 Paste Question JSON Content")
                q_json_str = st.text_area("JSON Body", height=200, placeholder='{\n  "examTitle": "...",\n  "questions": [...]\n}')

                # SUBMIT LOGIC
                verify_submit = st.form_submit_button("🚀 Validate & Publish System")

                if verify_submit:
                    # 🛡️ VALIDATION LAYER
                    errors = []
                    if not e_title: errors.append("Title is missing.")
                    if is_paid and not e_pass: errors.append("Password missing for Paid Exam.")
                    if not q_json_str: errors.append("Question JSON missing.")
                    
                    # JSON Syntax Check
                    try:
                        json.loads(q_json_str)
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid JSON Format: {e}")

                    if errors:
                        for err in errors: st.error(f"❌ {err}")
                    else:
                        # ✅ ALL GREEN - START ATOMIC UPDATE
                        with st.status("⚙️ Processing Request...", expanded=True) as status:
                            
                            # 1. Prepare Data
                            auto_id = f"e{ctx['next_idx']}"
                            q_filename = f"q{ctx['next_idx']}.json"
                            
                            new_exam_card = {
                                "id": auto_id,
                                "title": e_title,
                                "time": e_time,
                                "totalQuestions": e_ques,
                                "negativeMark": e_neg,
                                "questionFile": q_filename,
                                "isPaid": is_paid
                            }
                            if is_paid:
                                new_exam_card["password"] = e_pass

                            # 2. Upload Question File FIRST (public/data/id/qX.json)
                            # GitHub will create folder automatically if missing
                            q_path = f"public/data/{ctx['id']}/{q_filename}"
                            st.write(f"📤 Uploading Question File ({q_filename})...")
                            
                            q_res = upload_file(q_path, q_json_str, f"Add Exam Question {auto_id}")
                            
                            if q_res.status_code not in [200, 201]:
                                status.update(label="❌ Failed at Step 1 (Question Upload)", state="error")
                                st.error(f"GitHub Error: {q_res.json()}")
                            else:
                                st.write("✅ Question Uploaded! Updating List...")
                                
                                # 3. Update exams.json (Append Mode)
                                list_path = f"public/data/{ctx['id']}/exams.json"
                                
                                # Determine new list content
                                if ctx['existing_list']:
                                    final_list = ctx['existing_list'] + [new_exam_card]
                                else:
                                    final_list = [new_exam_card] # New file creation
                                
                                final_list_json = json.dumps(final_list, indent=2, ensure_ascii=False)
                                
                                # Upload List
                                l_res = upload_file(list_path, final_list_json, f"Update List {auto_id}", ctx['sha'])
                                
                                if l_res.status_code in [200, 201]:
                                    status.update(label="🎉 Operation Successful!", state="complete", expanded=False)
                                    st.balloons()
                                    st.success(f"Exam **{auto_id}** added to **{ctx['id']}** successfully!")
                                    
                                    # Clear Cache to force reload next time
                                    st.session_state.fetched_course_id = None
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    status.update(label="⚠️ List Update Failed (Orphaned Question)", state="error")
                                    st.error(f"Question uploaded but List failed: {l_res.json()}")

if __name__ == "__main__":
    main()