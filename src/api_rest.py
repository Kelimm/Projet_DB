from data_base import get_db_connection
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "Home_msg":"API de gestion de tests fonctionnels"
    }), 200

@app.route('/get_all', methods=['GET'])
def get_all():
    pass

@app.route('/requirements', methods=['GET'])
def get_requirements():
    """
    REQUETE QUESTION 1
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM requirement;"
    )

    res = cur.fetchall()
    cur.close()
    conn.close()

    requirements = []

    for r in res: 
        requirements.append({
            "id_requirement": r[0],
            "requirement_name": r[1],
            "requirement_description": r[2],
        })
    return jsonify(requirements), 200

@app.route("/nb_test_for_requirement", methods=['GET'])
def nb_test_requirement():
    """
    REQUETE QUESTION 3
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.id_requirement, r.requirement_name, count(id_test) as nb_test
        FROM Requirement as r  LEFT JOIN Requirement_test as rt 
        ON r.id_requirement = rt.id_requirement
        GROUP BY r.id_requirement
        ORDER BY r.id_requirement;
        """)
    res = cur.fetchall()

    cur.close()
    conn.close()

    nb_test = []
    for r in res:
        nb_test.append({
            "id_requirement": r[0],
            "requirement_name": r[1],
            "nb_test": r[2]
        })

    return nb_test
if __name__=="__main__":
    app.run(debug=True)