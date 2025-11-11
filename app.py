import streamlit as st                      #On crée l'interface web
from skyfield.api import load, Topos, Star  #On charge les éphémérides etla position géographique de l'utilisateur + "Star" pour regarder Sirius
from skyfield.data import hipparcos         #On importe le catalogue des étoiles
from datetime import datetime, timedelta    #Pour manipuler la date et l'heure 
import matplotlib.pyplot as plt             #Graphiques
import numpy as                             #Calcul numériques 

#Titres
st.set_page_config(page_title="Simulateur céleste", layout="centered")
st.title("Simulateur de mouvements célestes")
st.subheader("Positions de la Lune, du Soleil et de Sirius (Skyfield / NASA / Hipparcos)")

#Widgets utilisateur
date = st.date_input("Date", datetime.now().date()) #On sélectionne la date (date du jour par défaut)
if 'heure_selectionnee' not in st.session_state:
    st.session_state.heure_selectionnee = datetime.now().time() #Permet d'initialiser à l'heure actuelle même si l'utilisateur n'intéragit pas avec ce widget 

heure = st.time_input("Heure",st.session_state.heure_selectionnee,step=timedelta(minutes=1)) #On sélectionne l'heure avec un pas de 1 minute
st.session_state.heure_selectionnee = heure #Mise à jour de l'heure 

latitude = st.number_input("Latitude", 48.8566)
longitude = st.number_input("Longitude", 2.3522)

#Chargement éphémérides 
ephemerides = load('de421.bsp')
terre = ephemerides['earth']
lune = ephemerides['moon']
soleil = ephemerides['sun']
ts = load.timescale() #Permet de convertir la date et l'heure de la variable éphémérides en données utilisable par Skyfield : temps céleste très précis

#Chargement Sirius
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f) #On charge le catalogue hipparcos qui contient toutes les étoiles

sirius_data = stars.loc[32349]  # On récupère Sirius
sirius = Star(ra_hours=sirius_data['ra_hours'], dec_degrees=sirius_data['dec_degrees']) #Transforme les coordonnées astronomiques de Sirius en objet manipulable par Skyfield


#Position utilisateur
moment = ts.utc(date.year, date.month, date.day, heure.hour, heure.minute) #La date et l'heure choisies sont converties en objet Skyfield
observateur = terre + Topos(latitude_degrees=latitude, longitude_degrees=longitude) #Position sur Terre combinée avec Topos pour avoir un point précis sinon Skyfield prend par défaut le centre de la Terre

#Calcule altitude et azimut 
def calcul_position(corps):
    app = observateur.at(moment).observe(corps).apparent() #Moment précis + on observe le corps + correction du décalage dû à la lumière 
    alt, az, _ = app.altaz() #Récupère l'altitude l'azimut et la distance pour le corps choisi
                             #Traduit la position spatiale de l'astre en repères observables depuis notre localisation
    return alt.degrees, az.degrees

#Calcul pour chaque astre 
alt_lune, az_lune = calcul_position(lune) 
alt_soleil, az_soleil = calcul_position(soleil)
alt_sirius, az_sirius = calcul_position(sirius)


#Affichage altitude et azimut
st.markdown("### Position instantanée des astres")
st.success(f"Lune : altitude {alt_lune:.2f}°, azimut {az_lune:.2f}°")
st.info(f"Soleil : altitude {alt_soleil:.2f}°, azimut {az_soleil:.2f}°")
st.warning(f"Sirius : altitude {alt_sirius:.2f}°, azimut {az_sirius:.2f}°")

st.markdown("---")
st.subheader("Évolution sur 24 heures")

#Calcul des positions sur 24h
heures = np.linspace(0, 24, 100)
altitudes_lune, altitudes_soleil, altitudes_sirius = [], [], []

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
