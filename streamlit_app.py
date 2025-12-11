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

st.set_page_config(
    page_title="GitHub Profile Roaster",
    page_icon="🔥",
    layout="wide"
)

# Global CSS – tune these values to match your own site exactly
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #050816 0, #020617 55%);
    color: #e5e7eb;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
}
.main-block {
    max-width: 960px;
    margin: 0 auto;
    padding: 60px 16px 80px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 0.75rem;
    color: #a5b4fc;
    background: rgba(79, 70, 229, 0.18);
    border: 1px solid rgba(129, 140, 248, 0.35);
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    text-align: left;
    margin-top: 0.75rem;
    margin-bottom: 0.4rem;
}
.hero-subtitle {
    font-size: 0.98rem;
    color: #9ca3af;
    max-width: 520px;
    line-height: 1.5;
}
.hero-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 2.4rem;
    margin-top: 2.2rem;
}
.hero-left {
    flex: 1.1;
}
.hero-right {
    flex: 0.9;
}
.input-card {
    background: rgba(15, 23, 42, 0.9);
    border-radius: 1.25rem;
    padding: 1.2rem 1.4rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.7);
}
.input-row {
    display: flex;
    flex-direction: row;
    gap: 0.6rem;
    align-items: center;
}
.input-row input {
    border-radius: 999px !important;
}
.stButton > button {
    border-radius: 999px;
    font-weight: 600;
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 40%, #22c55e 100%) !important;
    color: #022c22 !important;
    border: none;
}
.stButton > button:hover {
    filter: brightness(1.02);
}
.result-card {
    margin-top: 2.5rem;
    background: rgba(15, 23, 42, 0.96);
    border-radius: 1.4rem;
    padding: 1.4rem 1.6rem 1.6rem;
    border: 1px solid rgba(148, 163, 184, 0.3);
    box-shadow: 0 24px 55px rgba(15, 23, 42, 0.8);
}
.metric-label {
    font-size: 0.75rem;
    color: #9ca3af;
}
.metric-value {
    font-size: 1.15rem;
    font-weight: 600;
    color: #e5e7eb;
}
.roast-box {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 40%, #22c55e 100%);
    padding: 16px 18px;
    border-radius: 16px;
    color: #052e16;
    font-size: 0.98rem;
    margin-top: 1rem;
    font-weight: 500;
}
.small-caption {
    font-size: 0.75rem;
    color: #9ca3af;
}
@media (max-width: 900px) {
    .hero-row {
        flex-direction: column;
        align-items: flex-start;
    }
    .hero-title {
        font-size: 2.1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# MAIN LAYOUT
st.markdown("<div class='main-block'>", unsafe_allow_html=True)

# Hero
st.markdown(
    "<div class='hero-badge'>🔥 GitHub roast · LLM‑powered</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 class='hero-title'>Year in GitHub, but roasted.</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='hero-subtitle'>Punch in any GitHub username and get a stats‑aware, AI‑generated roast of their profile. Followers, repos, languages – nothing is safe.</p>",
    unsafe_allow_html=True,
)

st.markdown("<div class='hero-row'>", unsafe_allow_html=True)

# Left side: copy, features etc (optional text, tweak as you like)
st.markdown("<div class='hero-left'>", unsafe_allow_html=True)
st.markdown(
    """
- No login, just a username.
- Roasts stay local – nothing stored.
- Built with GitHub REST API + Groq LLM.
""",
)
st.markdown("</div>", unsafe_allow_html=True)

# Right side: input card
st.markdown("<div class='hero-right'>", unsafe_allow_html=True)
st.markdown("<div class='input-card'>", unsafe_allow_html=True)

col_input, col_button = st.columns([3, 1])
with col_input:
    username = st.text_input(
        "GitHub username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed",
    )
with col_button:
    roast_btn = st.button("Roast my GitHub 🔥", use_container_width=True, type="primary")

st.markdown(
    "<p class='small-caption'>Tip: Try famous devs first, then your own profile.</p>",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)  # close input-card
st.markdown("</div>", unsafe_allow_html=True)  # close hero-right
st.markdown("</div>", unsafe_allow_html=True)  # close hero-row

# SESSION STATE
if "profile" not in st.session_state:
    st.session_state.profile = None
if "roast" not in st.session_state:
    st.session_state.roast = None
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = None

# HANDLE BUTTON CLICK
if roast_btn and username:
    if len(username) > 39:
        st.error("❌ Invalid GitHub username")
    else:
        cache_valid = (
            st.session_state.profile
            and st.session_state.profile["username"].lower() == username.lower()
            and st.session_state.last_fetch_time
            and datetime.now() - st.session_state.last_fetch_time < timedelta(seconds=CACHE_TTL_SECONDS)
        )

        # Fetch profile when cache is invalid
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

# RESULT CARD
if st.session_state.profile:
    profile = st.session_state.profile

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([1, 2])
    with top_col1:
        try:
            r = requests.get(profile["avatar_url"])
            img = Image.open(BytesIO(r.content))
            st.image(img, width=110)
        except Exception:
            st.write("@" + profile["username"])
    with top_col2:
        st.markdown(f"### {profile['name']}  `@{profile['username']}`")
        st.write(profile["bio"])
        st.markdown(
            f"<p class='small-caption'>📍 {profile['location']} · 🏢 {profile['company']}</p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    stats_labels = ["Repos", "Followers", "Following", "Years Active"]
    stats_values = [
        profile["public_repos"],
        f"{profile['followers']:,}",
        profile["following"],
        profile["years_on_github"],
    ]
    for col, lab, val in zip([s1, s2, s3, s4], stats_labels, stats_values):
        with col:
            st.markdown(
                f"<div class='metric-label'>{lab}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='metric-value'>{val}</div>",
                unsafe_allow_html=True,
            )

    # Languages
    if profile["top_languages"]:
        st.markdown("#### Top languages")
        lang_cols = st.columns(len(profile["top_languages"]))
        for i, (lang, count) in enumerate(profile["top_languages"]):
            with lang_cols[i]:
                st.metric(lang, count)

    # Repos
    if profile["top_repos"]:
        st.markdown("#### Highlighted repos")
        for repo in profile["top_repos"]:
            st.write(f"⭐ **{repo['name']}** · {repo['stars']}★ · {repo['language']}")

    # Roast
    if st.session_state.roast:
        st.markdown("#### Your roast")
        st.markdown(
            f"<div class='roast-box'>{st.session_state.roast}</div>",
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Another roast 🔁"):
                st.session_state.roast = generate_roast(profile)
                st.experimental_rerun()
        with b2:
            st.markdown(
                "<p class='small-caption'>Select the roast and press Cmd+C to copy.</p>",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)  # close result-card

st.markdown("</div>", unsafe_allow_html=True)  # close main-block
