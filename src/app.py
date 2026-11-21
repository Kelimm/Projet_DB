import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"

st.title("Gestion de tests fonctionnels")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Afficher les exigences", "Ajouter une Exigence", "Etat des Exigences"]
)

if menu == "Afficher les exigences" :
    st.header("Liste des exigences logicielles")
    try : 
        response = requests.get(f"{BASE_URL}/requirements")
        if response.status_code == 200 :
            data = response.json()
            if data:
                st.dataframe(data)
            else :
                st.info("Aucune exigence trouvée dans la DB")
        else :
            st.error(f"ERREUR API : code {response.status_code}")

    except Exception as e :
        st.error(f"ERREUR CONNEXION : Vérfiez que le serveur Flask est lancée.\n {e}")