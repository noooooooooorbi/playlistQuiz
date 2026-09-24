import os
import json
import random
import requests
import streamlit as st

st.set_page_config(page_title="QuizNuta", page_icon="🎵", layout="centered")

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# CSS: Twardy reset szerokości i brak wychodzenia poza ekran mobilny
st.markdown("""
    <style>
    /* Reset tła i ukrycie domyślnych nagłówków Streamlit */
    header[data-testid="stHeader"], footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Blokada rozpychania całej strony na boki */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* Główny kontener aplikacji */
    .block-container {
        padding: 1rem 0.5rem !important;
        max-width: 450px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    /* Nagłówek QuizNuta */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .app-title-container {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .app-logo {
        background: linear-gradient(135deg, #ff007a, #7b2cbf);
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(255, 0, 122, 0.4);
    }
    .app-title-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .app-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        line-height: 1;
    }
    .app-subtitle {
        font-size: 0.7rem;
        color: #a0a5b5;
        margin-top: 2px;
    }
    .badge-live {
        background-color: rgba(45, 198, 83, 0.15);
        color: #2dc653;
        border: 1px solid rgba(45, 198, 83, 0.4);
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .badge-live::before {
        content: '';
        width: 6px;
        height: 6px;
        background-color: #2dc653;
        border-radius: 50%;
    }

    /* SZTYWNY UKŁAD 2 KOLUMN DLA SELEKTORÓW (GRID) */
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        min-width: 0 !important;
    }

    /* Stylizacja etykiet i samych selectboxów */
    div[data-testid="stWidgetLabel"] p {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    div[data-baseweb="select"] {
        border-radius: 10px !important;
        min-width: 0 !important;
    }

    div[data-baseweb="select"] > div {
        padding-left: 6px !important;
        padding-right: 6px !important;
        font-size: 0.85rem !important;
    }

    /* Kafelki ze statystykami */
    .stats-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 12px;
    }
    .stat-card {
        background-color: #121622;
        border: 1px solid #1e2436;
        border-radius: 12px;
        padding: 8px 10px;
        position: relative;
    }
    .stat-label {
        font-size: 0.65rem;
        color: #7b839b;
        font-weight: 700;
        text-transform: uppercase;
    }
    .stat-value {
        font-size: 1.1rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 2px;
    }
    .stat-value span {
        font-size: 0.75rem;
        color: #7b839b;
        font-weight: normal;
    }
    .stat-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        font-size: 12px;
    }

    audio {
        width: 100% !important;
        height: 40px !important;
        margin-top: 4px;
    }

    .feedback-box {
        background-color: #121622;
        border: 1px solid #1e2436;
        border-radius: 12px;
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 10px 0;
    }
    .feedback-box.correct { border-color: #2dc653; background-color: rgba(45, 198, 83, 0.08); }
    .feedback-box.wrong { border-color: #ff3366; background-color: rgba(255, 51, 102, 0.08); }
    .feedback-icon { font-size: 20px; }
    .feedback-main { font-size: 0.95rem; font-weight: 700; color: #ffffff; }
    .feedback-sub { font-size: 0.8rem; color: #a0a5b5; }

    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff007a, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicjalizacja stanu
if "full_playlist" not in st.session_state:
    st.session_state.full_playlist = []
if "songs_pool" not in st.session_state:
    st.session_state.songs_pool = []
if "options_list" not in st.session_state:
    st.session_state.options_list = []
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "last_correct" not in st.session_state:
    st.session_state.last_correct = False
if "audio_id" not in st.session_state:
    st.session_state.audio_id = 0

def load_predefined_playlists():
    if os.path.exists("playlists.json"):
        try:
            with open("playlists.json", "r", encoding="utf-8") as f:
                content = f.read().replace('\xa0', ' ')
                data = json.loads(content)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []

def extract_playlist_id(url):
    clean_url = url.split("?")[0]
    parts = clean_url.strip("/").split("/")
    for part in reversed(parts):
        if part.isdigit():
            return part
    return url

def fetch_deezer_playlist(playlist_id):
    api_url = f"https://api.deezer.com/playlist/{playlist_id}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        if "error" in data:
            return []

        tracks = data.get("tracks", {}).get("data", [])
        songs = []

        for track in tracks:
            preview_url = track.get("preview")
            if preview_url and isinstance(preview_url, str) and preview_url.startswith("http"):
                songs.append({
                    "title": track.get("title", "Unknown"),
                    "artist": track.get("artist", {}).get("name", "Unknown"),
                    "preview_url": preview_url
                })
        return songs
    except Exception:
        return []

def prepare_options(songs, raw_mode):
    options = set()
    for s in songs:
        if "Tytuł" in raw_mode and "Wykonawca" not in raw_mode:
            options.add(s["title"])
        elif "Wykonawca" in raw_mode and "Tytuł" not in raw_mode:
            options.add(s["artist"])
        else:
            options.add(f'{s["artist"]} - {s["title"]}')
    return sorted(list(options))

def draw_next_song():
    if not st.session_state.songs_pool:
        st.session_state.current_song = None
        return
    song = random.choice(st.session_state.songs_pool)
    st.session_state.songs_pool.remove(song)
    st.session_state.current_song = song
    st.session_state.answered = False
    st.session_state.last_correct = False
    st.session_state.audio_id += 1

# Nagłówek
st.markdown("""
    <div class="app-header">
        <div class="app-title-container">
            <div class="app-logo">🎵</div>
            <div class="app-title-wrapper">
                <h1 class="app-title">QuizNuta</h1>
                <span class="app-subtitle">by Norbbs</span>
            </div>
        </div>
        <div class="badge-live">Live</div>
    </div>
""", unsafe_allow_html=True)

# Opcje trybów
mode_options = [
    "👤 Wykonawca",
    "🎵 Tytuł",
    "🔀 Obie opcje"
]

predefined = load_predefined_playlists()
playlist_id_to_load = None

# Blok wyboru - CSS Grid wymusza układ 50%/50% w jednym wierszu
col1, col2 = st.columns(2)

with col1:
    if predefined:
        options_map = {p["name"]: str(p["id"]) for p in predefined if "name" in p and "id" in p}
        options_map["-- Własna --"] = "custom"
        selected_name = st.selectbox("🎛️ Playlista", options=list(options_map.keys()))
        if options_map[selected_name] != "custom":
            playlist_id_to_load = options_map[selected_name]

with col2:
    selected_mode_full = st.selectbox("🎯 Tryb", options=mode_options, index=0)

# Odczyt trybu
if "Obie opcje" in selected_mode_full:
    clean_mode = "Wykonawca i Tytuł"
elif "Tytuł" in selected_mode_full:
    clean_mode = "Tytuł"
else:
    clean_mode = "Wykonawca"

if not playlist_id_to_load:
    custom_input = st.text_input("Link Deezer:", placeholder="https://www.deezer.com/pl/playlist/908622995")
    if custom_input:
        playlist_id_to_load = extract_playlist_id(custom_input)

if st.session_state.full_playlist:
    st.session_state.options_list = prepare_options(st.session_state.full_playlist, clean_mode)

# Przycisk startu
if not st.session_state.current_song and st.session_state.total == 0:
    if st.button("Pobierz i rozpocznij"):
        if playlist_id_to_load:
            with st.spinner("Pobieranie..."):
                fetched_songs = fetch_deezer_playlist(playlist_id_to_load)
                if fetched_songs:
                    st.session_state.full_playlist = fetched_songs.copy()
                    st.session_state.songs_pool = fetched_songs.copy()
                    st.session_state.options_list = prepare_options(fetched_songs, clean_mode)
                    st.session_state.score = 0
                    st.session_state.total = 0
                    st.session_state.audio_id = 0
                    draw_next_song()
                    st.rerun()
                else:
                    st.error("Błąd pobierania.")
        else:
            st.warning("Wybierz playlistę.")

# Gra
if st.session_state.current_song:
    song = st.session_state.current_song
    remaining_count = len(st.session_state.songs_pool) + 1
    accuracy = int((st.session_state.score / st.session_state.total * 100)) if st.session_state.total > 0 else 0

    st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-label">WYNIK</div>
                <div class="stat-value">{st.session_state.score} / {st.session_state.total} <span>({accuracy}%)</span></div>
                <div class="stat-icon">🏆</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">POZOSTAŁO</div>
                <div class="stat-value">{remaining_count} <span>utworów</span></div>
                <div class="stat-icon">🎵</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.audio(song["preview_url"])

    default_option = "Nie mam pojęcia :-)"
    selectable_options = [default_option] + st.session_state.options_list
    
    user_choice = st.selectbox(
        "Wybierz odpowiedź:", 
        options=selectable_options, 
        key=f"q_select_{st.session_state.audio_id}"
    )

    if not st.session_state.answered:
        if st.button("Sprawdź odpowiedź 🎯"):
            st.session_state.total += 1
            st.session_state.answered = True
            
            correct = False
            if user_choice != default_option:
                if clean_mode == "Tytuł" and user_choice == song["title"]:
                    correct = True
                elif clean_mode == "Wykonawca" and user_choice == song["artist"]:
                    correct = True
                elif clean_mode == "Wykonawca i Tytuł" and user_choice == f'{song["artist"]} - {song["title"]}':
                    correct = True

            st.session_state.last_correct = correct
            if correct:
                st.session_state.score += 1
                st.balloons()
            st.rerun()
    else:
        box_class = "correct" if st.session_state.last_correct else "wrong"
        icon = "🎯" if st.session_state.last_correct else "❌"

        if clean_mode == "Wykonawca":
            main_text, sub_text = song['artist'], song['title']
        elif clean_mode == "Tytuł":
            main_text, sub_text = song['title'], song['artist']
        else:
            main_text, sub_text = f"{song['artist']} - {song['title']}", ""

        sub_html = f'<div class="feedback-sub">{sub_text}</div>' if sub_text else ''

        st.markdown(f"""
            <div class="feedback-box {box_class}">
                <div class="feedback-icon">{icon}</div>
                <div>
                    <div class="feedback-main">{main_text}</div>
                    {sub_html}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Następne pytanie ➔"):
            draw_next_song()
            st.rerun()

elif st.session_state.total > 0 and not st.session_state.songs_pool:
    st.balloons()
    st.markdown("""
        <div class="feedback-box correct" style="text-align: center; display: block;">
            <h2>🎉 Koniec Quizu!</h2>
        </div>
    """, unsafe_allow_html=True)
    st.subheader(f"Ostateczny wynik: {st.session_state.score} / {st.session_state.total}")
    if st.button("Zagraj ponownie"):
        st.session_state.total = 0
        st.rerun()
