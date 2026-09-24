st.markdown("""
    <style>
    /* Reset paska nagłówka i stopki */
    header[data-testid="stHeader"], footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Zapobieganie przewijaniu poziomemu */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* Główny kontener aplikacji */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }

    /* ZACHOWANIE 1 WIERSZA NA KAŻDYM EKRANIE */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        width: 100% !important;
        align-items: flex-end !important;
    }

    /* Pierwsza kolumna (80%) */
    [data-testid="column"]:nth-child(1) {
        flex: 4 1 80% !important;
        width: 80% !important;
        min-width: 0 !important;
    }

    /* Druga kolumna (20%) */
    [data-testid="column"]:nth-child(2) {
        flex: 1 1 20% !important;
        width: 20% !important;
        min-width: 0 !important;
    }

    /* Etykiety i pola wybieralne */
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

    /* MIKRO-STYLIZACJA DLA DRUGIEJ KOLUMNY NA MOBILE (< 600px) */
    @media (max-width: 600px) {
        /* Ukrywamy etykietę nad drugim selektorem (zostawiamy samą w pierwszej kolumnie) */
        [data-testid="column"]:nth-child(2) div[data-testid="stWidgetLabel"] {
            display: none !important;
        }

        /* Zmniejszamy wewnętrzne marginesy pola, by zmieścić ikonkę */
        [data-testid="column"]:nth-child(2) div[data-baseweb="select"] > div {
            padding-left: 6px !important;
            padding-right: 4px !important;
            justify-content: center !important;
        }

        /* Ukrywamy domyślną strzałkę rozwijania w 2. kolumnie na rzecz oszczędności miejsca */
        [data-testid="column"]:nth-child(2) svg {
            display: none !important;
        }

        /* Przycinamy tekst, by widoczna była tylko pierwsza ikonka Emoji */
        [data-testid="column"]:nth-child(2) [data-aria-selected="true"],
        [data-testid="column"]:nth-child(2) div[role="combobox"] {
            max-width: 28px !important;
            overflow: hidden !important;
            text-overflow: clip !important;
            font-size: 1.1rem !important;
            text-align: center !important;
        }
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
        margin-top: 2px;
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
