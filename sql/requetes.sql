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
