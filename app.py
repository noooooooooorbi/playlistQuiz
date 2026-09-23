# Panel rozgrywki
song = st.session_state.current_song

if song and isinstance(song, dict) and song.get("preview_url"):
    st.divider()
    
    score_class = "score-success" if st.session_state.last_correct else "score-normal"
    st.markdown(f"""
        <div class="score-box {score_class}">
            Wynik: {st.session_state.score} / {st.session_state.total} &nbsp;|&nbsp; Pozostało piosenek: {len(st.session_state.songs_pool) + 1}
        </div>
    """, unsafe_allow_html=True)
    
    # Bezpieczne wywołanie audio
    st.audio(
        song["preview_url"],
        key=f"player_{st.session_state.audio_id}"
    )
    
    default_option = "Nie mam pojęcia! :-)"
    selectable_options = [default_option] + st.session_state.options_list
    
    user_choice = st.selectbox(
        "Wybierz odpowiedź z listy:", 
        options=selectable_options, 
        key=f"q_select_{st.session_state.audio_id}"
    )

    if not st.session_state.answered:
        if st.button("Sprawdź"):
            st.session_state.total += 1
            st.session_state.answered = True
            
            if user_choice == default_option:
                st.session_state.last_correct = False
                st.session_state.feedback_type = "info"
                st.session_state.feedback_msg = f"💡 Poprawna odpowiedź to: **{song['artist']} - {song['title']}**"
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
                    st.session_state.feedback_type = "success"
                    st.session_state.feedback_msg = f"🎯 Poprawna odpowiedź! (**{song['artist']} - {song['title']}**)"
                    st.balloons()
                else:
                    st.session_state.last_correct = False
                    st.session_state.feedback_type = "error"
                    st.session_state.feedback_msg = f"❌ Błąd! Poprawna odpowiedź to: **{song['artist']} - {song['title']}**"
            st.rerun()

    if st.session_state.answered:
        msg = getattr(st.session_state, "feedback_msg", "")
        fb_type = getattr(st.session_state, "feedback_type", "info")
        
        if fb_type == "success":
            st.success(msg)
        elif fb_type == "error":
            st.error(msg)
        else:
            st.info(msg)
            
        if st.button("Następne pytanie ➡️"):
            draw_next_song()
            st.rerun()

elif st.session_state.current_song:
    # Jeśli utwór został wylosowany, ale brakuje podglądu dźwięku
    st.warning("Piosenka nie posiada dostępnej próbki audio. Przechodzenie do kolejnej...")
    draw_next_song()
    st.rerun()

elif st.session_state.total > 0 and not st.session_state.songs_pool:
    st.divider()
    st.balloons()
    st.header("🎉 Koniec Quizu!")
    st.subheader(f"Twój ostateczny wynik to: {st.session_state.score} / {st.session_state.total}")
