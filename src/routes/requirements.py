from flask import Blueprint, jsonify, request
from psycopg2 import DatabaseError
from data_base import get_db_connection

requirements_bp = Blueprint("requirements", __name__)

# --------------------------------------------------------------------------------------------
# REQUETES CRUD :

# POST (CREATE)
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

# GET ALL (REQUEST)
@requirements_bp.route('/requirements', methods=['GET'])
def get_all_requirements():
    """
    QUESTION 1
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

# GET (by_id)
@requirements_bp.route("/requirements/<int:id_r>", methods=['GET'])
def requirement_by_id(id_r):
    """
    Renvoie tout pour l'exigence d'id = id_r
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """SELECT * FROM requirement
            WHERE id_requirement = %s;
            """, (id_r,)
        )

        res = cur.fetchone()

        if not res :
            return jsonify({"error": "Requirement not found"}), 404

        requirement = {
            "id_requirement": res[0],
            "requirement_name": res[1],
            "requirement_description": res[2],
        }

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(requirement), 200

# UPDATE (PUT)
@requirements_bp.route('/requirements/<int:id_r>', methods=['PUT'])
def update_requirement(id_r):
    """
    UPDATE (PUT) pour la table requirement
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
            UPDATE requirement
                SET requirement_name = %s, requirement_description = %s
                WHERE id_requirement = %s
            -- RETURNING permet de renvoyer la requete sans ça fetchone() ne récupère rien
            RETURNING id_requirement, requirement_name, requirement_description;
            """,
            (req_name, req_desc, id_r)
        )

        updated_row = cur.fetchone()
        
        if not updated_row:
            return jsonify({"error": "Requirement not found"}), 404    
        
        conn.commit()

        updated_req = {
            "id_requirement": updated_row[0],
            "requirement_name": updated_row[1],
            "requirement_description": updated_row[2],
        }

    except DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(updated_req), 200 

# DELETE
@requirements_bp.route("/requirements/<int:id_r>", methods=["DELETE"])
def delete_requirement(id_r):
    """
    DELETE
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """DELETE FROM requirement
            WHERE id_requirement = %s
            RETURNING id_requirement;
            """, (id_r,)
        )

        deleted_row = cur.fetchone()

        if not deleted_row :
            return jsonify({"error": "Requirement not found"}), 404

        conn.commit()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"message": f"Requirement {id_r} deleted successfully"}), 200

# --------------------------------------------------------------------------------------------

@requirements_bp.route("/requirements/<int:id_r>/tests", methods=['GET'])
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


@requirements_bp.route("/requirements/no-fail", methods=["GET"])
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

        res = cur.fetchall()
        no_fail = []

        for r in res:
            no_fail.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_description": r[2]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"no_fail": no_fail}), 200


@requirements_bp.route("/requirements/sorted-by-last-test-date", methods=['GET'])
def sorted_by_last_test_date():
    """
    QUESTION 21
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT r.*, MAX(tp.test_passage_at) as last_test_at
            FROM requirement r
            JOIN requirement_test rt ON r.id_requirement = rt.id_requirement
            JOIN test_passage tp ON tp.id_test = rt.id_test
            WHERE (tp.id_test, tp.test_passage_at) IN (
            SELECT id_test, MAX(test_passage_at)
            FROM test_passage
            GROUP BY id_test
            ) 
            GROUP BY r.id_requirement, r.requirement_name, r.requirement_description
            ORDER BY last_test_at ASC;
        """)

        res = cur.fetchall()

        list_requirements = []

        for r in res:
            list_requirements.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "requirement_description": r[2],
                "last_test_at": r[3]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(list_requirements), 200


@requirements_bp.route("/requirements/summary", methods=["GET"])
def requirement_summary():
    """
    REQUETE QUESTION 22 
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
SELECT r.id_requirement,
       r.requirement_name,
       COUNT(DISTINCT rt.id_test) AS nb_test_total, --distincte si un test est passé plusieurs fois
       CASE
           WHEN COUNT(CASE WHEN tp.test_state = 'KO' THEN 1 END) > 0 THEN 'KO' -- des qqu'un test est ko on STOP
           WHEN COUNT(tp.id_test_passage) = 0 THEN 'Non testée' -- grace a la jointure gauche on a aussi les non teste
           ELSE 'OK'
       END AS etat_exigence,
       COUNT(DISTINCT CASE WHEN tp.test_state = 'KO' THEN tp.id_test END) AS nb_tests_ko, --condition ici afin de ne pas supprimer pour les autres resultat avec un where
       -- RANK() et OVER trouvés sur internet car on ne connaissait pas : permet de classer les exigences selon leur nombre de tests KO croissant sans écraser les lignes du GROUP BY
       RANK() OVER (
           ORDER BY COUNT(DISTINCT CASE WHEN tp.test_state = 'KO' THEN tp.id_test END) ASC -- pareil que pour conter le nombre de test KO au dessus
       ) AS rang
FROM Requirement AS r
JOIN Requirement_test AS rt
  ON r.id_requirement = rt.id_requirement
LEFT JOIN Test_passage AS tp --LEFT join afin de garder aussi les exigences dont les tests ne sont pas encore réalisé
       ON rt.id_test = tp.id_test
GROUP BY r.id_requirement, r.requirement_name
ORDER BY rang ASC; --tri final pour afficher les lignes dans l'ordre du classement
        """)

        res = cur.fetchall()

        synthese = []
        for r in res:
            synthese.append({
                "id_requirement": r[0],
                "requirement_name": r[1],
                "nb_test_total": r[2],
                "etat_exigence": r[3],
                "nb_tests_ko": r[4],
                "rang": r[5]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(synthese), 200
