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

try :
    conn = get_db_connection()
    print("Connection réussie")

except Exception as e:
    print(f"Erreur connexion : {e}")


