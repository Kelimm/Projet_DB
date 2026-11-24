/* debut requete sql*/
-- question 1

SELECT *
FROM requirement;

--question 2 

CREATE OR REPLACE FUNCTION get_requirement_by_test(id_test INT)
RETURNS SETOF requirement
AS $$
   SELECT r.*
   FROM Requirement as r, Requirement_test as rt
   WHERE r.id_requirement = rt.id_requirement
   AND rt.id_test = $1;
   $$LANGUAGE sql;

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

--question 5

