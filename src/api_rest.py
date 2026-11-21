from data_base import get_db_connection
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "Home_msg":"API de gestion de tests fonctionnels"
    }), 200

@app.route('/get_all', methods=['GET'])
def get_all():
    pass

@app.route('/requirements', methods=['POST'])
def create_requirement():
    """
    CREATE (POST) pour la table requirement
    """
    data = request.get_json()

    if not data or "requirement_name" not in data or "requirement_description" not in data:
        return jsonify({
            "ERROR": "Missing data"
        }), 400

    req_name = data.get("requirement_name")
    req_desc = data.get("requirement_description")

    conn = get_db_connection()
    cur = conn.cursor()

    try : 
        cur.execute(
            """
            INSERT INTO requirement (requirement_name, requirement_description)
            VALUES (%s,%s)
            -- RETURNING permet de renvoyer la requete sans ça fetchone() ne récupère rien
            RETURNING id_requirement, requirement_name, requirement_description 
            """,
            (req_name, req_desc)
        )

        new_row = cur.fetchone()

        conn.commit()

        cur.close()
        conn.close()

        new_req = {
            "id_requirement": new_row[0],
            "requirement_name": new_row[1],
            "requirement_description": new_row[2],
        }

        return jsonify(new_req), 201 # Code HTTP "created"
        
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": e}), 500 # Code HTTP "Internal server error", il n'a pas reussi a post
    
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

@app.route("/requirements/tests-count", methods=['GET'])
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

    return jsonify(nb_test), 200

@app.route("/requirements/passed-tests")
def requirements_passed_test():
    """
    REQUETE QUESTION 4
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.id_requirement, r.requirement_name, t.test_name, tp.test_passage_at, tp.test_state
        FROM Requirement AS r, Test as t, Test_passage as tp, Requirement_test as rt
        WHERE r.id_requirement = rt.id_requirement
        AND rt.id_test = t.id_test
        AND t.id_test = tp.id_test 
        ORDER BY r.id_requirement, tp.test_passage_at;
        """)
    res = cur.fetchall()

    cur.close()
    conn.close()

    requirements_list = []
    for r in res:
        requirements_list.append({
            "id_requirement": r[0],
            "requirement_name": r[1],
            "test_name": r[2],
            "test_passage_at": r[3],
            "test_state": r[4]
        })

    return jsonify(requirements_list), 200

@app.route("/requirements/state")
def requirement_state():
    """
    REQUETE QUESTION 5
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        -- Utilisation du min(last_test_request.test_state), K est avant O dans l'alphabet 
        -- donc si une seul etape est KO alors l'exigence est KO aussi
        SELECT r.id_requirement, r.requirement_name, MIN(last_test_request.test_state) as requirement_state
        FROM requirement r
        JOIN requirement_test rt ON r.id_requirement = rt.id_requirement
        JOIN test t ON t.id_test = rt.id_test
        JOIN (
            SELECT id_test, test_state
            FROM test_passage
            WHERE (id_test, test_passage_at) IN (
                -- Recuperation du dernier etat du test
                SELECT id_test, MAX(test_passage_at) as max_date
                FROM test_passage
                GROUP BY id_test
            )
        ) last_test_request ON last_test_request.id_test = t.id_test
        GROUP BY r.id_requirement, r.requirement_name
        ORDER BY r.id_requirement;
        """)
    res = cur.fetchall()

    cur.close()
    conn.close()

    requirements_state = []
    for r in res:
        requirements_state.append({
            "id_requirement": r[0],
            "requirement_name": r[1],
            "requirement_state": r[2]
        })

    return jsonify(requirements_state), 200



    
if __name__=="__main__":
    app.run(debug=True)