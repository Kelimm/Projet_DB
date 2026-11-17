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

    with conn :
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Stage VALUES (%s, %s, %s, %s);",
                (1, 'etape_1', 'description', 3)
            )
            cur.execute("SELECT * FROM Stage;")
            result = cur.fetchone()
            print("Ligne insérée :", result)

except Exception as e:
    print(f"Erreur connexion : {e}")


