CREATE OR REPLACE FUNCTION init_stage_passage()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Stage_passage (state_stage, id_stage, id_test_passage)
    SELECT 'WAITING', s.id_stage, NEW.id_test_passage
    FROM Stage AS s
    WHERE s.id_test = NEW.id_test;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER init_stage_passage
    AFTER INSERT ON Test_passage
    FOR EACH ROW
EXECUTE FUNCTION init_stage_passage();


CREATE OR REPLACE FUNCTION update_test_passage_state()
RETURNS TRIGGER AS $$
DECLARE
    target_id  INT;
    new_state  Type_state;
    nb_total   INT;
    nb_ko      INT;
    nb_waiting INT;
BEGIN
    target_id := COALESCE(NEW.id_test_passage, OLD.id_test_passage);

    SELECT COUNT(*) INTO nb_total
    FROM Stage_passage
    WHERE id_test_passage = target_id;

    IF nb_total = 0 THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    /* Compter les étapes KO de ce test passé */
    SELECT COUNT(*) INTO nb_ko
    FROM Stage_passage
    WHERE id_test_passage = target_id 
      AND state_stage = 'KO';

    /* Compter les étapes en attente de ce test passé */
    SELECT COUNT(*) INTO nb_waiting
    FROM Stage_passage
    WHERE id_test_passage = target_id
      AND state_stage = 'WAITING';

    /* Déduction du résultat du test */
    IF nb_waiting > 0 THEN
        new_state := 'WAITING';
    ELSIF nb_ko > 0 THEN
        new_state := 'KO';
    ELSE
        new_state := 'OK';
    END IF;
    
    /* Mise à jour du test passé */
    IF new_state = 'WAITING' THEN
        UPDATE Test_passage
        SET test_state = new_state,
            test_passage_at = NULL
        WHERE id_test_passage = target_id 
          AND test_state IS DISTINCT FROM new_state;
    ELSE
        UPDATE Test_passage
        SET test_state = new_state,
            test_passage_at = CURRENT_TIMESTAMP
        WHERE id_test_passage = target_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_test_passage_state
    AFTER INSERT OR UPDATE OF state_stage OR DELETE ON Stage_passage 
    FOR EACH ROW
EXECUTE FUNCTION update_test_passage_state();


CREATE OR REPLACE FUNCTION check_stage_belongs_to_test()
RETURNS TRIGGER AS $$
DECLARE
    stage_test_id   INT;
    passage_test_id INT;
BEGIN
    SELECT id_test INTO stage_test_id FROM Stage WHERE id_stage = NEW.id_stage;
    SELECT id_test INTO passage_test_id FROM Test_passage WHERE id_test_passage = NEW.id_test_passage;

    IF stage_test_id IS DISTINCT FROM passage_test_id THEN
        RAISE EXCEPTION 'L''étape % n''appartient pas au test du passage %',
            NEW.id_stage, NEW.id_test_passage;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_stage_belongs_to_test
    BEFORE INSERT OR UPDATE OF id_stage, id_test_passage ON Stage_passage
    FOR EACH ROW
EXECUTE FUNCTION check_stage_belongs_to_test();


-- CREATE OR REPLACE FUNCTION delete_test_set_results()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     DELETE FROM Stage_passage
--     WHERE id_test_passage IN (
--         SELECT id_test_passage FROM Test_passage WHERE id_test_set = OLD.id_test_set
--     );

--     DELETE FROM Test_passage
--     WHERE id_test_set = OLD.id_test_set;

--     RETURN OLD;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER delete_test_set_results
--     BEFORE DELETE ON Test_set
--     FOR EACH ROW
-- EXECUTE FUNCTION delete_test_set_results();
