from flask import Blueprint, jsonify
from psycopg2 import DatabaseError
from data_base import get_db_connection

campaigns_bp = Blueprint("campaigns", __name__)

@campaigns_bp.route("/campaigns/<int:id_c>/stages-failed", methods=['GET'])
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

@campaigns_bp.route("/campaigns/nr/<int:id_c>", methods=['GET'])
def campaigns_non_regression_tests(id_c):
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


@campaigns_bp.route("/campaigns/<int:id_c>/count-tester", methods=['GET'])
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
        WHERE ts.id_campaign = %s;
        """, (id_c,))
        res = cur.fetchone()[0]

    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        cur.close()
        conn.close()

    return jsonify({"count_tester":res}), 200

@campaigns_bp.route("/campaigns/<int:id_c>", methods=['GET'])
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

@campaigns_bp.route("/campaigns/info", methods=['GET'])
def campaigns_information():
    """
    QUESTION 14
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT campaign_name, start_at, end_at, ts.type_test_set, t.id_test, test_state, test_name
        FROM Campaign as c, Test_set as ts, Test_passage as tp, Test as t 
        WHERE c.id_campaign = ts.id_campaign
        AND ts.id_test_set = tp.id_test_set
        AND tp.id_test = t.id_test 
        AND tp.test_state != 'WAITING'
        AND tp.test_passage_at IS NOT NULL;
        """)
        res = cur.fetchall()

        
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        cur.close()
        conn.close()

    return jsonify({"campaign_information":res}), 200
