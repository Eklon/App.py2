import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import random
from justwatch import JustWatch
import os

# =========================
# Hilfsfunktionen
# =========================
WATCHLIST_FILE = "watchlist.txt"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_watchlist(movies):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for movie in movies:
            f.write(movie + "\n")

# =========================
# JustWatch initialisieren
# =========================
justwatch = JustWatch(country="DE")

# Provider-ID → Name Mapping
provider_map = {
    7: "Apple iTunes",
    8: "Netflix",
    9: "Amazon Prime Video",
    10: "Amazon Video",
    11: "Google Play Movies",
    12: "YouTube",
    15: "Hulu",
    24: "Sky Store",
    31: "Maxdome",
    37: "Disney+",
    119: "MagentaTV",
    149: "Apple TV+",
    350: "WOW",
    384: "Netflix Kids",
}

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Meine Watchlist", page_icon="🎬")
st.title("🎬 Meine Watchlist mit Streaming-Infos")

# Watchlist laden
movies = load_watchlist()

# -------------------------
# Film hinzufügen
# -------------------------
st.subheader("➕ Film hinzufügen")
new_movie = st.text_input("Filmtitel eingeben:")
if st.button("Hinzufügen"):
    if new_movie and new_movie.strip():
        new_movie = new_movie.strip()
        if new_movie not in movies:
            movies.append(new_movie)
            save_watchlist(movies)
            st.success(f"✅ '{new_movie}' wurde zur Watchlist hinzugefügt.")
        else:
            st.warning("⚠️ Dieser Film ist schon in der Watchlist.")
    else:
        st.info("Bitte einen Filmtitel eingeben.")

# -------------------------
# Filme anzeigen + löschen
# -------------------------
st.subheader("📋 Aktuelle Watchlist")
if movies:
    selected_movie = st.selectbox("Film auswählen:", movies)
    if st.button("❌ Aus Liste entfernen"):
        movies.remove(selected_movie)
        save_watchlist(movies)
        st.success(f"🗑️ '{selected_movie}' wurde entfernt.")
else:
    st.info("Noch keine Filme in der Watchlist. Füge links einen Film hinzu.")

# -------------------------
# Zufälligen Film auswählen
# -------------------------
st.subheader("🎲 Zufallsauswahl")
if movies and st.button("Film vorschlagen"):
    film = random.choice(movies)
    st.subheader(f"👉 Heute schauen: {film}")

    try:
        # JustWatch-Suche
        results = justwatch.search_for_item(query=film)

        if results["items"]:
            item = results["items"][0]
            st.write(f"**Gefunden:** {item.get('title','-')} ({item.get('original_release_year', 'unbekannt')})")

            # Anbieter anzeigen
            offers = item.get("offers", [])
            if offers:
                st.write("📺 Verfügbar bei:")
                shown = set()
                for offer in offers:
                    provider_id = offer.get("provider_id")
                    provider_name = provider_map.get(provider_id, f"Anbieter #{provider_id}")
                    if provider_name not in shown:
                        link = offer.get("urls", {}).get("standard_web", "")
                        price = offer.get("retail_price", "")
                        monetization = offer.get("monetization_type", "")
                        if link:
                            st.markdown(f"- [{provider_name}]({link}) — {monetization} {price}")
                        else:
                            st.write(f"- {provider_name} — {monetization} {price}")
                        shown.add(provider_name)
            else:
                st.warning("⚠️ Keine Streaming-/Kauf-Angebote gefunden.")
        else:
            st.error("❌ Film nicht bei JustWatch gefunden.")
    except Exception as e:
        st.error(f"Fehler bei der Abfrage: {e}")