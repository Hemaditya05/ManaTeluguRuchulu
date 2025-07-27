import streamlit as st
from pymongo import MongoClient
import gridfs
import datetime
from bson.objectid import ObjectId
from passlib.hash import pbkdf2_sha256
import base64

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
    "te": {
        "title": "సాంప్రదాయ తెలుగు వంటల డేటా ప్లాట్‌ఫారమ్",
        "subtitle": "ప్రామాణికమైన తెలుగు ఆహార వారసత్వం కోసం ఒక సజీవ భాండాగారం.",
        "nav_home": "హోమ్",
        "nav_explore": "అన్వేషించండి",
        "nav_contribute": "సమర్పించండి",
        "nav_about": "గురించి",
        "nav_contact": "సంప్రదించండి",
        "login": "లాగిన్",
        "signup": "సైన్ అప్",
        "logout": "లాగ్అవుట్",
        "welcome": "స్వాగతం",
        "explore_header": "మా వంటల వారసత్వాన్ని అన్వేషించండి",
        "explore_intro": "మా సంఘం పంచుకున్న వంటకాలు మరియు ఆహార జ్ఞాపకాలను బ్రౌజ్ చేయండి.",
        "contribute_header": "వంటకం లేదా ఆహార జ్ఞాపకాన్ని సమర్పించండి",
        "recipe_name": "వంటకం పేరు",
        "region": "ప్రాంతం (ఉదా., తెలంగాణ, ఆంధ్రప్రదేశ్, జిల్లా, గ్రామం)",
        "food_type": "ఆహార రకం",
        "breakfast": "అల్పాహారం",
        "lunch": "మధ్యాహ్న భోజనం",
        "dinner": "రాత్రి భోజనం",
        "snack": "చిరుతిండి",
        "sweet": "తీపి",
        "pickle": "పచ్చడి",
        "other": "ఇతర",
        "ingredients": "కావాల్సిన పదార్థాలు (ఒక పంక్తికి ఒకటి)",
        "steps": "తయారీ విధానం",
        "images": "చిత్రాలను అప్‌లోడ్ చేయండి",
        "videos": "వీడియోలను అప్‌లోడ్ చేయండి",
        "audios": "ఆడియోను అప్‌లోడ్ చేయండి (ఇంటర్వ్యూలు, సూచనలు)",
        "contributor_name": "మీ పేరు (ఐచ్ఛికం)",
        "contributor_email": "మీ ఇమెయిల్ (ఐచ్ఛికం)",
        "bio": "సంక్షిప్త పరిచయం / సందర్భం (ఐచ్ఛికం)",
        "submit": "సమర్పించు",
        "success_msg": "మీ సమర్పణ సేవ్ చేయబడింది! సహకరించినందుకు ధన్యవాదాలు. 🙏",
        "about_header": "ప్రాజెక్ట్ గురించి",
        "about_text": "ఈ ప్లాట్‌ఫారమ్ తెలుగు మాట్లాడే ప్రాంతాల యొక్క గొప్ప ఆహార వారసత్వాన్ని సేకరించి, భద్రపరచడానికి రూపొందించబడింది. వంటకాలు, చిత్రాలు మరియు కథలను అందించడానికి వినియోగదారులను అనుమతించడం ద్వారా, మా పాక వారసత్వాన్ని భవిష్యత్ తరాలకు సజీవంగా ఉంచే డిజిటల్ ఆర్కైవ్‌ను సృష్టించాలని మేము లక్ష్యంగా పెట్టుకున్నాము. మాతో చేరండి!",
        "contact_header": "మమ్మల్ని సంప్రదించండి",
        "contact_info": "ఇమెయిల్: support@switchr.org | హైదరాబాద్, తెలంగాణ",
        "login_header": "మీ ఖాతాలోకి లాగిన్ అవ్వండి",
        "signup_header": "కొత్త ఖాతాను సృష్టించండి",
        "username": "యూజర్‌నేమ్",
        "password": "పాస్వర్డ్",
        "username_exists": "ఈ యూజర్‌నేమ్ ఇప్పటికే ఉంది. దయచేసి మరొకదాన్ని ఎంచుకోండి.",
        "signup_success": "ఖాతా విజయవంతంగా సృష్టించబడింది! దయచేసి లాగిన్ చేయండి.",
        "login_error": "తప్పు యూజర్‌నేమ్ లేదా పాస్వర్డ్.",
    }
}

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

