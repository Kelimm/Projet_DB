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

def execute_sql_file(filename):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit() #valide l'envoi de la requete
        print(f"Fichier {filename} exécuté avec succès.")
    except Exception as e:
        conn.rollback() #annule l'envoi de la requete 
        print(f"Erreur avec {filename} : {e}")
    finally:
        cur.close()
        conn.close()

def create_tables(): #lancer le code depuis src pour que sa marche 
    execute_sql_file("../sql/create_tables.sql")

def create_triggers():
    execute_sql_file("../sql/triggers")
