import streamlit as st
import random
import os
import imdb

# =========================
# Hilfsfunktionen
# =========================
WATCHLIST_FILE = "watchlist.txt"

def load_watchlist():
    """Lädt die Watchlist aus der Datei und gibt eine Liste von Dictionaries zurück"""
    movies = []
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                title = parts[0].strip()
                director = parts[1].strip() if len(parts) > 1 else "unbekannt"
                year = parts[2].strip() if len(parts) > 2 else "unbekannt"
                streaming = parts[3].strip() if len(parts) > 3 else ""
                movies.append({
                    "title": title,
                    "director": director,
                    "year": year,
                    "streaming": streaming
                })
    return movies

def save_watchlist(movies):
    """Speichert die Watchlist in der Datei"""
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for m in movies:
            f.write(f"{m['title']} | {m['director']} | {m['year']} | {m['streaming']}\n")

# =========================
# IMDb Instanz
# =========================
ia = imdb.IMDb()

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Meine Watchlist", page_icon="🎬")
st.title("🎬 Meine Watchlist mit Details")

# Load watchlist
movies = load_watchlist()

# -------------------------
# Film hinzufügen
# -------------------------
st.subheader("➕ Film hinzufügen")
new_movie = st.text_input("Filmtitel eingeben")
new_director = st.text_input("Regisseur")
new_year = st.text_input("Erscheinungsjahr")
new_streaming = st.text_input("Streaming-Anbieter (optional, Komma getrennt)")

if st.button("Hinzufügen"):
    if new_movie.strip():
        movies.append({
            "title": new_movie.strip(),
            "director": new_director.strip() if new_director else "unbekannt",
            "year": new_year.strip() if new_year else "unbekannt",
            "streaming": new_streaming.strip()
        })
        save_watchlist(movies)
        st.success(f"✅ '{new_movie.strip()}' hinzugefügt.")
    else:
        st.warning("Bitte mindestens einen Filmtitel eingeben.")

# -------------------------
# Filme anzeigen + löschen
# -------------------------
st.subheader("📋 Aktuelle Watchlist")
if movies:
    titles = [f"{m['title']} ({m['year']}) — {m['director']}" for m in movies]
    selected_index = st.selectbox("Film auswählen", range(len(titles)), format_func=lambda x: titles[x])
    if st.button("❌ Aus Liste entfernen"):
        removed = movies.pop(selected_index)
        save_watchlist(movies)
        st.success(f"🗑️ '{removed['title']}' entfernt.")
else:
    st.info("Noch keine Filme in der Watchlist.")

# -------------------------
# Zufälliger Film
# -------------------------
st.subheader("🎲 Zufallsauswahl")
if movies and st.button("Film vorschlagen"):
    film = random.choice(movies)
    st.subheader(f"👉 Heute schauen: {film['title']} ({film['year']})")
    st.write(f"🎬 Regisseur: {film['director']}")
    if film['streaming']:
        st.write(f"📺 Streaming: {film['streaming']}")

# -------------------------
# Suche nach Schlagworten + Regisseur
# -------------------------
st.subheader("🔍 Film suchen")
search_input = st.text_input("Titel oder Schlagwort")
director_input = st.text_input("Regisseur (optional)")

if st.button("Suchen"):
    results = []
    for movie in movies:
        if search_input.lower() in movie['title'].lower():
            if director_input:
                if director_input.lower() in movie['director'].lower():
                    results.append(movie)
            else:
                results.append(movie)
    if results:
        st.write("Gefundene Filme:")
        for f in results:
            st.write(f"{f['title']} ({f['year']}) — Regisseur: {f['director']} — Streaming: {f['streaming']}")
    else:
        st.warning("Kein Film gefunden.")
st.subheader("🔍 Erweiterte Suche (IMDb)")
search_input_imdb = st.text_input("Titel-Schlagwort für IMDb")
director_input_imdb = st.text_input("Regisseur für IMDb (optional)")

if st.button("IMDb-Suche"):
    if search_input_imdb.strip():
        try:
            # Filme suchen
            query = search_input_imdb.strip()
            results = ia.search_movie(query)
            filtered = []
            for movie in results:
                ia.update(movie)
                title = movie.get('title', '')
                year = movie.get('year', 'unbekannt')
                directors = [d['name'] for d in movie.get('directors', [])] or ['unbekannt']

                # Filter nach Regisseur, falls angegeben
                if director_input_imdb.strip():
                    if any(director_input_imdb.lower() in d.lower() for d in directors):
                        filtered.append((title, year, directors))
                else:
                    filtered.append((title, year, directors))

            # Ergebnisse anzeigen
            if filtered:
                st.write("Gefundene Filme in IMDb:")
                for f in filtered:
                    st.write(f"{f[0]} ({f[1]}) — Regisseur: {', '.join(f[2])}")
            else:
                st.warning("Kein passender Film in IMDb gefunden.")

        except Exception as e:
            st.error(f"Fehler bei der IMDb-Suche: {e}")
    else:
        st.info("Bitte ein Schlagwort eingeben.")