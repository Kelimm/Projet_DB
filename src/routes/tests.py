from flask import Blueprint, jsonify
from psycopg2 import DatabaseError
from data_base import get_db_connection

tests_bp = Blueprint("tests", __name__)


@tests_bp.route("/tests/<date1>/<date2>", methods=['GET'])
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

@tests_bp.route("/tests/<int:id_t>", methods=['GET'])
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
            AND t.id_test = %s;

            """, (id_t,))
        
        resultat_test = cur.fetchall()

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"resultat_test": resultat_test}), 200

    return jsonify({"Cahier de test de la campagne": test_book}), 200

