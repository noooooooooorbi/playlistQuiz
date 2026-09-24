import os
import json
import random
import requests
import streamlit as st

st.set_page_config(page_title="QuizNuta", page_icon="🎵", layout="centered")

# Katalog na pliki tymczasowe
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# CSS: Nowoczesny interfejs QuizNuta z dopasowanym nagłówkiem
st.markdown("""
    <style>
    /* Ukrywamy domyślne paski i sidebar Streamlita */
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Główny kontener aplikacji */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px !important;
    }

    /* Nagłówek aplikacji */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
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
    }
    .app-title-wrapper {
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    .app-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        line-height: 1;
    }
    .app-subtitle {
        font-size: 0.78rem;
        color: #a0a5b5;
        font-weight: normal;
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

    /* Kafelki ze statystykami */
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

    /* Sekcja audio */
    audio {
        width: 100% !important;
        height: 45px !important;
        border-radius: 12px;
        margin-top: 4px;
    }

    /* Baner z podpowiedzią/wynikiem */
    .feedback-box {
        background-color: #121622;
        border: 1px solid #1e2436;
        border-radius: 14px;
        padding: 12px 14px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 12px;
    }
    .feedback-box.correct {
        border-color: #2dc653;
        background-color: rgba(45, 198, 83, 0.08);
    }
    .feedback-box.wrong {
        border-color: #ff3366;
        background-color: rgba(255, 51, 102, 0.08);
    }
    .feedback-icon {
        font-size: 18px;
        margin-top: 1px;
    }
    .feedback-text {
        font-size: 0.85rem;
        color: #a0a5b5;
    }
    .feedback-title {
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }

    /* Stylizacja przycisku głównego */
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
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(255, 0, 122, 0.5) !important;
    }

    /* Dopasowanie pól wyboru */
    div[data-baseweb="select"] {
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicjalizacja stanu aplikacji
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

def prepare_options(songs, selected_mode):
    options = set()
    for s in songs:
        if selected_mode == "Tytuł":
            options.add(s["title"])
        elif selected_mode == "Wykonawca":
            options.add(s["artist"])
        elif selected_mode == "Wykonawca i Tytuł":
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

# Nagłówek aplikacji (QuizNuta by Norbbs)
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

# Sekcja opcji: Playlista i Tryb gry w 2 kolumnach obok siebie
col1, col2 = st.columns(2)

predefined = load_predefined_playlists()
playlist_id_to_load = None

with col1:
    if predefined:
        options_map = {p["name"]: str(p["id"]) for p in predefined if "name" in p and "id" in p}
        options_map["-- Wklej własny link / ID --"] = "custom"
        
        selected_name = st.selectbox("🎛️ Playlista:", options=list(options_map.keys()))
        
        if options_map[selected_name] != "custom":
            playlist_id_to_load = options_map[selected_name]

with col2:
    mode = st.selectbox(
        "🎯 Tryb gry:", 
        options=["Wykonawca", "Tytuł", "Wykonawca i Tytuł"], 
        index=0
    )

if not playlist_id_to_load:
    custom_input = st.text_input("Wklej link do playlisty Deezer:", placeholder="https://www.deezer.com/pl/playlist/908622995")
    if custom_input:
        playlist_id_to_load = extract_playlist_id(custom_input)

# Przycisk startowy (jeśli gra nie trwa)
if not st.session_state.current_song and st.session_state.total == 0:
    if st.button("Pobierz playlistę i rozpocznij grę"):
        if playlist_id_to_load:
            with st.spinner("Ładowanie piosenek..."):
                fetched_songs = fetch_deezer_playlist(playlist_id_to_load)
                if fetched_songs:
                    st.session_state.songs_pool = fetched_songs.copy()
                    st.session_state.options_list = prepare_options(fetched_songs, mode)
                    st.session_state.score = 0
                    st.session_state.total = 0
                    st.session_state.audio_id = 0
                    draw_next_song()
                    st.rerun()
                else:
                    st.error("Błąd podczas pobierania playlisty.")
        else:
            st.warning("Wybierz playlistę z listy.")

# Panel Gry
if st.session_state.current_song:
    song = st.session_state.current_song
    remaining_count = len(st.session_state.songs_pool) + 1
    accuracy = int((st.session_state.score / st.session_state.total * 100)) if st.session_state.total > 0 else 0

    # Kafelki statystyk (Wynik i Pozostało)
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

    # Odtwarzacz audio
    st.audio(song["preview_url"])

    # Odpowiedź
    default_option = "-- Wybierz odpowiedź --"
    selectable_options = [default_option] + st.session_state.options_list
    
    user_choice = st.selectbox(
        "Wybierz odpowiedź z listy:", 
        options=selectable_options, 
        key=f"q_select_{st.session_state.audio_id}"
    )

    # Przycisk "Sprawdź" lub "Następne pytanie"
    if not st.session_state.answered:
        if st.button("Sprawdź odpowiedź 🎯"):
            if user_choice != default_option:
                st.session_state.total += 1
                st.session_state.answered = True
                
                correct = False
                if mode == "Tytuł" and user_choice == song["title"]:
                    correct = True
                elif mode == "Wykonawca" and user_choice == song["artist"]:
                    correct = True
                elif mode == "Wykonawca i Tytuł" and user_choice == f'{song["artist"]} - {song["title"]}':
                    correct = True

                if correct:
                    st.session_state.score += 1
                    st.session_state.last_correct = True
                    st.balloons()
                else:
                    st.session_state.last_correct = False
                st.rerun()
            else:
                st.warning("Proszę wybrać odpowiedź z listy!")
    else:
        # Pokaż wynik / odpowiedź
        box_class = "correct" if st.session_state.last_correct else "wrong"
        icon = "🎯" if st.session_state.last_correct else "💡"
        title = "Poprawna odpowiedź!" if st.session_state.last_correct else "Poprawna odpowiedź to:"

        st.markdown(f"""
            <div class="feedback-box {box_class}">
                <div class="feedback-icon">{icon}</div>
                <div>
                    <div class="feedback-title">{title}</div>
                    <div class="feedback-text"><strong>{song['artist']} - {song['title']}</strong></div>
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
