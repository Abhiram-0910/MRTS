import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# ── Config ─────────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_BASE = f"{BACKEND_URL}/api"
TOKEN_URL = f"{BACKEND_URL}/token"

# ── i18n UI Strings ─────────────────────────────────────────────────────────────
UI_STRINGS = {
    "en": {
        "title": "🤖 Movie and TV Shows Recommending Engine AI",
        "subtitle": "Revolutionary AI-Powered Movie & TV Discovery Engine",
        "search_label": "What are you in the mood for?",
        "search_placeholder": "e.g., 'mind-bending sci-fi thriller' or 'कोई अच्छी हिंदी कॉमेडी'",
        "search_btn": "🚀 Search",
        "try_these": "💡 Try these searches:",
        "trending_header": "🔥 Trending Now",
        "watchlist_tab": "🔖 My Watchlist",
        "search_tab": "🔍 Search",
        "watchlist_empty": "Your watchlist is empty. Add movies from search results!",
        "love_it": "🔥 Love it",
        "pass_btn": "👎 Pass",
        "add_wl": "📋 Watchlist",
        "mark_watched": "✅ Mark Watched",
        "login_header": "🔐 Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "logged_in_as": "Logged in as",
        "ui_lang": "UI Language",
        "no_results": "🤔 No matches found. Try adjusting your search!",
        "connecting": "🤖 Movie and TV Shows Recommending Engine AI is analysing your preferences...",
        "stats_header": "📊 Your Stats",
        "user_profile": "👤 User Profile",
        "user_id_label": "User ID",
        "adv_filters": "🎛️ Advanced Filters",
        "ai_settings": "🤖 AI Settings",
        "quick_actions": "⚡ Quick Actions",
        "surprise_btn": "🎲 Surprise Me!",
        "my_stats_btn": "📊 My Stats",
    },
    "hi": {
        "title": "🤖 मिराई AI",
        "subtitle": "क्रांतिकारी AI-संचालित मूवी और TV खोज इंजन",
        "search_label": "आज आप क्या देखना चाहते हैं?",
        "search_placeholder": "उदा. 'एक अच्छी हिंदी कॉमेडी' या 'mind-bending sci-fi'",
        "search_btn": "🚀 खोजें",
        "try_these": "💡 इन्हें आज़माएं:",
        "trending_header": "🔥 अभी ट्रेंडिंग",
        "watchlist_tab": "🔖 वॉचलिस्ट",
        "search_tab": "🔍 खोज",
        "watchlist_empty": "आपकी वॉचलिस्ट खाली है। खोज परिणामों से फ़िल्में जोड़ें!",
        "love_it": "🔥 पसंद है",
        "pass_btn": "👎 छोड़ें",
        "add_wl": "📋 वॉचलिस्ट",
        "mark_watched": "✅ देखा",
        "login_header": "🔐 लॉगिन",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_btn": "लॉगिन",
        "logout_btn": "लॉगआउट",
        "logged_in_as": "लॉगिन:",
        "ui_lang": "UI भाषा",
        "no_results": "🤔 कोई परिणाम नहीं। खोज बदलें!",
        "connecting": "🤖 Movie and TV Shows Recommending Engine AI आपकी पसंद विश्लेषण कर रहा है...",
        "stats_header": "📊 आपके आँकड़े",
        "user_profile": "👤 उपयोगकर्ता प्रोफ़ाइल",
        "user_id_label": "उपयोगकर्ता ID",
        "adv_filters": "🎛️ उन्नत फ़िल्टर",
        "ai_settings": "🤖 AI सेटिंग्स",
        "quick_actions": "⚡ त्वरित क्रियाएँ",
        "surprise_btn": "🎲 कुछ नया!",
        "my_stats_btn": "📊 मेरे आँकड़े",
    },
    "te": {
        "title": "🤖 Movie and TV Shows Recommending Engine AI",
        "subtitle": "విప్లవాత్మక AI-ఆధారిత చలనచిత్రం & TV డిస్కవరీ ఇంజిన్",
        "search_label": "మీరు ఈరోజు ఏమి చూడాలనుకుంటున్నారు?",
        "search_placeholder": "ఉదా. 'తెలుగు లో మంచి యాక్షన్ సినిమా' లేదా 'sci-fi thriller'",
        "search_btn": "🚀 వెతకండి",
        "try_these": "💡 వీటిని ప్రయత్నించండి:",
        "trending_header": "🔥 ఇప్పుడు ట్రెండింగ్",
        "watchlist_tab": "🔖 వాచ్‌లిస్ట్",
        "search_tab": "🔍 శోధన",
        "watchlist_empty": "మీ వాచ్‌లిస్ట్ ఖాళీగా ఉంది. శోధన ఫలితాల నుండి చలనచిత్రాలను జోడించండి!",
        "love_it": "🔥 నచ్చింది",
        "pass_btn": "👎 వద్దు",
        "add_wl": "📋 వాచ్‌లిస్ట్",
        "mark_watched": "✅ చూశాను",
        "login_header": "🔐 లాగిన్",
        "username": "వినియోగదారు పేరు",
        "password": "పాస్‌వర్డ్",
        "login_btn": "లాగిన్",
        "logout_btn": "లాగ్‌అవుట్",
        "logged_in_as": "లాగిన్:",
        "ui_lang": "UI భాష",
        "no_results": "🤔 ఫలితాలు లేవు. శోధనను మార్చండి!",
        "connecting": "🤖 Movie and TV Shows Recommending Engine AI మీ ప్రాధాన్యతలను విశ్లేషిస్తోంది...",
        "stats_header": "📊 మీ గణాంకాలు",
        "user_profile": "👤 వినియోగదారు ప్రొఫైల్",
        "user_id_label": "వినియోగదారు ID",
        "adv_filters": "🎛️ అడ్వాన్స్‌డ్ ఫిల్టర్లు",
        "ai_settings": "🤖 AI సెట్టింగ్‌లు",
        "quick_actions": "⚡ త్వరిత చర్యలు",
        "surprise_btn": "🎲 సర్ప్రైజ్!",
        "my_stats_btn": "📊 నా గణాంకాలు",
    },
}

