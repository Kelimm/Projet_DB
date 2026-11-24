from data_base import get_db_connection
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "Home_msg": "API de gestion de tests fonctionnels"
    }), 200


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

        cur.close()
        conn.close()

        new_req = {
            "id_requirement": new_row[0],
            "requirement_name": new_row[1],
            "requirement_description": new_row[2],
        }

        return jsonify(new_req), 201  # Code HTTP "created"

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": e}), 500  # Code HTTP "Internal server error", il n'a pas reussi a post


@app.route('/requirements', methods=['GET'])
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
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(requirements), 200


@app.route("/requirements/<id_r>", methods=['GET'])
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
            """, id_r)
        res = cur.fetchall()
        test = []
        for r in res:
            test.append({
                "id_test": r[0],
                "test_name": r[1]
            })

    except DatabaseError as e:
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(test), 200


@app.route("/requirements/tests-count", methods=['GET'])
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
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(nb_test), 200


@app.route("/requirements/passed-tests")
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
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(requirements_list), 200


@app.route("/requirements/state")
def requirement_state():
    """
    REQUETE QUESTION 5
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
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
                    SELECT id_test, MAtest_passage_at) as max_date
                    FROM test_passage
                    GROUP BY id_test
                )
            ) last_test_request ON last_test_request.id_test = t.id_test
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
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(requirements_state), 200


@app.route("/campaign/<int:id_c>/stages-failed", methods=['GET'])
def campaign_failed_stages(id_c):
    """
    REQUETE QUESTION 6
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id_stage_passage, state_stage, commentary
            FROM stage_passage
            WHERE id_test_passage IN (
                SELECT id_test_passage 
                FROM test_passage
                WHERE id_test_set IN (
                    SELECT id_test_set 
                    FROM test_set ts
                    JOIN campaign c ON ts.id_campaign = %s and ts.id_campaign=c.id_campaign
                )
            ) AND state_stage='KO';
            """, (id_c))
        res = cur.fetchall()
        campaign_failed_stages = []
        for r in res:
            campaign_failed_stages.append({
                "id_stage_passage": r[0],
                "state_stage": r[1],
                "commentary": r[2]
            })

    except DatabaseError as e:
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(campaign_failed_stages), 200


@app.route("/requirements/<date1>/<date2>", methods=['GET'])
def test_in_date(date1, date2):
    """
    REQUETE QUESTION 7
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT *
            FROM Test as t
            WHERE t.id_test in (SELECT id_test
                                FROM Test_passage
                                WHERE test_passage_at BETWEEN %s AND %s);

            """, (date1, date2))
        res = cur.fetchall()
        test = []
        for r in res:
            test.append({
                "id_test": r[0],
                "test_name": r[1]
            })

    except DatabaseError as e:
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(test), 200


@app.route("/requirements/nb-test-more-than-3", methods=['GET'])
def requirement_with_3_plus_test():
    """
    REQUETE QUESTION 8
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT *
            FROM requirement
            WHERE id_requirement IN (
                SELECT count(id_test)
                FROM requirement_test
                GROUP BY id_requirement
                HAVING count(id_test) >= 3
            );
            """)
        res = cur.fetchall()
        requirement_list = []
        for r in res:
            requirement_list.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_description": r[2]
            })

    except DatabaseError as e:
        print(e)

    finally:
        cur.close()
        conn.close()
        return jsonify(requirement_list), 200


if __name__ == "__main__":
    app.run(debug=True)
