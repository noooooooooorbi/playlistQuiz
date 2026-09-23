import os
import random
import streamlit as st
import yt_dlp
from pydub import AudioSegment

# Folder na pliki tymczasowe
DOWNLOAD_DIR = "downloads"
CLIPS_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

st.set_page_config(page_title="YouTube Music Quiz", page_icon="🎵")
st.title("🎵 YouTube Music Quiz")

# Sidebar - Ustawienia
st.sidebar.header("⚙️ Ustawienia Quizu")
mode = st.sidebar.radio("Co chcesz odgadywać?", ["Tytuł", "Wykonawca", "Wykonawca i Tytuł"])
clip_duration = st.sidebar.slider("Długość fragmentu (sekundy):", min_value=3, max_value=30, value=10)

# Stan aplikacji
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

def download_playlist(url):
    ydl_opts = {
        'format': 'ba/bestaudio/b',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        # Ominięcie blokad IP serwerowych - podszywanie się pod klienta mobilnego iOS/Android
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web']
            }
        },
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    }
    
    files = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if info:
                entries = info.get('entries', [info])
                for entry in entries:
                    if not entry:
                        continue
                    video_id = entry.get('id')
                    mp3_filename = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
                    
                    if os.path.exists(mp3_filename):
                        title = entry.get('title', 'Unknown')
                        artist = entry.get('artist') or entry.get('uploader') or entry.get('channel', 'Unknown')
                        
                        # Czyszczenie tytułu jeśli zawiera "Artist - Title"
                        if " - " in title:
                            artist, title = title.split(" - ", 1)
                            
                        files.append({
                            "path": mp3_filename,
                            "artist": artist.strip(),
                            "title": title.strip()
                        })
        except Exception as e:
            st.error(f"Szczegóły błędu: {e}")
            
    return files

def draw_next_song():
    if not st.session_state.songs:
        return
    song = random.choice(st.session_state.songs)
    st.session_state.current_song = song
    
    audio = AudioSegment.from_file(song["path"])
    song_len_sec = int(len(audio) / 1000)
    
    if song_len_sec > clip_duration:
        start_sec = random.randint(0, song_len_sec - clip_duration)
    else:
        start_sec = 0
        
    start_ms = start_sec * 1000
    end_ms = start_ms + (clip_duration * 1000)
    
    clip = audio[start_ms:end_ms]
    clip_path = os.path.join(CLIPS_DIR, "temp_clip.mp3")
    clip.export(clip_path, format="mp3")
    st.session_state.clip_path = clip_path

# Formularz główny
playlist_url = st.text_input("Wklej link do playlisty YouTube:")
if st.button("Pobierz playlistę i rozpocznij"):
    if playlist_url:
        with st.spinner("Pobieranie playlisty... To może zająć 1-2 minuty."):
            st.session_state.songs = download_playlist(playlist_url)
            st.session_state.score = 0
            st.session_state.total = 0
            if st.session_state.songs:
                draw_next_song()
                st.success(f"Pobrano {len(st.session_state.songs)} piosenek!")
            else:
                st.error("Nie udało się pobrać utworów z tej playlisty.")
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
                st.session_state.score += 1
            else:
                st.error(f"❌ Błąd! Poprawna odpowiedź: {song['artist']} - {song['title']}")
    
    if st.button("Następne pytanie ➡️"):
        draw_next_song()
        st.rerun()
