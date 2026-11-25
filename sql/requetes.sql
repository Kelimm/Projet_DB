/* debut requete sql*/
-- question 1

SELECT *
FROM requirement;

--question 2 

 SELECT rt.id_test, t.test_name
 FROM Test as t, Requirement_test as rt
 WHERE t.id_test = rt.id_test
 AND rt.id_requirement = %s ;


--question3

SELECT rt.id_requirement,r.requirement_name,count(id_test) as nb_test
FROM Requirement as r 
LEFT JOIN Requirement_test as rt ON r.id_requirement = rt.id_requirement
GROUP BY r.id_requirement
ORDER BY r.id_requirement;

--question4

SELECT r.id_requirement,r.requirement_name,t.test_name,tp.test_passage_at,tp.test_state
FROM Requirement AS r, Test as t, Test_passage as tp, Requirement_test as rt
WHERE r.id_requirement = rt.id_requirement
AND rt.id_test = t.id_test
AND t.id_test = tp.id_test 
ORDER BY r.id_requirement, tp.test_passage_at;

--question 6
SELECT id_stage_passage, state_stage, commentary
FROM stage_passage
WHERE id_test_passage IN (
 SELECT id_test_passage 
 FROM test_passage
 WHERE id_test_set IN (
 SELECT id_test_set 
 FROM test_set ts
 JOIN campaign c ON ts.id_campaign = 3 and ts.id_campaign=c.id_campaign
 )
) AND state_stage='KO';

--question 7


SELECT *
FROM Test as t
WHERE t.id_test in (SELECT id_test
      		    FROM Test_passage
		    WHERE test_passage_at BETWEEN '2026-10-06' AND '2026-10-09');

--question 9
--réalisé our montrer que la sous requete aurai était possible seulement si on nous demandais les éléments d'une seule table dans le select 
SELECT *
FROM Test
WHERE id_test IN (SELECT id_test
      	      	  FROM Test_passage
		  WHERE id_test_set IN (SELECT id_test_set
		  		        FROM Test_set
					WHERE id_campaign = $));


SELECT c.id_campaign,
       c.campaign_name,
       ts.id_test_set,
       ts.type_test_set,
       t.id_test,
       t.test_name,
       t.test_description,
       t.initial_condition,
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


--question 10

SELECT id_test,
       test_state,
       test_passage_at
FROM test_passage
WHERE id_test_set IN (SELECT id_test_set
                      FROM test_set
                      WHERE id_campaign = %s
                      AND test_set_type = 'NON_REGRESSION');


--question 11

SELECT t.id_test,
       t.test_name,
       tp.id_test_passage,
       tp.test_state,
       tp.test_passage_at
FROM Test AS t,
     Test_passage AS tp
WHERE t.id_test = tp.id_test
  AND t.id_test = %s

--question 14

SELECT campaign_name, start_at, end_at, ts.test_set_type, t.id_test, test_state, test_name
FROM Campaign as c, Test_set as ts, Test_passage as tp, Test as t 
WHERE c.id_campaign = ts.id_campaign
AND ts.id_test_set = tp.id_test_set
AND tp.id_test = t.id_test 
AND tp.test_state != 'WAITING'
AND tp.test_passage_at IS NOT NULL
ORDER BY c.id_campaign;
