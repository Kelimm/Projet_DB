CREATE OR REPLACE FUNCTION init_stage_passage()
RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO stage_passage (state_stage, id_stage, id_test_passage)
        SELECT 'WAITING', s.id_stage, NEW.id_test_passage
        FROM Stage as s
        WHERE s.id_test = NEW.id_test;
    RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER init_stage_passage
    AFTER INSERT ON test_passage
    FOR EACH ROW
EXECUTE FUNCTION init_stage_passage();


CREATE OR REPLACE FUNCTION update_test_passage_state()
RETURNS TRIGGER AS $$
	DECLARE
		target_id INT;
		new_state Type_state;
		nb_ko int;
		nb_waiting INT;
	BEGIN
		target_id := COALESCE(NEW.id_test_passage, OLD.id_test_passage); --recupere l'ID du new ou old 
		/*compter les étapes ko de ce test passé*/
		SELECT COUNT(*) INTO nb_ko
    		FROM stage_passage
    		WHERE id_test_passage = target_id 
      		AND state_stage = 'KO';

    		/*compter les étapes en attente de ce test passé*/
       	  	SELECT COUNT(*) INTO nb_waiting
    		FROM stage_passage
    		WHERE id_test_passage = target_id
      		AND state_stage = 'WAITING';

    		/* deduction du resultat du test*/
    		IF nb_ko > 0 THEN
        	      new_state := 'KO';
    		ELSIF nb_waiting > 0 THEN
        	      new_state := 'WAITING';
    		ELSE
		      new_state := 'OK';
    		END IF;
		
		/*mise à jour du test passé*/
    		IF new_state = 'WAITING' THEN
        	      UPDATE test_passage
        	      SET test_state = new_state,
            	      test_passage_at = NULL
        	      WHERE id_test_passage = target_id 
				  AND test_state IS DISTINCT FROM new_state;
    		ELSE
		      UPDATE test_passage
        	      SET test_state = new_state,
            	      test_passage_at = CURRENT_DATE
        	      WHERE id_test_passage = target_id 
				  AND test_state IS DISTINCT FROM new_state;
					
    		END IF;
		RETURN COALESCE(NEW,OLD);

	END;
	$$ LANGUAGE plpgsql;

CREATE TRIGGER update_test_passage_state
    AFTER INSERT OR UPDATE OF state_stage OR DELETE ON stage_passage 
    FOR EACH ROW
EXECUTE FUNCTION update_test_passage_state();
