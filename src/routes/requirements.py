from flask import Blueprint, jsonify, request
from psycopg2 import DatabaseError
from data_base import get_db_connection

requirements_bp = Blueprint("requirements", __name__)

@requirements_bp.route('/requirements', methods=['POST'])
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

    try:
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

        new_req = {
            "id_requirement": new_row[0],
            "requirement_name": new_row[1],
            "requirement_description": new_row[2],
        }

    except DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(new_req), 201  # Code HTTP "created"


@requirements_bp.route('/requirements', methods=['GET'])
def get_requirements():
    """
    REQUETE QUESTION 1
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT * FROM requirement;"
        )

        res = cur.fetchall()

        requirements = []
        for r in res:
            requirements.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_description": r[2],
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(requirements), 200

@requirements_bp.route("/requirements/<int:id_r>", methods=['GET'])
def test_for_requirement(id_r):
    """
    REQUETE QUESTION 2
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT rt.id_test, t.test_name
            FROM Test as t, Requirement_test as rt
            WHERE t.id_test = rt.id_test
            AND rt.id_requirement = %s ;
            """, (id_r,))
        res = cur.fetchall()
        test = []
        for r in res:
            test.append({
                "id_test": r[0],
                "test_name": r[1]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(test), 200

@requirements_bp.route("/requirements/tests-count", methods=['GET'])
def nb_test_requirement():
    """
    REQUETE QUESTION 3
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT r.id_requirement, r.requirement_name, count(id_test) as nb_test
            FROM Requirement as r LEFT JOIN Requirement_test as rt 
            ON r.id_requirement = rt.id_requirement
            GROUP BY r.id_requirement
            ORDER BY r.id_requirement;
            """)
        res = cur.fetchall()

        nb_test = []
        for r in res:
            nb_test.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "nb_test": r[2]
            })


    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(nb_test), 200

@requirements_bp.route("/requirements/passed-tests", methods=['GET'])
def requirements_passed_test():
    """
    REQUETE QUESTION 4
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT r.id_requirement, r.requirement_name, t.test_name, tp.test_passage_at, tp.test_state
            FROM Requirement AS r, Test as t, Test_passage as tp, Requirement_test as rt
            WHERE r.id_requirement = rt.id_requirement
            AND rt.id_test = t.id_test
            AND t.id_test = tp.id_test 
            ORDER BY r.id_requirement, tp.test_passage_at;
            """)
        res = cur.fetchall()

        requirements_list = []
        for r in res:
            requirements_list.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "test_name": r[2],
                "test_passage_at": r[3],
                "test_state": r[4]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(requirements_list), 200
    
@requirements_bp.route("/requirements/state", methods=['GET'])
def requirement_state():
    """
    REQUETE QUESTION 5
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT  r.id_requirement, 
            r.requirement_name, 
            CASE
                WHEN BOOL_OR(tp.test_state = 'KO') THEN 'KO'
                WHEN BOOL_OR(tp.test_state = 'WAITING') THEN 'WAITING'
                ELSE 'OK'
            END AS requirement_state
            
            FROM requirement r
            JOIN requirement_test rt ON r.id_requirement = rt.id_requirement
            JOIN test t ON t.id_test = rt.id_test
            JOIN test_passage tp ON tp.id_test = t.id_test
            WHERE (tp.id_test, test_passage_at) IN (
                -- Recuperation du dernier etat du test
                SELECT id_test, MAX(test_passage_at) as max_date
                FROM test_passage
                GROUP BY id_test
                )
            GROUP BY r.id_requirement, r.requirement_name
            ORDER BY r.id_requirement;
            """)
        res = cur.fetchall()

        requirements_state = []
        for r in res:
            requirements_state.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_state": r[2]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(requirements_state), 200

@requirements_bp.route("/requirements/nb-test-more-than-3", methods=['GET'])
def count_requirements_with_more_than_3_test():
    """
    REQUETE QUESTION 8
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT count(*) as nbexigence
            FROM (
                SELECT id_requirement
                FROM requirement_test
                GROUP BY id_requirement
                HAVING count(id_test) > 3
            );
            """)
        # Récupération de l'élément 0 car fetchone renvoie un tuple
        nb_requirement = cur.fetchone()[0]

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"Nombre d'exigences couverte par plus de 3 tests": nb_requirement}), 200

@requirements_bp.route("/requirements/sorted-by-ok-tests", methods=['GET'])
def requirements_sorted_by_ok_tests():
    """
    QUESTION 16
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT r.id_requirement, r.requirement_name, r.requirement_description, COUNT(tp.id_test_passage) AS nb_tests_ok
        FROM requirement r
        LEFT JOIN requirement_test rt ON rt.id_requirement = r.id_requirement
        LEFT JOIN test_passage tp ON tp.id_test = rt.id_test AND tp.test_state = 'OK'
        GROUP BY r.id_requirement, r.requirement_name, r.requirement_description
        ORDER BY nb_tests_ok DESC;
        """)
        res = cur.fetchall()

        requirements_sorted = []

        for r in res:
            requirements_sorted.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_description": r[2],
                "nb_tests_ok": r[3]
            })
    
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(requirements_sorted), 200


@app.route("/requirements/no-fail", methods=["GET"])
def never_fail():
    """
    REQUETE QUESTION 15 : Exigences n'ayant jamais eu de test en échec ('KO')
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT r.*
            FROM Requirement AS r
            WHERE NOT EXISTS (
                SELECT *
                FROM Requirement_test AS rt,
                     Test_passage AS tp
                WHERE rt.id_requirement = r.id_requirement
                AND rt.id_test = tp.id_test
                AND tp.test_state = 'KO'
            );
        """)

        no_fail = cur.fetchall()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"no_fail": no_fail}), 200
