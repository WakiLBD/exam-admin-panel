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
    TOKEN_MAIN = st.secrets["GITHUB_TOKEN_MAIN"] # For ExamPortal
    TOKEN_PS = st.secrets["GITHUB_TOKEN_PS"]     # For PS Website
except:
    # Fallback for local testing if secrets.toml is missing (Not recommended for prod)
    ADMIN_PASSWORD = "123"
    TOKEN_MAIN = "Add_Your_Token_Here"
    TOKEN_PS = "Add_Your_Token_Here"

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
        .stSelectbox > div > div > div {
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
        
        /* STATUS PILLS */
        .id-badge {
            background-color: #ECFDF5;
            color: #059669;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid #D1FAE5;
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

def push_data(owner, repo, path, token, content_obj, message, sha):
    """Generic push function for any repo"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        json_str = json.dumps(content_obj, indent=2, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": message,
            "content": encoded,
            "sha": sha,
            "branch": "main"
        }
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
    
    if res['status'] == 'success':
        sha = res['sha']
        existing_list = res['content']
        if existing_list:
            last_id = existing_list[-1].get('id', 'e0')
            num = ''.join(filter(str.isdigit, last_id))
            if num: next_idx = int(num) + 1
        
        for ex in existing_list:
            if ex.get('password'): passwords.add(ex['password'])
            
    return next_idx, list(passwords), sha, existing_list

# ==========================================
# 🖥️ MAIN APPLICATION
# ==========================================
def main():
    apply_custom_design()
    
    # --- AUTHENTICATION ---
    if 'auth' not in st.session_state: st.session_state.auth = False
    
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

    # --- DASHBOARD UI ---
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
    # TAB 1: EXAM PORTAL (Existing Logic)
    # =======================================================
    with tab_examportal:
        sub_tab1, sub_tab2 = st.tabs(["📘 Add Course", "📝 Exam Master"])
        
        # --- SUB TAB: NEW COURSE ---
        with sub_tab1:
            st.info("Adds new course to `src/data/CourseList.json` (ExamPortal)")
            with st.form("ep_course_form"):
                c1, c2 = st.columns(2)
                ep_id = c1.text_input("🆔 ID", placeholder="med-25")
                ep_title = c2.text_input("📌 Title", placeholder="Course Name")
                
                c3, c4, c5 = st.columns(3)
                ep_price = c3.number_input("Price", value=150)
                ep_old = c4.number_input("Old Price", value=5000)
                ep_cat = c5.selectbox("Category", ["HSC-26 Academic", "HSC-26 Admission", "HSC-25 Admission"])
                
                ep_img = st.text_input("🖼️ Image Name", placeholder="img.jpg")
                
                if st.form_submit_button("🚀 Upload to ExamPortal"):
                    if not ep_id: st.warning("ID Required")
                    else:
                        res = fetch_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN)
                        if res['status'] == 'success':
                            new_entry = {
                                "id": ep_id, "title": ep_title, "price": ep_price,
                                "oldPrice": ep_old, "category": ep_cat, 
                                "image": f"{IMG_CDN_BASE}{ep_img}"
                            }
                            updated_list = [new_entry] + res['content']
                            push_res = push_data(REPO_1_OWNER, REPO_1_NAME, PATH_1_COURSE, TOKEN_MAIN, updated_list, f"Add {ep_title}", res['sha'])
                            if push_res and push_res.status_code in [200, 201]:
                                st.balloons()
                                st.success(f"Added {ep_title}")
                        else:
                            st.error("Failed to fetch current list")

        # --- SUB TAB: EXAM MASTER ---
        with sub_tab2:
            st.write("Manages `public/data/ID/exams.json`")
            # (Keeping it brief as requested in prompt, focusing on integration)
            target_id = st.text_input("Enter Course ID for Exam Context", placeholder="e.g. med25")
            if st.button("Load Context"):
                if target_id:
                    idx, pws, sha, curr_list = analyze_exam_context(target_id)
                    st.session_state.ep_context = {"id": target_id, "idx": idx, "sha": sha, "list": curr_list}
                    st.success(f"Loaded {target_id}. Next Exam: e{idx}")

            if 'ep_context' in st.session_state:
                ctx = st.session_state.ep_context
                with st.form("ep_exam_form"):
                    ex_title = st.text_input("Exam Title")
                    ex_json = st.text_area("Questions JSON")
                    if st.form_submit_button("Publish Exam"):
                        # (Simplified upload logic for brevity, full logic in previous robust code)
                        st.info("Logic similar to previous app would execute here.")

    # =======================================================
    # TAB 2: PS WEBSITE MANAGER (The New Feature)
    # =======================================================
    with tab_ps:
        st.markdown("### 🌐 Premium Subscriptions Course Manager")
        st.markdown("Updates `courses/courses.json` in `ps` repo.")
        
        # 1. AUTO-FETCH & ID CALCULATION
        with st.status("🔄 Syncing with PS Database...", expanded=True) as status:
            ps_data = fetch_data(REPO_2_OWNER, REPO_2_NAME, PATH_2_COURSE, TOKEN_PS)
            
            if ps_data['status'] == 'success':
                current_courses = ps_data['content']
                # Calculate Max ID
                all_ids = [c.get('id', 0) for c in current_courses if isinstance(c.get('id'), int)]
                next_id = max(all_ids) + 1 if all_ids else 100
                
                status.update(label=f"✅ Synced! Next Auto-ID: {next_id}", state="complete", expanded=False)
                
                # --- THE FORM ---
                with st.form("ps_add_form"):
                    st.markdown(f"#### 🆔 New Course ID: <span class='id-badge'>{next_id}</span> (Auto-Generated)", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    ps_title = col_a.text_input("📌 Course Title", placeholder="🔥 ACS ENGINEERING 2026🔥")
                    ps_img = col_b.text_input("🖼️ Image Name", placeholder="IMG_2026.jpg")
                    if ps_img: st.caption(f"Preview: {IMG_CDN_BASE}{ps_img}")

                    col_c, col_d, col_e = st.columns(3)
                    ps_price = col_c.number_input("💰 Price", value=350)
                    ps_old = col_d.number_input("📉 Original Price", value=5000)
                    ps_dur = col_e.number_input("⏳ Duration (Months)", value=2.5, step=0.5)

                    col_f, col_g = st.columns(2)
                    # Dropdowns as requested
                    ps_grade = col_f.selectbox("🎓 Grade", [
                        "HSC 27", "HSC 26", "Admission 26", "Admission 25"
                    ])
                    ps_type = col_g.selectbox("🏷️ Course Type", [
                        'ACS', 'UDVASH', 'Physics Hunters', 'Bondi Pathshala', 
                        'RTDS', 'Battle of Biology', 'Alchemy', 'CPS'
                    ])

                    col_h, col_i = st.columns(2)
                    ps_stud = col_h.number_input("👥 Students", value=1000, step=100)
                    ps_rate = col_i.slider("⭐ Rating", 1, 5, 5)

                    st.markdown("---")
                    ps_submit = st.form_submit_button("🚀 Publish to PS Website")

                    if ps_submit:
                        if not ps_title or not ps_img:
                            st.warning("⚠️ Title and Image are required!")
                        else:
                            # 2. CONSTRUCT ROBUST JSON
                            new_ps_course = {
                                "id": next_id,
                                "title": ps_title,
                                "grade": [ps_grade], # Array format
                                "courseType": ps_type,
                                "price": ps_price,
                                "originalPrice": ps_old,
                                "duration": f"{ps_dur} months", # String format
                                "students": ps_stud,
                                "rating": ps_rate,
                                "image": f"{IMG_CDN_BASE}{ps_img}"
                            }

                            # 3. PREPEND & PUSH
                            updated_ps_list = [new_ps_course] + current_courses
                            
                            with st.spinner("🚀 Pushing to PremiumSubscriptions Repo..."):
                                res_push = push_data(
                                    REPO_2_OWNER, 
                                    REPO_2_NAME, 
                                    PATH_2_COURSE, 
                                    TOKEN_PS, 
                                    updated_ps_list, 
                                    f"Add Course {next_id}: {ps_title}", 
                                    ps_data['sha']
                                )
                                
                                if res_push and res_push.status_code in [200, 201]:
                                    st.balloons()
                                    st.success(f"✅ Successfully Added: **{ps_title}** (ID: {next_id})")
                                    # Show JSON Preview
                                    with st.expander("View Data Payload"):
                                        st.json(new_ps_course)
                                    time.sleep(2)
                                    st.rerun() # Refresh to update ID
                                else:
                                    st.error("❌ Failed to push data.")

            else:
                st.error(f"❌ Could not fetch PS Database. Check Token. ({ps_data.get('msg')})")

if __name__ == "__main__":
    main()
