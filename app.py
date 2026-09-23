import os
import random
import requests
import streamlit as st

DOWNLOAD_DIR = "downloads"
CLIPS_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

st.set_page_config(page_title="Deezer Music Quiz", page_icon="🎵")
st.title("🎵 Deezer Music Quiz")

st.sidebar.header("⚙️ Ustawienia Quizu")
mode = st.sidebar.radio("Co chcesz odgadywać?", ["Tytuł", "Wykonawca", "Wykonawca i Tytuł"])
clip_duration = st.sidebar.slider("Długość fragmentu (sekundy):", min_value=3, max_value=30, value=10)

if "songs" not in st.session_state:
    st.session_state.songs = []
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "clip_path" not in st.session_state:
    st.session_state.clip_path = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0

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

def draw_next_song():
    if not st.session_state.songs:
        return
    
    song = random.choice(st.session_state.songs)
    st.session_state.current_song = song
    
    res = requests.get(song["preview_url"])
    if res.status_code == 200:
        clip_path = os.path.join(CLIPS_DIR, "temp_clip.mp3")
        with open(clip_path, "wb") as f:
            f.write(res.content)
        st.session_state.clip_path = clip_path

playlist_input = st.text_input("Wklej link do playlisty Deezer (lub jej ID):", placeholder="https://www.deezer.com/pl/playlist/908622995")

if st.button("Pobierz playlistę i rozpocznij"):
    if playlist_input:
        playlist_id = extract_playlist_id(playlist_input)
        with st.spinner("Pobieranie playlisty z Deezer..."):
            st.session_state.songs = fetch_deezer_playlist(playlist_id)
            st.session_state.score = 0
            st.session_state.total = 0
            if st.session_state.songs:
                draw_next_song()
                st.success(f"Pobrano {len(st.session_state.songs)} piosenek!")
            else:
                st.error("Nie udało się pobrać playlisty. Upewnij się, że link/ID jest poprawny i playlista jest publiczna.")
    else:
        st.warning("Podaj link do playlisty Deezer.")

if st.session_state.current_song and st.session_state.clip_path:
    st.divider()
    st.subheader(f"Wynik: {st.session_state.score} / {st.session_state.total}")
    
    st.audio(st.session_state.clip_path, format="audio/mp3")
    
    with st.form(key="answer_form"):
        user_answer = st.text_input("Twoja odpowiedź:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            clean_answer = user_answer.strip()
            if not clean_answer:
                st.warning("⚠️ Wpisz odpowiedź przed kliknięciem 'Sprawdź'!")
            else:
                st.session_state.total += 1
                song = st.session_state.current_song
                correct = False
                
                if mode == "Tytuł" and clean_answer.lower() in song["title"].lower():
                    correct = True
                elif mode == "Wykonawca" and clean_answer.lower() in song["artist"].lower():
                    correct = True
                elif mode == "Wykonawca i Tytuł":
                    if clean_answer.lower() in f'{song["artist"]} {song["title"]}'.lower():
                        correct = True

                if correct:
                    st.success("🎯 Poprawna odpowiedź!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Błąd! Poprawna odpowiedź: {song['artist']} - {song['title']}")
    
    if st.button("Następne pytanie ➡️"):
        draw_next_song()
        st.rerun()
