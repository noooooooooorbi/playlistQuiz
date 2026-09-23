import os
import random
import requests
import streamlit as st

DOWNLOAD_DIR = "downloads"
CLIPS_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

st.set_page_config(page_title="Deezer Music Quiz", page_icon="🎵")

# Własny CSS: Powiększenie odtwarzacza audio oraz stylizacja banera punktacji
st.markdown("""
    <style>
    /* Powiększenie kontrolek odtwarzacza audio */
    audio {
        width: 100% !important;
        height: 70px !important;
        transform: scale(1.02);
    }
    
    /* Dynamiczny baner z wynikiem */
    .score-box {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 20px;
        transition: all 0.5s ease;
    }
    .score-normal {
        background-color: #1e2129;
        color: #ffffff;
        border: 1px solid #3e4451;
    }
    .score-success {
        background-color: #1b4332;
        color: #2dc653;
        border: 2px solid #2dc653;
        box-shadow: 0 0 15px rgba(45, 198, 83, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 Deezer Music Quiz")

st.sidebar.header("⚙️ Ustawienia Quizu")
mode = st.sidebar.radio("Co chcesz odgadywać?", ["Tytuł", "Wykonawca", "Wykonawca i Tytuł"])

# Stan aplikacji
if "songs_pool" not in st.session_state:
    st.session_state.songs_pool = []
if "options_list" not in st.session_state:
    st.session_state.options_list = []
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "clip_path" not in st.session_state:
    st.session_state.clip_path = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "last_correct" not in st.session_state:
    st.session_state.last_correct = False

def extract_playlist_id(url):
    clean_url = url.split("?")[0]
    parts = clean_url.strip("/").split("/")
    for part in reversed(parts):
        if part.isdigit():
            return part
    return url

def fetch_deezer_playlist(playlist_id):
    api_url = f"https://api.deezer.com/playlist/{playlist_id}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        return []

    data = response.json()
    if "error" in data:
        return []

    tracks = data.get("tracks", {}).get("data", [])
    songs = []

    for track in tracks:
        preview_url = track.get("preview")
        if preview_url:
            songs.append({
                "title": track.get("title", "Unknown"),
                "artist": track.get("artist", {}).get("name", "Unknown"),
                "preview_url": preview_url
            })

    return songs

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
        st.session_state.clip_path = None
        return
    
    song = random.choice(st.session_state.songs_pool)
    st.session_state.songs_pool.remove(song)
    st.session_state.current_song = song
    st.session_state.answered = False
    st.session_state.last_correct = False
    
    res = requests.get(song["preview_url"])
    if res.status_code == 200:
        clip_path = os.path.join(CLIPS_DIR, "temp_clip.mp3")
        with open(clip_path, "wb") as f:
            f.write(res.content)
        st.session_state.clip_path = clip_path

playlist_input = st.text_input("Wklej link do playlisty Deezer (lub jej ID):", placeholder="https://www.deezer.com/pl/playlist/908622995")

if st.button("Pobierz playlistę i rozpocznij grę"):
    if playlist_input:
        playlist_id = extract_playlist_id(playlist_input)
        with st.spinner("Pobieranie playlisty z Deezer..."):
            fetched_songs = fetch_deezer_playlist(playlist_id)
            if fetched_songs:
                st.session_state.songs_pool = fetched_songs.copy()
                st.session_state.options_list = prepare_options(fetched_songs, mode)
                st.session_state.score = 0
                st.session_state.total = 0
                draw_next_song()
                st.success(f"Załadowano {len(fetched_songs)} piosenek!")
            else:
                st.error("Nie udało się pobrać playlisty. Upewnij się, że link/ID jest poprawny.")
    else:
        st.warning("Podaj link do playlisty Deezer.")

# Panel rozgrywki
if st.session_state.current_song and st.session_state.clip_path:
    st.divider()
    
    # Efekt wizualny zmiana koloru tła w zależności od poprawnej odpowiedzi
    score_class = "score-success" if st.session_state.last_correct else "score-normal"
    st.markdown(f"""
        <div class="score-box {score_class}">
            Wynik: {st.session_state.score} / {st.session_state.total} &nbsp;|&nbsp; Pozostało piosenek: {len(st.session_state.songs_pool) + 1}
        </div>
    """, unsafe_allow_html=True)
    
    # Powiększony odtwarzacz audio
    st.audio(st.session_state.clip_path, format="audio/mp3")
    
    # Opcja domyślna z listą rozwijaną
    default_option = "Nie mam pojęcia! :-)"
    selectable_options = [default_option] + st.session_state.options_list
    
    user_choice = st.selectbox(
        "Wybierz odpowiedź z listy:", 
        options=selectable_options, 
        key=f"q_{st.session_state.total}"
    )

    if not st.session_state.answered:
        if st.button("Sprawdź"):
            st.session_state.total += 1
            st.session_state.answered = True
            song = st.session_state.current_song
            
            if user_choice == default_option:
                st.session_state.last_correct = False
                st.info(f"💡 Poprawna odpowiedź to: **{song['artist']} - {song['title']}**")
            else:
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
                    st.success("🎯 Poprawna odpowiedź! Punkty doliczone!")
                    st.rerun()
                else:
                    st.session_state.last_correct = False
                    st.error(f"❌ Błąd! Poprawna odpowiedź to: **{song['artist']} - {song['title']}**")

    if st.session_state.answered:
        if st.button("Następne pytanie ➡️"):
            draw_next_song()
            st.rerun()

elif st.session_state.total > 0 and not st.session_state.songs_pool:
    st.divider()
    st.balloons()
    st.header("🎉 Koniec Quizu!")
    st.subheader(f"Twój ostateczny wynik to: {st.session_state.score} / {st.session_state.total}")
