from flask import Blueprint, jsonify
from psycopg2 import DatabaseError
from data_base import get_db_connection

testers_bp = Blueprint("testers", __name__)


@testers_bp.route("/testers/tests-count", methods=['GET'])
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