def T(key):
    return translations[st.session_state.lang].get(key, key)

# --- MongoDB Setup ---
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["telugu_cuisine_db"]
submissions_collection = db["submissions"]
users_collection = db["users"]
fs = gridfs.GridFS(db)

# --- Inject custom CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Authentication Functions ---
def signup_user(username, password):
    if users_collection.find_one({"username": username}):
        return False
    hashed_password = pbkdf2_sha256.hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

def check_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and pbkdf2_sha256.verify(password, user["password"]):
        return True
    return False

# --- Data Functions ---
def save_submission(data, images, videos, audios):
    file_ids = {"images": [], "videos": [], "audios": []}
    for img in images:
        fid = fs.put(img.read(), filename=img.name, content_type=img.type)
        file_ids["images"].append(fid)
    for vid in videos:
        fid = fs.put(vid.read(), filename=vid.name, content_type=vid.type)
        file_ids["videos"].append(fid)
    for aud in audios:
        fid = fs.put(aud.read(), filename=aud.name, content_type=aud.type)
        file_ids["audios"].append(fid)
    data["file_ids"] = file_ids
    data["created_at"] = datetime.datetime.utcnow()
    data["submitted_by"] = st.session_state.username
    submissions_collection.insert_one(data)

def get_all_submissions():
    return list(submissions_collection.find().sort("created_at", -1))

def get_image(file_id):
    try:
        gridout = fs.get(file_id)
        base64_img = base64.b64encode(gridout.read()).decode('utf-8')
        return f"data:{gridout.content_type};base64,{base64_img}"
    except Exception:
        return None

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
    
    if st.button(T('nav_explore'), key="home_explore_btn", type="primary"):
        st.session_state.page = "Explore"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Explore":
    st.markdown(f"<div class='main-container'>", unsafe_allow_html=True)
    st.markdown(f"<h2>{T('explore_header')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p>{T('explore_intro')}</p>", unsafe_allow_html=True)

    submissions = get_all_submissions()
    if not submissions:
        st.info("No recipes have been submitted yet. Be the first to contribute!")
    else:
        for sub in submissions:
            with st.container():
                st.markdown("<div class='recipe-card'>", unsafe_allow_html=True)
                cols = st.columns([1, 2])
                with cols[0]:
                    # Image
                    if sub.get("file_ids", {}).get("images"):
                        img_data = get_image(sub["file_ids"]["images"][0])
                        if img_data:
                            st.image(img_data, use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300", use_column_width=True)
                    # Videos
                    if sub.get("file_ids", {}).get("videos"):
                        for vid_fid in sub["file_ids"]["videos"]:
                            video_bytes = fs.get(vid_fid).read()
                            st.video(video_bytes)
                    # Audios
                    if sub.get("file_ids", {}).get("audios"):
                        for aud_fid in sub["file_ids"]["audios"]:
                            audio_bytes = fs.get(aud_fid).read()
                            st.audio(audio_bytes)
                with cols[1]:
                    st.markdown(f"<h3>{sub.get('recipe_name', 'No Title')}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**{T('region')}:** {sub.get('region', 'N/A')}", unsafe_allow_html=True)
                    st.markdown(f"**{T('food_type')}:** {sub.get('food_type', 'N/A')}", unsafe_allow_html=True)
                    with st.expander(f"View Details"):
                        st.markdown(f"**{T('ingredients')}:**\n<pre>{sub.get('ingredients', '')}</pre>", unsafe_allow_html=True)
                        st.markdown(f"**{T('steps')}:**\n<pre>{sub.get('steps', '')}</pre>", unsafe_allow_html=True)
                        if sub.get('submitted_by'):
                             st.markdown(f"<p class='submitted-by'>Submitted by: {sub.get('submitted_by')}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
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
            submit = st.form_submit_button(T("submit"), type="primary")
        if submit:
            data = {
                "recipe_name": recipe_name, "region": region, "food_type": food_type,
                "ingredients": ingredients, "steps": steps
            }
            save_submission(data, images or [], videos or [], audios or [])
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
        submit = st.form_submit_button(T("login"), type="primary")
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
        submit = st.form_submit_button(T("signup"), type="primary")
    if submit:
        if signup_user(username, password):
            st.success(T("signup_success"))
            st.session_state.page = "Login"
            st.rerun()
        else:
            st.error(T("username_exists"))
    st.markdown("</div>", unsafe_allow_html=True)
