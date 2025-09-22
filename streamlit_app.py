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
st.title("🎬 Meine Watchlist App")

# -------------------------
# Watchlist laden
# -------------------------
movies = load_watchlist()

# -------------------------
# Watchlist anzeigen
# -------------------------
st.subheader("📋 Aktuelle Watchlist")
if movies:
    st.table([{ "Titel": m["title"], "Regisseur": m["director"], "Jahr": m["year"], "Streaming": m["streaming"] } for m in movies])
    # Film löschen
    titles = [f"{m['title']} ({m['year']})" for m in movies]
    selected_index = st.selectbox("Film zum Entfernen auswählen", range(len(titles)), format_func=lambda x: titles[x])
    if st.button("❌ Film entfernen"):
        removed = movies.pop(selected_index)
        save_watchlist(movies)
        st.success(f"🗑️ '{removed['title']}' wurde entfernt.")
else:
    st.info("Noch keine Filme in der Watchlist.")

# -------------------------
# Zufälliger Film
# -------------------------
st.subheader("🎲 Zufälliger Film")
if movies and st.button("Film vorschlagen"):
    film = random.choice(movies)
    st.subheader(f"👉 Heute schauen: {film['title']} ({film['year']})")
    st.write(f"🎬 Regisseur: {film['director']}")
    if film['streaming']:
        st.write(f"📺 Streaming: {film['streaming']}")

# -------------------------
# IMDb-Suche + zur Watchlist hinzufügen
# -------------------------
st.subheader("🔍 IMDb-Suche und zur Watchlist hinzufügen")
search_input = st.text_input("Titel-Schlagwort")
director_input = st.text_input("Regisseur (optional)")

if st.button("IMDb-Suche"):
    if search_input.strip():
        try:
            query = search_input.strip()
            results = ia.search_movie(query)
            filtered = []
            for movie in results:
                ia.update(movie)
                title = movie.get('title', '')
                year = movie.get('year', 'unbekannt')
                directors = [d['name'] for d in movie.get('directors', [])] or ['unbekannt']

                # Filter nach Regisseur, falls angegeben
                if director_input.strip():
                    if any(director_input.lower() in d.lower() for d in directors):
                        filtered.append((title, year, directors))
                else:
                    filtered.append((title, year, directors))

            # Ergebnisse als MultiSelect zum Hinzufügen
            if filtered:
                options = [f"{f[0]} ({f[1]}) — {', '.join(f[2])}" for f in filtered]
                selected = st.multiselect("Filme zur Watchlist hinzufügen", options)
                if st.button("Ausgewählte Filme hinzufügen"):
                    for s in selected:
                        # Infos extrahieren
                        idx = options.index(s)
                        f = filtered[idx]
                        movies.append({
                            "title": f[0],
                            "director": ", ".join(f[2]),
                            "year": str(f[1]),
                            "streaming": ""
                        })
                    save_watchlist(movies)
                    st.success(f"✅ {len(selected)} Film(e) hinzugefügt.")
            else:
                st.warning("Kein passender Film in IMDb gefunden.")

        except Exception as e:
            st.error(f"Fehler bei der IMDb-Suche: {e}")
    else:
        st.info("Bitte ein Schlagwort eingeben.")