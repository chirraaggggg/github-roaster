import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
import logging

from api import get_complete_profile, GitHubAPIError
from roast import generate_roast, RoastGenerationError
from config import CACHE_TTL_SECONDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(
    page_title="GitHub Profile Roaster",
    page_icon="🔥",
    layout="wide"
)

# Simple CSS for roast box
st.markdown("""
<style>
.roast-box {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    font-size: 18px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔥 GitHub Profile Roaster")
st.markdown("*Get your GitHub profile roasted in a fun, light-hearted way!*")
st.markdown("---")

with st.sidebar:
    st.subheader("About")
    st.write("Uses the GitHub API to fetch profile data and Groq LLM to generate witty roasts.")
    st.subheader("How it works")
    st.markdown("1. Enter a GitHub username\n2. We fetch their public profile\n3. AI cooks a roast")
    st.subheader("Tips")
    st.markdown("- Try: `torvalds`, `gvanrossum`, `dhh`\n- Use your own username too")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Input")
    username = st.text_input("GitHub Username", placeholder="e.g., torvalds")
    search_button = st.button("🔥 Generate Roast!", type="primary")

# Session state for caching
if "profile" not in st.session_state:
    st.session_state.profile = None
if "roast" not in st.session_state:
    st.session_state.roast = None
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = None

with col2:
    st.subheader("Result")
    if search_button and username:
        if len(username) > 39:
            st.error("❌ Invalid GitHub username")
        else:
            cache_valid = (
                st.session_state.profile
                and st.session_state.profile["username"].lower() == username.lower()
                and st.session_state.last_fetch_time
                and datetime.now() - st.session_state.last_fetch_time < timedelta(seconds=CACHE_TTL_SECONDS)
            )

            # Fetch profile if not cached
            if not cache_valid:
                with st.spinner("🔍 Fetching GitHub profile..."):
                    try:
                        st.session_state.profile = get_complete_profile(username)
                        st.session_state.last_fetch_time = datetime.now()
                    except GitHubAPIError as e:
                        st.error(f"❌ {e}")
                        st.session_state.profile = None
                        st.stop()

            # Generate roast
            if st.session_state.profile:
                with st.spinner("🎤 Cooking up the roast..."):
                    try:
                        st.session_state.roast = generate_roast(st.session_state.profile)
                    except RoastGenerationError as e:
                        st.error(f"❌ {e}")
                        st.session_state.roast = None

# Display profile and roast if available
if st.session_state.profile:
    profile = st.session_state.profile

    st.markdown("---")
    st.subheader(f"📊 Profile: {profile['name']} (@{profile['username']})")

    colA, colB = st.columns([1, 3])
    with colA:
        try:
            r = requests.get(profile["avatar_url"])
            img = Image.open(BytesIO(r.content))
            st.image(img, width=150)
        except Exception:
            st.write("@" + profile["username"])
    with colB:
        st.write(f"**Bio:** {profile['bio']}")
        st.write(f"**Location:** {profile['location']}")
        st.write(f"**Company:** {profile['company']}")
        st.write(f"**Website:** {profile['blog']}")

    st.markdown("### 📈 Stats")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Repos", profile["public_repos"])
    with c2:
        st.metric("Followers", f"{profile['followers']:,}")
    with c3:
        st.metric("Following", profile["following"])
    with c4:
        st.metric("Years Active", profile["years_on_github"])

    if profile["top_repos"]:
        st.markdown("### 🌟 Top Repos")
        for repo in profile["top_repos"]:
            st.write(f"⭐ **{repo['name']}** ({repo['stars']} stars)")

    if profile["top_languages"]:
        st.markdown("### 💻 Languages")
        cols = st.columns(len(profile["top_languages"]))
        for i, (lang, count) in enumerate(profile["top_languages"]):
            with cols[i]:
                st.metric(lang, count)

    if st.session_state.roast:
        st.markdown("---")
        st.markdown("### 🔥 Your Roast")
        st.markdown(
            f"""
        <div class="roast-box">
        {st.session_state.roast}
        </div>
        """,
            unsafe_allow_html=True,
        )

        c1, _, c3 = st.columns(3)
        with c1:
            if st.button("🔄 Different Roast"):
                st.session_state.roast = generate_roast(profile)
                st.experimental_rerun()
        with c3:
            if st.button("📋 Copy"):
                st.success("✅ Copied! (select the text and press Cmd+C)")

st.markdown("---")
st.markdown("Made with 🔥 | Powered by GitHub API + Groq LLM")
