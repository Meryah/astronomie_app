import streamlit as st
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

#Titres
st.set_page_config(page_title="Simulateur céleste", layout="centered")
st.title("Simulateur de mouvements célestes")
st.subheader("Positions de la Lune, du Soleil et de Sirius (Skyfield / NASA / Hipparcos)")

#Widgets utilisateur
date = st.date_input("Date", datetime.now().date())
if 'heure_selectionnee' not in st.session_state:
    st.session_state.heure_selectionnee = datetime.now().time()

heure = st.time_input("Heure",st.session_state.heure_selectionnee,step=timedelta(minutes=1))
st.session_state.heure_selectionnee = heure

latitude = st.number_input("Latitude", 48.8566)
longitude = st.number_input("Longitude", 2.3522)

#Chargement éphémérides 
ephemerides = load('de421.bsp')
terre = ephemerides['earth']
lune = ephemerides['moon']
soleil = ephemerides['sun']
ts = load.timescale()

# --- Catalogue d’étoiles pour Sirius ---
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

sirius_data = stars.loc[32349]  # HIP 32349 = Sirius
sirius = Star(ra_hours=sirius_data['ra_hours'], dec_degrees=sirius_data['dec_degrees'])


# --- Création position observateur ---
moment = ts.utc(date.year, date.month, date.day, heure.hour, heure.minute)
observateur = terre + Topos(latitude_degrees=latitude, longitude_degrees=longitude)

# --- Fonction pour calculer altitude / azimut ---
def calcul_position(corps):
    app = observateur.at(moment).observe(corps).apparent()
    alt, az, _ = app.altaz()
    return alt.degrees, az.degrees

#Calcul instantané 
alt_lune, az_lune = calcul_position(lune)
alt_soleil, az_soleil = calcul_position(soleil)
alt_sirius, az_sirius = calcul_position(sirius)


#Affichage instantané
st.markdown("### Position instantanée des astres")
st.success(f"Lune : altitude {alt_lune:.2f}°, azimut {az_lune:.2f}°")
st.info(f"Soleil : altitude {alt_soleil:.2f}°, azimut {az_soleil:.2f}°")
st.warning(f"Sirius : altitude {alt_sirius:.2f}°, azimut {az_sirius:.2f}°")

st.markdown("---")
st.subheader("Évolution sur 24 heures")

#Calcul des positions sur 24h
heures = np.linspace(0, 24, 100)
altitudes_lune, altitudes_soleil, altitudes_sirius = [], [], []

observateur = terre + Topos(latitude_degrees=latitude, longitude_degrees=longitude)

for h in heures:
    t = ts.utc(date.year, date.month, date.day, int(h), int((h % 1) * 60))
    altitudes_lune.append(observateur.at(t).observe(lune).apparent().altaz()[0].degrees)
    altitudes_soleil.append(observateur.at(t).observe(soleil).apparent().altaz()[0].degrees)
    altitudes_sirius.append(observateur.at(t).observe(sirius).apparent().altaz()[0].degrees)

#Trouver l'indice de l'heure sélectionnée
indice = (np.abs(heures - (heure.hour + heure.minute/60))).argmin()

#Graphique
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(heures, altitudes_lune, label="Lune", color="black",linewidth=2)
ax.plot(heures, altitudes_soleil, label="Soleil",color="#ffd700", linewidth=2)
ax.plot(heures, altitudes_sirius, label="Sirius",color="#1e90ff", linewidth=2)

# Ligne verticale à l'heure choisie
ax.axvline(heure.hour + heure.minute/60, color='grey', linestyle=':', linewidth=2, label='Heure sélectionnée')

# Marquer les points instantanés
ax.plot(heures[indice], altitudes_lune[indice], 'o', color="black")
ax.plot(heures[indice], altitudes_soleil[indice], 'o', color="#ffd700")
ax.plot(heures[indice], altitudes_sirius[indice], 'o', color="#1e90ff")

ax.set_xlabel("Heure (UTC)", fontsize=12)
ax.set_ylabel("Altitude (°)", fontsize=12)
ax.set_title("Évolution de l'altitude sur 24h", fontsize=14)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.7)

st.pyplot(fig)


st.markdown("""
<style>
body {background: radial-gradient(circle at 20% 20%, #0b0c10, #1f2833);}
h1, h2, h3, label, .stMarkdown {color: #f8f9fa !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("*Projet personnel – Simulation astronomie Python *")