import os
import random
import requests
import streamlit as st
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
CLIPS_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

st.set_page_config(page_title="YouTube Music Quiz", page_icon="🎵")
st.title("🎵 YouTube Music Quiz")

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
    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return url

def download_playlist_invidious(playlist_id):
    # Publiczne instancje Invidious
    instances = [
        "https://invidious.nerdvpn.de",
        "https://inv.tux.pizza",
        "https://invidious.drgns.space"
    ]
    
    songs = []
    for instance in instances:
        try:
            api_url = f"{instance}/api/v1/playlists/{playlist_id}"
            res = requests.get(api_url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                videos = data.get("videos", [])
                
                for vid in videos[:15]: # Limituemy do 15 piosenek dla szybszego ładowania
                    v_id = vid["videoId"]
                    title = vid["title"]
                    author = vid.get("author", "Unknown")
                    
                    # Pobieranie strumienia audio
                    audio_url = f"{instance}/latest_version?id={v_id}&itag=140"
                    audio_res = requests.get(audio_url, timeout=15)
                    
                    if audio_res.status_code == 200:
                        file_path = os.path.join(DOWNLOAD_DIR, f"{v_id}.m4a")
                        with open(file_path, "wb") as f:
                            f.write(audio_res.content)
                            
                        if " - " in title:
                            author, title = title.split(" - ", 1)
                            
                        songs.append({
                            "path": file_path,
                            "artist": author.strip(),
                            "title": title.strip()
                        })
                if songs:
                    break
        except Exception:
            continue
            
    return songs

def draw_next_song():
    if not st.session_state.songs:
        return
    song = random.choice(st.session_state.songs)
    st.session_state.current_song = song
    
    audio = AudioSegment.from_file(song["path"])
    song_len_sec = int(len(audio) / 1000)
    
    start_sec = random.randint(0, max(0, song_len_sec - clip_duration))
    clip = audio[start_sec * 1000 : (start_sec + clip_duration) * 1000]
    
    clip_path = os.path.join(CLIPS_DIR, "temp_clip.mp3")
    clip.export(clip_path, format="mp3")
    st.session_state.clip_path = clip_path

playlist_url = st.text_input("Wklej link do playlisty YouTube:")
if st.button("Pobierz playlistę i rozpocznij"):
    if playlist_url:
        p_id = extract_playlist_id(playlist_url)
        with st.spinner("Pobieranie playlisty przez proxy... To zajmie około minuty."):
            st.session_state.songs = download_playlist_invidious(p_id)
            st.session_state.score = 0
            st.session_state.total = 0
            if st.session_state.songs:
                draw_next_song()
                st.success(f"Pobrano {len(st.session_state.songs)} piosenek!")
            else:
                st.error("Nie udało się pobrać utwórów. Spróbuj ponownie za chwilę.")
    else:
        st.warning("Podaj link do playlisty.")

if st.session_state.current_song and st.session_state.clip_path:
    st.divider()
    st.subheader(f"Wynik: {st.session_state.score} / {st.session_state.total}")
    st.audio(st.session_state.clip_path, format="audio/mp3")
    
    with st.form(key="answer_form"):
        user_answer = st.text_input("Twoja odpowiedź:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            st.session_state.total += 1
            song = st.session_state.current_song
            correct = False
            
            if mode == "Tytuł" and user_answer.lower() in song["title"].lower():
                correct = True
            elif mode == "Wykonawca" and user_answer.lower() in song["artist"].lower():
                correct = True
            elif mode == "Wykonawca i Tytuł":
                if user_answer.lower() in f'{song["artist"]} {song["title"]}'.lower():
                    correct = True

            if correct:
                st.success("🎯 Poprawna odpowiedź!")
                st.score += 1
            else:
                st.error(f"❌ Błąd! Poprawna odpowiedź: {song['artist']} - {song['title']}")
    
    if st.button("Następne pytanie ➡️"):
        draw_next_song()
        st.rerun()
