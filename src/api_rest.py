from data_base import get_db_connection
from flask import Flask, jsonify, request
from psycopg2 import DatabaseError

app = Flask(__name__)

# Permet d'afficher les données dans l'ordre que l'on souhaite
app.json.sort_keys = False

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

        new_req = {
            "id_requirement": new_row[0],
            "requirement_name": new_row[1],
            "requirement_description": new_row[2],
        }

        return jsonify(new_req), 201  # Code HTTP "created"

    except DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


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

        return jsonify(requirements), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/requirements/<int:id_r>", methods=['GET'])
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

        return jsonify(test), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


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

        return jsonify(nb_test), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/requirements/passed-tests", methods=['GET'])
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

        return jsonify(requirements_list), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/requirements/state", methods=['GET'])
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

        return jsonify(requirements_state), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/campaigns/<int:id_c>/stages-failed", methods=['GET'])
def campaign_failed_stages(id_c):
    """
    REQUETE QUESTION 6
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT sp.id_stage_passage, s.stage_name, sp.state_stage, sp.commentary
            FROM stage_passage sp
            JOIN test_passage tp ON sp.id_test_passage = tp.id_test_passage
            JOIN test_set ts ON tp.id_test_set = ts.id_test_set
            JOIN stage s ON sp.id_stage = s.id_stage
            WHERE ts.id_campaign = %s
            AND sp.state_stage = 'KO';
            """, (id_c,))
        res = cur.fetchall()

        campaign_failed_stages = []
        for r in res:
            campaign_failed_stages.append({
                "id_stage_passage": r[0],
                "stage_name": r[1],
                "state_stage": r[2],
                "commentary": r[3]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(campaign_failed_stages), 200



@app.route("/tests/<date1>/<date2>", methods=['GET'])
def test_in_date(date1, date2):
    """
    REQUETE QUESTION 7
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id_test, test_name
            FROM Test as t
            WHERE t.id_test IN (
                SELECT id_test
                FROM Test_passage
                WHERE test_passage_at BETWEEN %s AND %s
            );
            """, (date1, date2))
        res = cur.fetchall()

        test = []
        for r in res:
            test.append({
                "id_test": r[0],
                "test_name": r[1]
            })

        return jsonify(test), 200

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/requirements/nb-test-more-than-3", methods=['GET'])
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

@app.route("/campaigns/<int:id_c>", methods=['GET'])
def campaign_test_book(id_c):
    """
    REQUETE QUESTION 9 : Afficher le cahier de test associé à une campagne
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT c.id_campaign,
                   c.campaign_name,
                   ts.id_test_set,
                   ts.type_test_set,
                   t.id_test,
                   t.test_name,
                   t.test_description,
                   t.condition_init,
                   tp.id_test_passage,
                   tp.test_state,
                   tp.test_passage_at,
                   s.id_stage,
                   s.stage_name,
                   s.stage_description,
                   s.expectation,
                   sp.state_stage,
                   sp.commentary
            FROM Campaign AS c,
                 Test_set AS ts,
                 Test_passage AS tp,
                 Test AS t,
                 Stage AS s,
                 Stage_passage AS sp
            WHERE c.id_campaign = ts.id_campaign
              AND ts.id_test_set = tp.id_test_set
              AND tp.id_test = t.id_test
              AND t.id_test = s.id_test
              AND s.id_stage = sp.id_stage
              AND sp.id_test_passage = tp.id_test_passage
              AND c.id_campaign = %s
            """, (id_c,))
        
        test_book = cur.fetchall()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/campaign/nr/<int:id_c>", methods=['GET'])
def campaign_non_regression_tests(id_c):
    """
    REQUETE QUESTION 10
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT id_test,
            test_state,
            test_passage_at
        FROM test_passage
        WHERE id_test_set IN (SELECT id_test_set
                      FROM test_set
                      WHERE id_campaign = %s
                      AND test_set_type = 'NON_REGRESSION');

            """, (id_c,))
        
        test_non_r = cur.fetchall()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"test de non regression": test_non_r}), 200



@app.route("/test/<int:id_t>", methods=['GET'])
def all_state_test(id_t):
    """
    REQUETE QUESTION 11 
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT t.id_test,
                t.test_name,
                tp.id_test_passage,
                tp.test_state,
                tp.test_passage_at
            FROM Test AS t,
                Test_passage AS tp
            WHERE t.id_test = tp.id_test
            AND t.id_test = %s

            """, (id_t,))
        
        resultat_test = cur.fetchall()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"resultat_test": resultat_test}), 200

    return jsonify({"Cahier de test de la campagne": test_book}), 200

@app.route("/campaigns/<int:id_c>/count-tester", methods=['GET'])
def campaigns_count_tester(id_c):
    """
    QUESTION 12
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT count(DISTINCT tp.id_tester) as count_tester
        FROM test_passage tp
        JOIN test_set ts ON ts.id_test_set = tp.id_test_set
        WHERE ts.id_campaign = %s
        """, (id_c,))
        res = cur.fetchone()[0]

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        cur.close()
        conn.close()

    return jsonify({"count_tester":res}), 200

@app.route("/campaigns/tester-tests-count", methods=['GET'])
def testers_tests_count():
    """
    QUESTION 13
    """
 
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT tp.id_tester, t.tester_name, count(id_test) as count_test
        FROM test_passage tp
        JOIN tester t ON t.id_tester = tp.id_tester

        GROUP BY tp.id_tester, t.tester_name
        """)
        res = cur.fetchall()

        tester_list = []
        for r  in res:
            tester_list.append({
                "id_tester": r[0],
                "tester_name": r[1],
                "count_test": r[2]
            })
        
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        cur.close()
        conn.close()

    return jsonify(tester_list), 200

if __name__ == "__main__":
    app.run(debug=True)
