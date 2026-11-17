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