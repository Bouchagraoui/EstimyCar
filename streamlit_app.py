import polars as pl
import streamlit as st
from duckdb import InvalidInputException

from src.modules.app.accueil import accueil
from src.modules.app.import_mm import import_marques_modeles
from src.modules.app.menu import (
    batterie_select,
    boite_select,
    cylindre_select,
    display_annee,
    display_km,
    display_prix_selection,
    display_puissance,
    energie_select,
    finition_select,
    generation_select,
    marques_select,
    modeles_select,
    moteur_select,
    select_user_role,
)
from src.modules.app.stats_plots import show_selected_chart
from src.modules.app.tabs import (
    get_prix_moy_displayed,
    get_prix_pred_displayed,
    predict_button,
    predict_km_fictif_button,
    show_dataframe,
)
from src.modules.app.title import title
from src.modules.requetes.requetes_kpi import calcul_delta, get_avg_price, get_count_car

nom_marques_modeles = pl.DataFrame(import_marques_modeles())

title()

user_role = select_user_role()

if user_role == "None":
    accueil()

if user_role == "Acheteur":
    nb_annonces, prix_moyen = st.columns(2)
    tab_data, tab_stats, tab_surprise = st.tabs(
        ["🗃 Data", "📊 Statistiques Descriptives", "🎈 Créateurs"]
    )
    st.sidebar.header("Caractéristiques")
    try:
        marques = marques_select(user_role)
        modeles = modeles_select(nom_marques_modeles, marques, user_role)
        annee_min, annee_max = display_annee(user_role)
        km_min, km_max = display_km(user_role)
        boite = boite_select(user_role)
        energie = energie_select(user_role)
        prix_min, prix_max = display_prix_selection()
        with tab_data:
            with nb_annonces:
                with st.container(border=True):
                    st.metric(
                        label="Nombre total de voitures",
                        value=get_count_car(
                            marques,
                            modeles,
                            annee_min,
                            annee_max,
                            km_min,
                            km_max,
                            boite,
                            energie,
                            prix_min,
                            prix_max,
                        ),
                        delta=calcul_delta(
                            marques,
                            modeles,
                            annee_min,
                            annee_max,
                            km_min,
                            km_max,
                            boite,
                            energie,
                            prix_min,
                            prix_max,
                        ),
                    )
            with prix_moyen:
                with st.container(border=True):
                    st.metric(
                        "Prix moyen",
                        value=str(
                            get_avg_price(
                                marques,
                                modeles,
                                annee_min,
                                annee_max,
                                km_min,
                                km_max,
                                boite,
                                energie,
                                prix_min,
                                prix_max,
                                user_role,
                            )
                        )
                        + "€",
                    )
            show_dataframe(
                marques,
                modeles,
                annee_min,
                annee_max,
                km_min,
                km_max,
                boite,
                energie,
                prix_min,
                prix_max,
            )
        with tab_stats:
            show_selected_chart()
    except InvalidInputException as e:
        st.error(f"""
                 Il y a eu une erreur, recharger la page svp.
                 Si cette erreur persiste, 
                 n'hésitez pas à nous le signaler afin qu'elle soit corrigée. \n 
                 Détail de l'erreur : \n 
                 {e}
                 """)
    
    with tab_surprise:
        st.balloons()
        with st.expander(
            "**Cette app géniale ? Le fruit d'une alchimie numérique orchestrée par…**"
        ):
            st.write("- 👩‍💻 Aybuké BICAT : https://github.com/aybuke-b")
            st.write("- 👨‍💻 Hassan TILKI : https://github.com/HTilki")


if user_role == "Vendeur":
    tab_prediction = st.tabs(["🎯 Estimation"])
    st.sidebar.header("Caractéristiques")
    marque = marques_select(user_role)
    modele = modeles_select(nom_marques_modeles, marque, user_role)
    annee = display_annee(user_role, marque, modele)
    moteur = moteur_select(marque, modele)
    cylindre = cylindre_select(marque, modele)
    puissance = display_puissance()
    km = display_km(user_role)
    boite = boite_select(user_role)
    energie = energie_select(user_role)
    batterie = batterie_select(energie)
    generation = generation_select(marque, modele)
    finition = finition_select(marque, modele)
    with st.container():
        predict_button(
            marque,
            modele,
            annee,
            moteur,
            cylindre,
            puissance,
            km,
            boite,
            energie,
            batterie,
            generation,
            finition,
            user_role,
        )
        resultat = st.empty()
        get_prix_pred_displayed()
        get_prix_moy_displayed()
    predict_km_fictif_button(
        marque,
        modele,
        annee,
        moteur,
        cylindre,
        puissance,
        km,
        boite,
        energie,
        batterie,
        generation,
        finition,
    )
