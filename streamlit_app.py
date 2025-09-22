import streamlit as st
import random
import os
import requests

# =========================
# Hilfsfunktionen
# =========================
WATCHLIST_FILE = "watchlist.txt"
OMDB_API_KEY = "dc082af9"  # <-- Dein OMDb API-Key hier
OMDB_URL = "http://www.omdbapi.com/"

def load_watchlist():
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
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for m in movies:
            f.write(f"{m['title']} | {m['director']} | {m['year']} | {m['streaming']}\n")

def search_omdb(title, director=None):
    """Suche Filme über OMDb API"""
    params = {"apikey": OMDB_API_KEY, "s": title, "type": "movie"}
    response = requests.get(OMDB_URL, params=params)
    data = response.json()
    results = []
    if data.get("Response") == "True":
        for item in data.get("Search", []):
            imdb_id = item.get("imdbID")
            # Detailinfos abrufen
            detail = requests.get(OMDB_URL, params={"apikey": OMDB_API_KEY, "i": imdb_id}).json()
            t = detail.get("Title", "")
            y = detail.get("Year", "unbekannt")
            d = detail.get("Director", "unbekannt")
            # Optional nach Regisseur filtern
            if director:
                if director.lower() in d.lower():
                    results.append({"title": t, "year": y, "director": d})
            else:
                results.append({"title": t, "year": y, "director": d})
    return results

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Meine Watchlist", page_icon="🎬")
st.title("🎬 Meine Watchlist App (OMDb Version)")

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
# OMDb-Suche + zur Watchlist hinzufügen
# -------------------------
st.subheader("🔍 OMDb-Suche und zur Watchlist hinzufügen")
search_input = st.text_input("Titel-Schlagwort")
director_input = st.text_input("Regisseur (optional)")

if st.button("Filme suchen"):
    if search_input.strip():
        results = search_omdb(search_input.strip(), director_input.strip())
        if results:
            options = [f"{f['title']} ({f['year']}) — {f['director']}" for f in results]
            selected = st.multiselect("Filme zur Watchlist hinzufügen", options)
            if st.button("Ausgewählte Filme hinzufügen"):
                for s in selected:
                    idx = options.index(s)
                    f = results[idx]
                    movies.append({"title": f["title"], "director": f["director"], "year": f["year"], "streaming": ""})
                save_watchlist(movies)
                st.success(f"✅ {len(selected)} Film(e) hinzugefügt.")
        else:
            st.warning("Keine Filme gefunden.")
    else:
        st.info("Bitte ein Schlagwort eingeben.")