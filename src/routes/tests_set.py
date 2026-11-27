
from flask import Blueprint, jsonify
from psycopg2 import DatabaseError
from data_base import get_db_connection

tests_set_bp = Blueprint("tests_set", __name__)

@tests_set_bp.route("/tests-sets/<int:id_ts>/tests", methods=['GET'])
def get_tests_by_test_set(id_ts):
    """
    QUESTION 20
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT t.id_test, t.test_name, t.test_description, t.condition_init, t.id_plan, tp.test_state
            FROM test_passage tp
            JOIN test t ON t.id_test = tp.id_test
            WHERE tp.id_test_set = %s
            """, (id_ts,)
        )

        res = cur.fetchall()

        list_tests = []

        for r in res:
            list_tests.append({
                "id_test": r[0],
                "test_name": r[1],
                "test_description": r[2],
                "condition_init": r[3],
                "id_plan": r[4],
                "test_state": r[5]
            })

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify(list_tests), 200

    