from utils import DBConfig
import psycopg2

# Connect to the database.
def get_db_connection():
    return psycopg2.connect(
        dbname=DBConfig.DB_NAME,
        user=DBConfig.USERNAME,
        password=DBConfig.PASSWORD,
        host=DBConfig.HOSTNAME,
        port=DBConfig.PORT,
        options=DBConfig.OPTIONS
    )

def execute_sql_file(filename):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit() # valide l'envoi de la requete
        print(f"Fichier {filename} exécuté avec succès.")
    except Exception as e:
        conn.rollback() # annule l'envoi de la requete
        print(f"Erreur avec {filename} : {e}")
        raise # remonte l'erreur à la route Flask si appelé via l'API
    finally:
        cur.close()
        conn.close()

def create_tables(): # lancer le code depuis src pour que ça marche
    execute_sql_file("../sql/create_tables.sql")

def create_triggers():
    execute_sql_file("../sql/triggers.sql")

def insert_data():
    execute_sql_file("../sql/donnee_test.sql")

if __name__ == "__main__":
    try:
        create_tables()
        create_triggers()
        insert_data()
        print("Connexion réussie et initialisation réussi")
        conn.close()
    except Exception as e:
        print(f"Erreur connexion : {e}")
