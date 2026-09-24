import os
import json
import random
import requests
import streamlit as st

st.set_page_config(page_title="QuizNuta", page_icon="🎵", layout="centered")

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# CSS – czysty interfejs bez niepotrzebnych marginesów
st.markdown("""
    <style>
    header[data-testid="stHeader"], footer, [data-testid="sidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 12px !important;
        width: 100% !important;
    }

    [data-testid="column"] {
        flex: 1 1 50% !important;
        width: 50% !important;
        min-width: 0 !important;
    }

    @media (max-width: 600px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 10px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    div[data-testid="stWidgetLabel"] p {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    div[data-baseweb="select"] {
        border-radius: 12px !important;
        width: 100% !important;
        min-width: 0 !important;
    }

    div[data-baseweb="select"] > div {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
        padding-top: 0px;
        margin-top: -25px;
    }
    .app-title-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-logo {
        background: linear-gradient(135deg, #ff007a, #7b2cbf);
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 12px rgba(255, 0, 122, 0.4);
        margin-top: 15px;
    }
    .app-title-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }
    .app-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        line-height: 1;
    }
    .app-subtitle {
        font-size: 0.72rem;
        color: #a0a5b5;
        font-weight: normal;
        margin-top: -20px;
        line-height: 1;
    }
    .badge-live {
        background-color: rgba(45, 198, 83, 0.15);
        color: #2dc653;
        border: 1px solid rgba(45, 198, 83, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .badge-live::before {
        content: '';
        width: 6px;
        height: 6px;
        background-color: #2dc653;
        border-radius: 50%;
    }

    .stats-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 12px;
    }
    .stat-card {
        background-color: #121622;
        border: 1px solid #1e2436;
        border-radius: 14px;
        padding: 10px 12px;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stat-label {
        font-size: 0.68rem;
        color: #7b839b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 4px;
    }
    .stat-value span {
        font-size: 0.8rem;
        color: #7b839b;
        font-weight: normal;
    }
    .stat-icon {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 30px;
        height: 30px;
        background-color: #1a2030;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }

    audio {
        width: 100% !important;
        height: 45px !important;
        border-radius: 12px;
        margin-top: 4px;
    }

    .feedback-box {
        background-color: #121622;
        border: 1px solid #1e2436;
        border-radius: 14px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 12px;
    }
    .feedback-box.correct { border-color: #2dc653; background-color: rgba(45, 198, 83, 0.08); }
    .feedback-box.wrong { border-color: #ff3366; background-color: rgba(255, 51, 102, 0.08); }
    .feedback-icon { font-size: 22px; }
    .feedback-main { font-size: 1rem; font-weight: 700; color: #ffffff; line-height: 1.2; }
    .feedback-sub { font-size: 0.82rem; color: #a0a5b5; margin-top: 2px; }

    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff007a, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255, 0, 122, 0.3) !important;
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
if "current_playlist_id" not in st.session_state:
    st.session_state.current_playlist_id = None
if "missing_tracks" not in st.session_state:
    st.session_state.missing_tracks = []
if "trigger_focus_reset" not in st.session_state:
    st.session_state.trigger_focus_reset = 0

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

@st.cache_data(ttl=60)
def fetch_deezer_playlist_v3(playlist_ids_str):
    all_songs = []
    missing_songs = []
    
    ids = [p_id.strip() for p_id in str(playlist_ids_str).split(",") if p_id.strip()]
    
    for playlist_id in ids:
        url = f"https://api.deezer.com/playlist/{playlist_id}/tracks?limit=100"
        
        while url:
            try:
                res = requests.get(url, timeout=10)
                if res.status_code != 200:
                    break
                data = res.json()
                if "error" in data or "data" not in data:
                    break
                
                for track in data["data"]:
                    preview = track.get("preview")
                    title = track.get("title", "Unknown")
                    artist = track.get("artist", {}).get("name", "Unknown")
                    
                    if preview and isinstance(preview, str) and preview.startswith("http"):
                        all_songs.append({
                            "title": title,
                            "artist": artist,
                            "preview_url": preview
                        })
                    else:
                        missing_songs.append(f"{artist} - {title}")
                
                url = data.get("next")
            except Exception:
                break
                
    return all_songs, missing_songs

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
    st.session_state.trigger_focus_reset += 1

def start_new_game(playlist_id, mode):
    with st.spinner("Pobieranie pełnej playlisty..."):
        fetched_songs, missing = fetch_deezer_playlist_v3(playlist_id)
        if fetched_songs:
            st.session_state.current_playlist_id = playlist_id
            st.session_state.full_playlist = fetched_songs.copy()
            st.session_state.songs_pool = fetched_songs.copy()
            st.session_state.options_list = prepare_options(fetched_songs, mode)
            st.session_state.missing_tracks = missing
            st.session_state.score = 0
            st.session_state.total = 0
            st.session_state.audio_id = 0
            draw_next_song()
            return True
        else:
            st.error("Błąd pobierania playlisty. Sprawdź czy jest publiczna.")
            return False

def on_select_change():
    st.session_state.trigger_focus_reset += 1

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

mode_options = [
    "👤 Wykonawca",
    "🎵 Tytuł",
    "🔀 Obie opcje"
]

predefined = load_predefined_playlists()
playlist_id_to_load = None

col1, col2 = st.columns(2)

with col1:
    if predefined:
        options_map = {p["name"]: str(p["id"]) for p in predefined if "name" in p and "id" in p}
        options_map["-- Inny link --"] = "custom"
        selected_name = st.selectbox("🎛️ Playlista:", options=list(options_map.keys()))
        if options_map[selected_name] != "custom":
            playlist_id_to_load = options_map[selected_name]

with col2:
    selected_mode_full = st.selectbox("🎯 Tryb gry:", options=mode_options, index=0)

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

# Wykrywanie zmiany playlisty na nową
if playlist_id_to_load and playlist_id_to_load != st.session_state.current_playlist_id:
    if start_new_game(playlist_id_to_load, clean_mode):
        st.rerun()

if st.session_state.full_playlist:
    st.session_state.options_list = prepare_options(st.session_state.full_playlist, clean_mode)

if not st.session_state.current_song and st.session_state.total == 0:
    if st.button("Pobierz playlistę i rozpocznij grę"):
        if playlist_id_to_load:
            if start_new_game(playlist_id_to_load, clean_mode):
                st.rerun()
        else:
            st.warning("Wybierz playlistę.")

if st.session_state.current_song:
    song = st.session_state.current_song
    remaining_count = len(st.session_state.songs_pool) + 1
    accuracy = int((st.session_state.score / st.session_state.total * 100)) if st.session_state.total > 0 else 0

    st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div>
                    <div class="stat-label">TWÓJ WYNIK</div>
                    <div class="stat-value">{st.session_state.score} / {st.session_state.total} <span>({accuracy}%)</span></div>
                </div>
                <div class="stat-icon">🏆</div>
            </div>
            <div class="stat-card">
                <div>
                    <div class="stat-label">POZOSTAŁO</div>
                    <div class="stat-value">{remaining_count} <span>piosenek</span></div>
                </div>
                <div class="stat-icon">🎵</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if song.get("preview_url"):
        st.audio(song["preview_url"])
    else:
        st.warning("Brak pliku audio dla tej piosenki.")

    default_option = "Nie mam pojęcia :-)"
    selectable_options = [default_option] + st.session_state.options_list
    
    user_choice = st.selectbox(
        "Wybierz odpowiedź z listy:", 
        options=selectable_options, 
        key=f"q_select_{st.session_state.audio_id}",
        on_change=on_select_change
    )

    # Ulepszony JS – wymusza zdejmujący blur i skupienie na audio z ciągłym próbkowaniem
    st.components.v1.html(f"""
        <script>
            function shiftFocusToAudio() {{
                var parentDoc = window.parent.document;
                var active = parentDoc.activeElement;
                if (active) {{
                    active.blur();
                }}
                var audioElem = parentDoc.querySelector('audio');
                if (audioElem) {{
                    audioElem.focus();
                }}
            }}
            
            // Wykonaj od razu oraz po krótkiej chwili, gdy Streamlit zakończy renderowanie
            shiftFocusToAudio();
            setTimeout(shiftFocusToAudio, 150);
            setTimeout(shiftFocusToAudio, 350);
        </script>
    """, height=0, key=f"focus_script_{st.session_state.trigger_focus_reset}")

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
            main_text = song['artist']
            sub_html = f'<div class="feedback-sub">{song["title"]}</div>'
        elif clean_mode == "Tytuł":
            main_text = song['title']
            sub_html = f'<div class="feedback-sub">{song["artist"]}</div>'
        else:
            main_text = song['artist']
            sub_html = f'<div class="feedback-main">{song["title"]}</div>'

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
        st.session_state.current_song = None
        st.session_state.current_playlist_id = None
        st.rerun()

# --- BLOK DIAGNOSTYCZNY ---
if st.session_state.missing_tracks:
    with st.expander(f"⚠️ Zobacz pominięte utwory bez próbki audio ({len(st.session_state.missing_tracks)})"):
        for item in st.session_state.missing_tracks:
            st.write(f"❌ {item}")
