
import streamlit as st #création de la page web
import pandas as pd #gestion des données
import folium #gestion affichage
import plotly.express as px #affichage des graphiques
from datetime import datetime

import time
import os
import json


CUR_DIR = os.path.dirname(__file__)



# --- Streamlit Config ---
st.set_page_config(page_title="Fromage", layout="wide")
st.title("📊 🧀CartoFromages v5 - Real-Time Live Fromage")
st.write("⏱️ Auto-refreshes every 60 seconds. Click the button below to manually refresh.")

# --- Handle Manual Refresh ---
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = datetime.now()

if st.button("🔄 Manual Refresh Now"):
    st.session_state['last_refresh'] = datetime.now()

st.caption(f"Last refreshed: {st.session_state['last_refresh'].strftime('%Y-%m-%d %H:%M:%S')}")

#-- récupération fichier json --

json1 = os.path.join( CUR_DIR, "dept_siqo_fromage.geojson")
csv1 = os.path.join( CUR_DIR, "dept_siqo_fromage.csv")
csv2 = os.path.join(CUR_DIR,"categorie_fromage.csv")


## chargement du fichier dans un objet json
with open(json1,encoding='utf-8') as f:
    geo_data = json.load(f)

df = pd.read_csv(csv1,encoding='utf8')
df2 = pd.read_csv(csv2,encoding='utf8',sep=';' )


## --- Select Box ---
st.subheader("Menu déroulant")

# récupération du département sélectionné
selected_department = st.selectbox(label='Choisissez un département',options= df['NOM'],index=0)

# filtre et récupération dans le dataframe de la ligne avec le nom du département choisi
filtered_data = df[df['NOM']==selected_department]
# st.text(filtered_data)

# dans la ligne, on récupère le numéro de département par INSEE_DEP
numero_departement = filtered_data['INSEE_DEP']
# st.text(numero_departement)

# dans la cellule choisie, on prend la valeur
department_id = numero_departement.values[0]


## --- Display Data ---

df_filtre = df[df['INSEE_DEP']==department_id]

st.subheader("Catégories de fromages de l'INAO")
st.dataframe(df2)


st.subheader("Tableau")

st.dataframe(df_filtre)


## --- Charts ---

st.subheader("Graphique")

## extraction d'un sous dataframe en utilisant double barre
df_graphique = df_filtre[['PPC','PPNC','PMCF','PMCL','PP','CH','AUTRES']]
# st.text(df_graphique)

df_graphique_transpose = df_graphique.transpose()
df_graphique_transpose.columns = ["VALEUR"]

liste_valeur = []

for i in df_graphique_transpose.index:
    liste_valeur.append(float(df_graphique_transpose["VALEUR"][i]))


liste_categorie = ["PPC","PPNC","PMCF","PMCL","PP","CH","AUTRES"]
color_discrete_sequence= ["#ec7c34","#ec7c34","#fdbf6f","#fdbf6f","#609cd4","#b2df8a","#fb9a99"]

# st.text(liste_valeur)
# st.text(liste_categorie)

fig = px.bar(liste_categorie, y = liste_valeur, color= liste_categorie,
             color_discrete_sequence=color_discrete_sequence,
             title="Nombre total de commune en SIQO pour les catégories de fromage")

st.plotly_chart(fig, width='stretch')




## st.text(json1)







## st.text(geo_data)

# -- Map ---
st.subheader("Départements et SIQO")
st.caption(f"Cliquez sur le département {selected_department} pour plus d'informations : ")

## on charge la vue et on va créer un geodataframe


m = folium.Map(location=[46.08,6.655],name="Light Map",zoom_start=6)

## folium est capable d'afficher des objets de type geodataframe
## la commande est folium.GeoJson()



popup = folium.GeoJsonPopup(
    fields=["NOM", "EXPLICATION"],
    aliases=["Nom du département", "Liste des SIQO"],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

folium.GeoJson(geo_data,
               popup=popup,
                style_function=lambda feature: {
                    'fillColor': 'grey' if feature['properties']['INSEE_DEP'] ==
                                           str(df[df['NOM'] == selected_department]['INSEE_DEP'].values[0]) else 'blue',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.6
                }


               ).add_to(m)



st.iframe(folium.Figure().add_child(m).render(),height=500)

## st.logo(LOGO_URL_LARGE, link='', caption="logo réalisé par © 2023 by Martine Peters (license creative commons BY-NC-SA 4.0)")
## st.text("Site réalisé sans intelligence articielle, inspiré d'autres créations cités en bas de la page")

# -- Sources ---
st.subheader("Crédits")
st.markdown("""
<p>
<em> Sources pour les données : </em>
<ul>
<li> Fond carte OpenSreetMap © OSM Contributors - IGN ADMIN EXPRESS Départements PE </li>
<li> Données INAO SIQO Fromages 2025 - Licence ouverte ETALAB </li>
</ul>
</p>
<p> 
<em>  Sources pour la programmation : </em>
<ul>
<li> data-geek-lab / real time dashboard - MIT License - Copyright (c) 2025 Data-Geek-is-my-Name </li>
<li> How to Build choropleth map in Python | Streamlit Tutorial #3 | Data Driven Maps With Python Folium - SCIENCE AND SCIENCE ONLY - Youtube</li>
</ul>
</p>

<br>

<p>
    <img src="https://www.cartodev.net/image/20240824_NIA_FR.png"> </img>
    <br>
    Réalisé sans intelligence articielle
    <br>
    <small> source logo © 2023 by Martine Peters (license creative commons BY-NC-SA 4.0) </small>
</p>
""", unsafe_allow_html=True)



footer="""<style>
a:link , a:visited{
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
text-align: center;
}


</style>
<div class="footer">
<p> Developed by F. Bougé, juillet 2026 - Tous droits réservés</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)





# --- Auto Refresh (every 600 seconds) ---
time.sleep(600)
st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