LANG_OPTIONS = {"English": "en", "हिंदी": "hi", "తెలుగు": "te"}


# ── Helper: authenticated request headers ──────────────────────────────────────

def _auth_headers() -> dict:
    token = st.session_state.get("jwt_token", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _try_login(username: str, password: str) -> bool:
    """Obtain a JWT token from /token endpoint. Returns True on success."""
    try:
        resp = requests.post(
            TOKEN_URL,
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["jwt_token"] = data["access_token"]
            st.session_state["jwt_username"] = username
            return True
        else:
            return False
    except Exception:
        return False


# ── Main App ───────────────────────────────────────────────────────────────────

def run():
    st.set_page_config(
        page_title="Movie and TV Shows Recommending Engine AI — Movie & TV Discovery",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _apply_styles()

    # ── Sidebar ──────────────────────────────────────────────────────────────

    # Language selector (first — affects all labels below it)
    st.sidebar.markdown("---")
    lang_display = st.sidebar.selectbox(
        "🌐 UI Language / UI भाषा / UI భాష",
        list(LANG_OPTIONS.keys()),
        index=0,
    )
    lang = LANG_OPTIONS[lang_display]
    S = UI_STRINGS[lang]

    # Login / Logout block
    st.sidebar.markdown(f"### {S['login_header']}")
    if st.session_state.get("jwt_token"):
        st.sidebar.success(f"{S['logged_in_as']}: **{st.session_state.get('jwt_username', 'user')}**")
        if st.sidebar.button(S["logout_btn"], key="logout_btn"):
            st.session_state.pop("jwt_token", None)
            st.session_state.pop("jwt_username", None)
            st.rerun()
    else:
        uname = st.sidebar.text_input(S["username"], value="admin", key="login_uname")
        pwd = st.sidebar.text_input(S["password"], type="password", value="mirai2024", key="login_pwd")
        if st.sidebar.button(S["login_btn"], key="login_btn"):
            if _try_login(uname, pwd):
                st.sidebar.success(f"✅ {S['logged_in_as']}: {uname}")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid credentials")

    st.sidebar.markdown("---")

    # User profile
    st.sidebar.markdown(f"### {S['user_profile']}")
    user_id = st.sidebar.text_input(S["user_id_label"], value=st.session_state.get("user_id", "demo_user"), key="user_id_input")
    st.session_state["user_id"] = user_id

    languages = ["Auto-detect", "English", "हिंदी (Hindi)", "తెలుగు (Telugu)", "தமிழ் (Tamil)", "Español", "Français", "中文"]
    lang_pref = st.sidebar.selectbox("Preferred Language", languages)

    st.sidebar.markdown("---")

    # Filters
    st.sidebar.markdown(f"### {S['adv_filters']}")
    media_type = st.sidebar.selectbox("Media Type", ["All", "Movies", "TV Shows"])
    min_rating = st.sidebar.slider("Min Rating", 0.0, 10.0, 6.0, 0.5)
    year_range = st.sidebar.slider("Year Range", 1970, 2025, (1990, 2025))
    max_runtime = st.sidebar.slider("Max Runtime (min)", 30, 300, 180, 10)

    all_genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
                  "Family", "Fantasy", "Horror", "Mystery", "Romance", "Science Fiction", "Thriller"]
    selected_genres = st.sidebar.multiselect("Genres", all_genres, default=[])

    platforms = ["Netflix", "Prime Video", "Disney+", "HBO Max", "Hulu", "Apple TV+", "Hotstar", "Zee5"]
    selected_platforms = st.sidebar.multiselect("Available on", platforms, default=[])

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {S['ai_settings']}")
    explanation_style = st.sidebar.selectbox("Explanation Style", ["Detailed Analysis", "Quick Summary", "Technical", "Casual"])
    diversity_level = st.sidebar.slider("Diversity Level", 0.0, 1.0, 0.7, 0.1)
    include_trending = st.sidebar.checkbox("Include Trending", value=True)

    filters = {
        "media_type": media_type,
        "min_rating": min_rating,
        "year_range": list(year_range),
        "max_runtime": max_runtime,
        "genre": selected_genres[0] if len(selected_genres) == 1 else None,
        "platforms": selected_platforms,
        "explanation_style": explanation_style,
        "diversity_level": diversity_level,
        "include_trending": include_trending,
        "language_pref": lang_pref,
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {S['quick_actions']}")
    if st.sidebar.button(S["surprise_btn"], use_container_width=True, key="surprise_btn"):
        import random
        queries = ["A hidden gem most people haven't heard of", "Something completely unexpected", "A movie that broke all the rules"]
        st.session_state["surprise_query"] = random.choice(queries)

    if st.sidebar.button(S["my_stats_btn"], use_container_width=True, key="mystats_btn"):
        st.session_state["show_stats"] = True

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f'<h1 class="mirai-header">{S["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="mirai-subtitle">{S["subtitle"]}</p>', unsafe_allow_html=True)
    _render_stats_bar()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    search_tab, watchlist_tab = st.tabs([S["search_tab"], S["watchlist_tab"]])

    # ── SEARCH TAB ───────────────────────────────────────────────────────────
    with search_tab:
        st.markdown(f"### {S['search_label']}")
        qcol1, qcol2 = st.columns([5, 1])
        with qcol1:
            query = st.text_input(
                "query",
                label_visibility="collapsed",
                placeholder=S["search_placeholder"],
                key="main_query",
            )
        with qcol2:
            search_clicked = st.button(S["search_btn"], type="primary", use_container_width=True, key="search_btn_main")

        # Sample queries
        st.markdown(f"#### {S['try_these']}")
        sample_queries = [
            "Mind-bending movies that make you think",
            "Feel-good comedies for a rainy day",
            "Intense crime thrillers with plot twists",
            "Beautiful animated films for adults",
            "कोई रोमांचक हिंदी फिल्म",
            "తెలుగులో మంచి కామెడీ సినిమాలు",
            "Visually stunning sci-fi epics",
            "Inspiring true stories",
        ]
        cols = st.columns(4)
        for i, sq in enumerate(sample_queries[:8]):
            with cols[i % 4]:
                if st.button(f"🎬 {sq[:22]}…", key=f"sq_{i}", help=sq):
                    st.session_state["surprise_query"] = sq

        # Handle search
        effective_query = st.session_state.pop("surprise_query", None) if "surprise_query" in st.session_state else None
        if search_clicked and query.strip():
            effective_query = query.strip()

        if effective_query:
            if not st.session_state.get("jwt_token"):
                st.warning("⚠️ Please log in (sidebar) to get recommendations.")
            else:
                _render_recommendations(effective_query, filters, user_id, lang, S)
        else:
            # Show Trending Now when idle
            _render_trending_section(S, lang, user_id)

    # ── WATCHLIST TAB ─────────────────────────────────────────────────────────
    with watchlist_tab:
        _render_watchlist(S, user_id)

    # ── Stats overlay ─────────────────────────────────────────────────────────
    if st.session_state.pop("show_stats", False):
        _show_user_stats(user_id, S)


# ── Rendering Functions ────────────────────────────────────────────────────────

def _render_stats_bar():
    """Top stats strip."""
    try:
        r = requests.get(f"{API_BASE}/stats", timeout=3)
        stats = r.json() if r.status_code == 200 else {}
    except Exception:
        stats = {}
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item"><div class="stat-number">{stats.get('total_titles', '10K+')}</div><div class="stat-label">Movies & Shows</div></div>
        <div class="stat-item"><div class="stat-number">{stats.get('languages', '15+')}</div><div class="stat-label">Languages</div></div>
        <div class="stat-item"><div class="stat-number">{stats.get('platforms', '50+')}</div><div class="stat-label">Platforms</div></div>
        <div class="stat-item"><div class="stat-number">∞</div><div class="stat-label">AI Explanations</div></div>
    </div>
    """, unsafe_allow_html=True)


def _render_recommendations(query: str, filters: dict, user_id: str, lang: str, S: dict):
    with st.spinner(S["connecting"]):
        try:
            payload = {"query": query, "user_id": user_id, **filters}
            r = requests.post(f"{API_BASE}/recommend", json=payload, headers=_auth_headers(), timeout=60)
            if r.status_code == 401:
                st.error("🔐 Session expired or invalid. Please log in again.")
                return
            if r.status_code == 429:
                st.warning("⏳ Rate limit reached (10/min). Please wait a moment.")
                return
            if r.status_code != 200:
                st.error(f"❌ API error {r.status_code}: {r.text[:200]}")
                return
            data = r.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach backend. Is it running?")
            st.info("💡 Run: `start_mirai.bat` to launch the backend.")
            return

    st.markdown("### 🤖 Movie and TV Shows Recommending Engine AI Analysis")
    if data.get("translated_query"):
        st.info(f"🌐 **Translated:** *{data['translated_query']}*")
    if data.get("explanation"):
        st.markdown(f'<div class="ai-explanation">{data["explanation"]}</div>', unsafe_allow_html=True)
    if data.get("total_candidates"):
        st.caption(f"📊 Analysed {data['total_candidates']} titles")
    st.divider()

    st.markdown("### 🎬 Your Personalised Recommendations")
    movies = data.get("movies", [])
    if not movies:
        st.warning(S["no_results"])
        return

    cols = st.columns(3)
    for idx, movie in enumerate(movies):
        with cols[idx % 3]:
            _render_movie_card(movie, idx, user_id, S)


def _render_movie_card(movie: dict, index: int, user_id: str, S: dict):
    title = movie.get("title", "Unknown")
    year = str(movie.get("release_date", ""))[:4]
    rating = movie.get("rating", 0)
    match_score = movie.get("match_score", 0)
    overview = movie.get("overview", "")
    poster = movie.get("poster_path") or "https://via.placeholder.com/500x750/1e293b/94a3b8?text=No+Poster"
    providers = movie.get("streaming_platforms") or movie.get("providers", [])
    media_type = movie.get("media_type", "movie")
    tmdb_id = movie.get("id", 0)

    badge_platforms = "".join([f'<span class="platform-badge">{p}</span>' for p in providers[:3]])
    extra = f'<span style="color:#94a3b8;font-size:0.8rem">+{len(providers)-3} more</span>' if len(providers) > 3 else ""

    st.markdown(f"""
    <div class="movie-card-enhanced">
        <div style="display:flex;gap:1rem;">
            <div style="flex-shrink:0;"><img src="{poster}" style="width:110px;height:165px;object-fit:cover;border-radius:8px;" alt="{title}"></div>
            <div style="flex-grow:1;">
                <h4 style="margin:0 0 0.5rem 0;color:#f8fafc;">{title} {f'({year})' if year else ''}</h4>
                <div style="display:flex;gap:0.5rem;margin-bottom:0.5rem;flex-wrap:wrap;">
                    <span class="match-badge">🎯 {match_score}% Match</span>
                    <span class="rating-badge">⭐ {rating:.1f}</span>
                    <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:0.25rem 0.5rem;border-radius:20px;font-size:0.8rem;">{media_type.title()}</span>
                </div>
                <p style="font-size:0.9rem;color:#cbd5e1;margin:0.5rem 0;line-height:1.4;">{overview[:180]}{'...' if len(overview)>180 else ''}</p>
                {badge_platforms}{extra}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        if st.button(S["love_it"], key=f"like_{index}_{tmdb_id}", use_container_width=True):
            _record_interaction(user_id, tmdb_id, "like")
            st.toast(f"❤️ Liked '{title}'!", icon="🔥")
    with bcol2:
        if st.button(S["pass_btn"], key=f"dislike_{index}_{tmdb_id}", use_container_width=True):
            _record_interaction(user_id, tmdb_id, "dislike")
            st.toast(f"👎 Got it, fewer like '{title}'", icon="👎")
    with bcol3:
        if st.button(S["add_wl"], key=f"watchlist_{index}_{tmdb_id}", use_container_width=True):
            _add_to_watchlist(user_id, tmdb_id)
            st.toast(f"📋 Added '{title}' to watchlist!", icon="📋")


def _render_trending_section(S: dict, lang: str, user_id: str):
    st.markdown(f"### {S['trending_header']}")
    try:
        r = requests.get(f"{API_BASE}/trending", timeout=5)
        if r.status_code != 200:
            st.info("🔥 Trending content will appear here once the backend has data.")
            return
        data = r.json()
        trending = data.get("trending", [])
    except Exception:
        st.info("🔥 Trending content will appear here!")
        return

    if not trending:
        st.info("🔥 No trending data yet. The backend will populate this on startup.")
        return

    cols = st.columns(min(len(trending[:6]), 6))
    for idx, item in enumerate(trending[:6]):
        with cols[idx]:
            title = item.get("title", "Unknown")
            poster = item.get("poster_path") or "https://via.placeholder.com/300x450/1e293b/94a3b8?text=No+Poster"
            rating = item.get("rating", 0)
            st.markdown(f"""
            <div class="trending-card" style="text-align:center;">
                <img src="{poster}" style="width:100%;border-radius:8px;max-height:180px;object-fit:cover;" alt="{title}">
                <div style="font-weight:600;font-size:0.85rem;color:#f8fafc;margin-top:0.4rem;">{title[:22]}{'…' if len(title)>22 else ''}</div>
                <div style="font-size:0.75rem;color:#94a3b8">⭐ {rating:.1f}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_watchlist(S: dict, user_id: str):
    st.markdown(f"### {S['watchlist_tab']}")
    if not st.session_state.get("jwt_token"):
        st.warning("⚠️ Please log in to view your watchlist.")
        return

    try:
        r = requests.get(f"{API_BASE}/watchlist/{user_id}", headers=_auth_headers(), timeout=5)
        if r.status_code == 401:
            st.error("🔐 Session expired. Please log in again.")
            return
        if r.status_code != 200:
            st.info(S["watchlist_empty"])
            return
        data = r.json()
        items = data.get("watchlist", [])
    except Exception:
        st.info(S["watchlist_empty"])
        return

    if not items:
        st.info(S["watchlist_empty"])
        return

    st.caption(f"📋 {data.get('count', len(items))} titles in your watchlist")

    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            title = item.get("title", "Unknown")
            poster = item.get("poster_path") or "https://via.placeholder.com/300x450/1e293b/94a3b8?text=No+Poster"
            rating = item.get("rating", 0)
            watched = item.get("watched", False)
            tmdb_id = item.get("id", 0)
            genres_list = item.get("genres", [])
            genres_str = ", ".join(genres_list[:3]) if genres_list else ""

            watched_badge = '✅ <span style="color:#10b981">Watched</span>' if watched else '🕐 Unwatched'
            st.markdown(f"""
            <div class="movie-card-enhanced">
                <img src="{poster}" style="width:100%;height:160px;object-fit:cover;border-radius:8px;margin-bottom:0.5rem;" alt="{title}">
                <div style="font-weight:600;color:#f8fafc;">{title}</div>
                <div style="font-size:0.75rem;color:#94a3b8;margin:0.2rem 0;">⭐ {rating:.1f} &nbsp;|&nbsp; {genres_str}</div>
                <div style="font-size:0.8rem;">{watched_badge}</div>
            </div>
            """, unsafe_allow_html=True)

            if not watched:
                if st.button(S["mark_watched"], key=f"watched_{idx}_{tmdb_id}", use_container_width=True):
                    _mark_watched(user_id, tmdb_id)
                    st.rerun()
            if st.button(f"🗑️ Remove", key=f"rm_{idx}_{tmdb_id}", use_container_width=True):
                _remove_from_watchlist(user_id, tmdb_id)
                st.rerun()


def _show_user_stats(user_id: str, S: dict):
    st.markdown(f"### {S['stats_header']}")
    try:
        r = requests.get(f"{API_BASE}/user_stats/{user_id}", headers=_auth_headers(), timeout=5)
        if r.status_code == 200:
            stats = r.json()
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("👍 Liked", stats.get("movies_liked", 0))
            mc2.metric("👎 Disliked", stats.get("movies_disliked", 0))
            mc3.metric("📋 Watchlist", stats.get("watchlist_size", 0))
            if stats.get("genre_preferences"):
                st.markdown("#### 🎭 Genre Preferences")
                df = pd.DataFrame(list(stats["genre_preferences"].items()), columns=["Genre", "Count"])
                st.bar_chart(df.set_index("Genre"))
        else:
            st.info("Start using Movie and TV Shows Recommending Engine to see your personalised stats!")
    except Exception:
        st.info("Stats will appear here once you start using the app!")


# ── API Action Helpers ─────────────────────────────────────────────────────────

def _record_interaction(user_id: str, tmdb_id: int, interaction_type: str):
    try:
        requests.post(
            f"{API_BASE}/interact",
            json={"user_id": user_id, "tmdb_id": tmdb_id, "interaction_type": interaction_type},
            headers=_auth_headers(),
            timeout=5,
        )
    except Exception:
        pass


def _add_to_watchlist(user_id: str, tmdb_id: int):
    try:
        requests.post(
            f"{API_BASE}/watchlist",
            json={"user_id": user_id, "tmdb_id": tmdb_id, "action": "add"},
            headers=_auth_headers(),
            timeout=5,
        )
    except Exception:
        pass


def _remove_from_watchlist(user_id: str, tmdb_id: int):
    try:
        requests.post(
            f"{API_BASE}/watchlist",
            json={"user_id": user_id, "tmdb_id": tmdb_id, "action": "remove"},
            headers=_auth_headers(),
            timeout=5,
        )
    except Exception:
        pass


def _mark_watched(user_id: str, tmdb_id: int):
    try:
        requests.patch(
            f"{API_BASE}/watchlist/{user_id}/{tmdb_id}/watched",
            headers=_auth_headers(),
            timeout=5,
        )
    except Exception:
        pass


# ── Styles ─────────────────────────────────────────────────────────────────────

def _apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, .stApp { font-family: 'Inter', sans-serif; }
    .stApp {
        background-color: #0f172a;
        background-image: radial-gradient(at 0% 0%, rgba(99,102,241,0.15) 0px, transparent 50%),
                          radial-gradient(at 100% 0%, rgba(139,92,246,0.15) 0px, transparent 50%);
        color: #f8fafc;
    }
    .mirai-header {
        background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3.2rem !important; font-weight: 800 !important;
        text-align: center; margin-bottom: 0.5rem; padding-bottom: 12px;
    }
    .mirai-subtitle {
        text-align: center; color: #cbd5e1; font-size: 1.15rem;
        margin-bottom: 1.5rem; font-weight: 300; letter-spacing: 0.5px;
    }
    .movie-card-enhanced {
        background: rgba(30,41,59,0.85); border-radius: 12px; padding: 1rem;
        margin: 0.5rem 0; border: 1px solid rgba(129,140,248,0.15);
        transition: all 0.3s ease;
    }
    .movie-card-enhanced:hover {
        transform: translateY(-3px); box-shadow: 0 10px 24px rgba(0,0,0,0.35);
        border-color: rgba(129,140,248,0.4);
    }
    .platform-badge {
        display:inline-block; background:linear-gradient(135deg,#10b981,#059669);
        color:white; padding:0.2rem 0.45rem; border-radius:20px; font-size:0.75rem;
        font-weight:600; margin:0.1rem;
    }
    .rating-badge {
        background:linear-gradient(135deg,#f59e0b,#d97706); color:white;
        padding:0.2rem 0.45rem; border-radius:20px; font-size:0.75rem; font-weight:600;
    }
    .match-badge {
        background:linear-gradient(135deg,#8b5cf6,#7c3aed); color:white;
        padding:0.2rem 0.45rem; border-radius:20px; font-size:0.75rem; font-weight:600;
    }
    .trending-card {
        background:linear-gradient(135deg,rgba(239,68,68,0.1),rgba(220,38,38,0.2));
        border:1px solid rgba(239,68,68,0.3); border-radius:10px;
        padding:0.65rem; margin:0.2rem 0; transition: all 0.2s ease;
    }
    .trending-card:hover { transform: scale(1.02); }
    .ai-explanation {
        background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.2));
        border-left:4px solid #6366f1; border-radius:0 12px 12px 0;
        padding:1.25rem 1.5rem; margin:1rem 0; font-size:1.05rem; line-height:1.65;
        color:#e2e8f0;
    }
    .stats-container {
        display:flex; justify-content:space-around;
        background:rgba(30,41,59,0.8); border-radius:12px;
        padding:1rem; margin:1rem 0;
    }
    .stat-item { text-align:center; }
    .stat-number { font-size:1.5rem; font-weight:700; color:#6366f1; }
    .stat-label { font-size:0.85rem; color:#94a3b8; }
    .stButton>button {
        background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color:white !important; border:none !important; border-radius:10px !important;
        font-weight:600 !important; transition:all 0.25s ease !important;
        box-shadow:0 4px 12px rgba(99,102,241,0.3) !important;
    }
    .stButton>button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 20px rgba(99,102,241,0.4) !important; }
    </style>
    """, unsafe_allow_html=True)


# ── Entry point ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run()