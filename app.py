import streamlit as st
import datetime

# --- Page Configuration ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --- Language Translations ---
translations = {
    "en": {
        "title": "Traditional Telugu Cuisine Data Platform",
        "subtitle": "A living repository for authentic Telugu food heritage.",
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
        "explore_intro": "Browse recipes and food memories shared by our community.",
        "contribute_header": "Contribute a Recipe or Food Memory",
        "recipe_name": "Recipe Name",
        "region": "Region (e.g., Telangana, Andhra Pradesh, District, Village)",
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
        "images": "Upload Images",
        "videos": "Upload Videos",
        "audios": "Upload Audio (interviews, instructions)",
        "contributor_name": "Your Name (optional)",
        "contributor_email": "Your Email (optional)",
        "bio": "Short Bio / Context (optional)",
        "submit": "Submit",
        "success_msg": "Your submission has been saved! Thank you for contributing. 🙏",
        "about_header": "About the Project",
        "about_text": "This platform is designed to collect and preserve the rich food heritage of Telugu-speaking regions. By enabling users to contribute recipes, images, and stories, we aim to create a digital archive that keeps our culinary legacy alive for future generations. Join us!",
        "contact_header": "Contact Us",
        "contact_info": "Email: support@Team10-1 | Hyderabad, Telangana",
        "login_header": "Login to Your Account",
        "signup_header": "Create a New Account",
        "username": "Username",
        "password": "Password",
        "username_exists": "Username already exists. Please choose another one.",
        "signup_success": "Account created successfully! Please login.",
        "login_error": "Invalid username or password.",
    },
    # Telugu translations omitted for brevity (add them if needed)
}

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if "users" not in st.session_state:
    st.session_state.users = {}  # username: password

def T(key):
    return translations[st.session_state.lang].get(key, key)

# --- Authentication Functions (In-Memory, for demo only) ---
def signup_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = password
    return True

def check_user(username, password):
    return st.session_state.users.get(username) == password

# --- UI Components ---
def language_switcher():
    with st.container():
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("English", use_container_width=True, key="lang_en"):
                st.session_state.lang = 'en'
                st.rerun()
        with cols[1]:
            if st.button("తెలుగు", use_container_width=True, key="lang_te"):
                st.session_state.lang = 'te'
                st.rerun()

def main_nav():
    NAV_PAGES = ["nav_home", "nav_explore", "nav_contribute", "nav_about", "nav_contact"]
    page_map = {"nav_home": "Home", "nav_explore": "Explore", "nav_contribute": "Contribute", "nav_about": "About", "nav_contact": "Contact"}
    cols = st.columns(len(NAV_PAGES))
    for i, page_key in enumerate(NAV_PAGES):
        with cols[i]:
            if st.button(T(page_key), key=f"nav-{page_key}", use_container_width=True):
                st.session_state.page = page_map[page_key]
                st.rerun()

def auth_nav():
    if st.session_state.logged_in:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<div class='welcome-text'>{T('welcome')}, {st.session_state.username}!</div>", unsafe_allow_html=True)
        with col2:
            if st.button(T('logout'), key="logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.page = "Home"
                st.rerun()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(T('login'), key="login_nav", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()
        with col2:
            if st.button(T('signup'), key="signup_nav", use_container_width=True):
                st.session_state.page = "Signup"
                st.rerun()

# --- Header Section ---
with st.container():
    col1, col2, col3 = st.columns([1.5, 5, 1.5])
    with col1:
        language_switcher()
    with col2:
        main_nav()
    with col3:
        auth_nav()
    st.markdown("<hr class='header-divider'>", unsafe_allow_html=True)

# --- Page Routing ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='main-container home-content'>", unsafe_allow_html=True)
    st.markdown(f"<h1>{T('title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{T('subtitle')}</p>", unsafe_allow_html=True)
    if st.button(T('nav_explore'), key="home_explore_btn"):
        st.session_state.page = "Explore"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Explore":
    st.markdown(f"<div class='main-container'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('explore_header')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p>{T('explore_intro')}</p>", unsafe_allow_html=True)
    st.info("No recipes have been submitted yet. Be the first to contribute!")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Contribute":
    if not st.session_state.logged_in:
        st.warning("Please log in to contribute a recipe.")
        if st.button(T('login')):
            st.session_state.page = "Login"
            st.rerun()
    else:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        st.markdown(f"<h2>{T('contribute_header')}</h2>", unsafe_allow_html=True)
        with st.form("contribute_form", clear_on_submit=True):
            recipe_name = st.text_input(T("recipe_name"))
            region = st.text_input(T("region"))
            food_type = st.selectbox(T("food_type"), [T("breakfast"), T("lunch"), T("dinner"), T("snack"), T("sweet"), T("pickle"), T("other")])
            ingredients = st.text_area(T("ingredients"), height=150)
            steps = st.text_area(T("steps"), height=250)
            images = st.file_uploader(T("images"), accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
            videos = st.file_uploader(T("videos"), accept_multiple_files=True, type=['mp4', 'mov', 'avi', 'mkv'])
            audios = st.file_uploader(T("audios"), accept_multiple_files=True, type=['mp3', 'wav', 'ogg'])
            submit = st.form_submit_button(T("submit"))
        if submit:
            st.success(T("success_msg"))
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "About":
    st.markdown(f"<div class='main-container text-page'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('about_header')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p>{T('about_text')}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Contact":
    st.markdown(f"<div class='main-container text-page'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('contact_header')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='contact-box'>{T('contact_info')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Login":
    st.markdown("<div class='form-container auth-form'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('login_header')}</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input(T("username"))
        password = st.text_input(T("password"), type="password")
        submit = st.form_submit_button(T("login"))
    if submit:
        if check_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Explore"
            st.rerun()
        else:
            st.error(T("login_error"))
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Signup":
    st.markdown("<div class='form-container auth-form'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('signup_header')}</h2>", unsafe_allow_html=True)
    with st.form("signup_form"):
        username = st.text_input(T("username"))
        password = st.text_input(T("password"), type="password")
        submit = st.form_submit_button(T("signup"))
    if submit:
        if signup_user(username, password):
            st.success(T("signup_success"))
            st.session_state.page = "Login"
            st.rerun()
        else:
            st.error(T("username_exists"))
    st.markdown("</div>", unsafe_allow_html=True)
