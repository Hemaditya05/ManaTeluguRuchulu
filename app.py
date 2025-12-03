import streamlit as st
import datetime
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import List, Dict

# -----------------------------
# Config & Paths
# -----------------------------
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
USERS_FILE = DATA_DIR / "users.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
STYLE_FILE = APP_DIR / "style.css"

for p in [DATA_DIR, UPLOADS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Utilities
# -----------------------------

def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


USERS: Dict[str, Dict] = load_json(USERS_FILE, {})
SUBMISSIONS: List[Dict] = load_json(SUBMISSIONS_FILE, [])


def commit_users():
    save_json(USERS_FILE, USERS)


def commit_submissions():
    save_json(SUBMISSIONS_FILE, SUBMISSIONS)


# -----------------------------
# Minimal CSS (fallback)
# -----------------------------
DEFAULT_CSS = r"""
:root{--accent:#7c3aed;--muted:#6b7280;--card:#ffffff;--bg:#f8fafc}
body {background: var(--bg);} 
.header{display:flex;align-items:center;gap:16px}
.logo{font-weight:700;font-size:18px}
.subtitle{color:var(--muted);margin-top:-8px}
.recipe-card{background:var(--card);padding:12px;border-radius:12px;margin-bottom:12px;box-shadow:0 4px 12px rgba(2,6,23,0.06)}
.form-container{background:var(--card);padding:16px;border-radius:12px}
.small-muted{color:var(--muted);font-size:12px}
.placeholder{border:1px dashed #e5e7eb;padding:12px;border-radius:8px;color:var(--muted)}
"""

if not STYLE_FILE.exists():
    STYLE_FILE.write_text(DEFAULT_CSS, encoding="utf-8")

# -----------------------------
# Translations (kept compact)
# -----------------------------
translations = {
    "en": {
        "title": "Traditional Telugu Cuisine Data Platform",
        "subtitle": "Collecting recipes, stories & media from Telangana and Andhra Pradesh",
        "nav_home": "Home",
        "nav_explore": "Explore",
        "nav_contribute": "Contribute",
        "nav_about": "About",
        "nav_contact": "Contact",
        "login": "Login",
        "signup": "Sign Up",
        "logout": "Logout",
        "welcome": "Welcome",
        "explore_header": "Explore Our Culinary Heritage",
        "explore_intro": "Browse community-submitted recipes, media and stories.",
        "contribute_header": "Contribute a Recipe or Food Memory",
        "recipe_name": "Recipe Name",
        "region": "Region (Telangana / Andhra / District / Village)",
        "food_type": "Food Type",
        "breakfast": "Breakfast",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "snack": "Snack",
        "sweet": "Sweet",
        "pickle": "Pickle",
        "other": "Other",
        "ingredients": "Ingredients (one per line)",
        "steps": "Preparation Steps",
        "images": "Upload Images (jpg/png)",
        "videos": "Upload Videos (mp4)",
        "audios": "Upload Audio",
        "contributor_name": "Your Name (optional)",
        "contributor_email": "Your Email (optional)",
        "bio": "Short Bio / Context (optional)",
        "submit": "Submit",
        "success_msg": "Saved — thank you for contributing! 🙏",
        "about_header": "About the Project",
        "about_text": "A living archive of Telugu culinary heritage — multimedia friendly, community driven.",
        "contact_header": "Contact Us",
        "contact_info": "Email: support@team10-1.example | Hyderabad, Telangana",
        "login_header": "Login to Your Account",
        "signup_header": "Create a New Account",
        "username": "Username",
        "password": "Password",
        "username_exists": "Username already exists. Pick another one.",
        "signup_success": "Account created — please login.",
        "login_error": "Invalid username or password.",
    }
}

# -----------------------------
# Helpers for translations
# -----------------------------
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'


def T(k):
    return translations.get(st.session_state.lang, translations['en']).get(k, k)

# -----------------------------
# Session state defaults
# -----------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# -----------------------------
# Auth (very simple local auth)
# -----------------------------

def signup_flow(username: str, password: str):
    if username in USERS:
        return False, T('username_exists')
    USERS[username] = {
        'password': hash_password(password),
        'created_at': now_iso(),
    }
    commit_users()
    return True, T('signup_success')


def login_flow(username: str, password: str):
    if username not in USERS:
        return False, T('login_error')
    if USERS[username]['password'] != hash_password(password):
        return False, T('login_error')
    st.session_state.logged_in = True
    st.session_state.username = username
    return True, f"{T('welcome')}, {username}"

# -----------------------------
# File helpers
# -----------------------------

def save_uploaded_file(uploaded_file, subfolder: str = "misc") -> str:
    ext = Path(uploaded_file.name).suffix
    fname = f"{uuid.uuid4().hex}{ext}"
    folder = UPLOADS_DIR / subfolder
    folder.mkdir(exist_ok=True)
    target = folder / fname
    with open(target, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return str(target.relative_to(APP_DIR))

# -----------------------------
# Submission storage
# -----------------------------

def save_submission(data: dict, image_paths: List[str], video_paths: List[str], audio_paths: List[str]):
    entry = data.copy()
    entry['id'] = uuid.uuid4().hex
    entry['images'] = image_paths
    entry['videos'] = video_paths
    entry['audios'] = audio_paths
    entry['created_at'] = now_iso()
    entry['submitted_by'] = st.session_state.username or 'anonymous'
    SUBMISSIONS.append(entry)
    commit_submissions()
    return entry['id']


def get_all_submissions():
    return list(reversed(SUBMISSIONS))

# -----------------------------
# UI Components
# -----------------------------

def language_switcher():
    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("EN", key="lang_en"):
            st.session_state.lang = 'en'
    with cols[1]:
        if st.button("TE", key="lang_te"):
            st.session_state.lang = 'en'  # Telugu strings can be added similarly
    with cols[2]:
        st.markdown("<div class='small-muted'>Select language — English (TE coming soon)</div>", unsafe_allow_html=True)


def main_nav():
    NAV_PAGES = [T('nav_home'), T('nav_explore'), T('nav_contribute'), T('nav_about'), T('nav_contact')]
    cols = st.columns(len(NAV_PAGES))
    for i, label in enumerate(NAV_PAGES):
        if cols[i].button(label, key=f"nav-{i}"):
            mapping = {
                0: 'Home', 1: 'Explore', 2: 'Contribute', 3: 'About', 4: 'Contact'
            }
            st.session_state.page = mapping[i]


def auth_box():
    if st.session_state.logged_in:
        st.markdown(f"<div class='small-muted'>{T('welcome')}, <strong>{st.session_state.username}</strong></div>", unsafe_allow_html=True)
        if st.button(T('logout')):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.experimental_rerun()
    else:
        with st.expander(T('login_header')):
            u = st.text_input(T('username'), placeholder="eg: raj_1987")
            p = st.text_input(T('password'), type='password', placeholder="pick a secure password")
            if st.button(T('login')):
                ok, msg = login_flow(u, p)
                if ok:
                    st.success(msg)
                    st.experimental_rerun()
                else:
                    st.error(msg)
        with st.expander(T('signup_header')):
            su = st.text_input("New username", key="su_user", placeholder="choose a public handle")
            sp = st.text_input("New password", type='password', key="su_pass", placeholder="at least 8 chars")
            if st.button(T('signup')):
                ok, msg = signup_flow(su, sp)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# -----------------------------
# Page: Home
# -----------------------------

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title=T('title'))

with open(STYLE_FILE, 'r', encoding='utf-8') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

header_cols = st.columns([3, 6, 3])
with header_cols[0]:
    st.markdown("<div class='header'><div class='logo'>TeluguKitchen</div></div>", unsafe_allow_html=True)
with header_cols[1]:
    st.markdown(f"<div><h1>{T('title')}</h1><div class='subtitle'>{T('subtitle')}</div></div>", unsafe_allow_html=True)
with header_cols[2]:
    language_switcher()

st.markdown("---")

nav_col1, nav_col2 = st.columns([3, 9])
with nav_col1:
    main_nav()
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    auth_box()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Quick actions</div>", unsafe_allow_html=True)
    if st.button("Contribute (quick)"):
        st.session_state.page = 'Contribute'

# -----------------------------
# Page Router
# -----------------------------
page = st.session_state.page

if page == 'Home':
    with nav_col2:
        st.markdown(f"<div class='form-container'><h2>{T('explore_header')}</h2><p class='small-muted'>{T('explore_intro')}</p>", unsafe_allow_html=True)
        latest = get_all_submissions()[:5]
        if not latest:
            st.info("No submissions yet — be the first to add a family recipe!")
            st.markdown("<div class='placeholder'>Try contributing a quick recipe using the Contribute page. Placeholders are everywhere :)</div>", unsafe_allow_html=True)
        else:
            for s in latest:
                st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
                cols = st.columns([1, 3])
                with cols[0]:
                    if s.get('images'):
                        p = Path(s['images'][0])
                        if p.exists():
                            st.image(str(p), use_column_width=True)
                        else:
                            st.image("https://via.placeholder.com/300", use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300?text=No+Image", use_column_width=True)
                with cols[1]:
                    st.markdown(f"### {s.get('recipe_name', 'Untitled')}")
                    st.markdown(f"**Region:** {s.get('region','-')} • **Type:** {s.get('food_type','-')}")
                    st.markdown(f"<p class='small-muted'>Submitted by {s.get('submitted_by')} on {s.get('created_at')}</p>", unsafe_allow_html=True)
                    with st.expander('View details'):
                        st.markdown(f"**Ingredients**\n<pre>{s.get('ingredients','')}</pre>", unsafe_allow_html=True)
                        st.markdown(f"**Steps**\n<pre>{s.get('steps','')}</pre>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == 'Explore':
    with nav_col2:
        st.header(T('explore_header'))
        st.write(T('explore_intro'))
        # Filters and search
        q_col1, q_col2, q_col3 = st.columns([3, 2, 2])
        with q_col1:
            query = st.text_input('Search recipes, regions, or ingredients', placeholder='e.g. gongura, pesarattu, pulihora')
        with q_col2:
            region_filter = st.text_input('Filter by region', placeholder='e.g. Nalgonda, Vijayawada')
        with q_col3:
            type_filter = st.selectbox('Food type', ['', 'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Sweet', 'Pickle'])

        results = get_all_submissions()
        def match(s):
            text = ' '.join([s.get('recipe_name',''), s.get('region',''), s.get('ingredients',''), s.get('steps','')]).lower()
            if query and query.lower() not in text:
                return False
            if region_filter and region_filter.lower() not in s.get('region','').lower():
                return False
            if type_filter and type_filter != s.get('food_type'):
                return False
            return True
        matches = list(filter(match, results))
        st.markdown(f"### Results ({len(matches)})")
        if not matches:
            st.info('No results — try broader filters or add a placeholder sample.')
        for s in matches:
            st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
            cols = st.columns([1, 3])
            with cols[0]:
                if s.get('images'):
                    p = Path(s['images'][0])
                    if p.exists():
                        st.image(str(p), use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300", use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/300?text=No+Image", use_column_width=True)
            with cols[1]:
                st.markdown(f"### {s.get('recipe_name','Untitled')}")
                st.markdown(f"**Region:** {s.get('region','-')} • **Type:** {s.get('food_type','-')}")
                with st.expander('Details'):
                    st.markdown(f"**Ingredients**\n<pre>{s.get('ingredients','')}</pre>", unsafe_allow_html=True)
                    st.markdown(f"**Steps**\n<pre>{s.get('steps','')}</pre>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

elif page == 'Contribute':
    with nav_col2:
        st.header(T('contribute_header'))
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        with st.form('contribute_form'):
            recipe_name = st.text_input(T('recipe_name'), placeholder='e.g. Gongura Pappu – Amma recipe')
            region = st.text_input(T('region'), placeholder='State, District, Village — e.g. Telangana, Karimnagar, A village')
            food_type = st.selectbox(T('food_type'), [T('breakfast'), T('lunch'), T('dinner'), T('snack'), T('sweet'), T('pickle'), T('other')])
            ingredients = st.text_area(T('ingredients'), placeholder='One ingredient per line. e.g.\n- 1 cup rice\n- 1/2 cup urad dal', height=160)
            steps = st.text_area(T('steps'), placeholder='Step 1: ...\nStep 2: ...\nInclude tips, local names, approximate timings', height=280)
            st.markdown("---")
            img_files = st.file_uploader(T('images'), type=['png','jpg','jpeg'], accept_multiple_files=True)
            vid_files = st.file_uploader(T('videos'), type=['mp4','mov','mkv'], accept_multiple_files=True)
            aud_files = st.file_uploader(T('audios'), type=['mp3','wav','m4a'], accept_multiple_files=True)
            st.markdown("---")
            contributor_name = st.text_input(T('contributor_name'), placeholder='Optional — how should we credit you?')
            contributor_email = st.text_input(T('contributor_email'), placeholder='Optional — we will not spam')
            bio = st.text_area(T('bio'), placeholder='Optional context — who taught you this recipe? special occasions?')
            preview = st.checkbox('Show preview before submit')
            submitted = st.form_submit_button(T('submit'))

        if submitted:
            # Save files to disk
            img_paths = [save_uploaded_file(f, 'images') for f in (img_files or [])]
            vid_paths = [save_uploaded_file(f, 'videos') for f in (vid_files or [])]
            aud_paths = [save_uploaded_file(f, 'audios') for f in (aud_files or [])]
            data = {
                'recipe_name': recipe_name or 'Untitled Recipe',
                'region': region or 'Unknown region',
                'food_type': food_type,
                'ingredients': ingredients or '',
                'steps': steps or '',
                'contributor_name': contributor_name or '',
                'contributor_email': contributor_email or '',
                'bio': bio or '',
            }
            sid = save_submission(data, img_paths, vid_paths, aud_paths)
            st.success(T('success_msg'))
            st.markdown(f"<div class='small-muted'>Saved with id: {sid}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == 'About':
    with nav_col2:
        st.header(T('about_header'))
        st.write(T('about_text'))
        st.markdown("<div class='placeholder'>Project description placeholder — paste your long form project description here. This area supports rich text and images.</div>", unsafe_allow_html=True)

elif page == 'Contact':
    with nav_col2:
        st.header(T('contact_header'))
        st.write(T('contact_info'))
        st.markdown("<div class='placeholder'>Office address, phone numbers, or a contact form can go here.</div>", unsafe_allow_html=True)

# -----------------------------
# Footer: quick debug info (hidden by default)
# -----------------------------
with st.expander('Debug / Admin (dev only)'):
    st.write('Registered users', list(USERS.keys()))
    st.write('Total submissions', len(SUBMISSIONS))
    if st.button('Re-save submissions file (force)'):
        commit_submissions()
        st.success('Committed')

# -----------------------------
# EOF
# -----------------------------
