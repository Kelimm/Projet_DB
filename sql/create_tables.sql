CREATE DOMAIN Type_state 
AS VARCHAR(7)
CHECK (VALUE IN ('OK', 'KO', 'WAITING'));

CREATE DOMAIN Test_set_type
AS VARCHAR(14)
CHECK (VALUE IN ('Non_regression', 'Functional'));

CREATE TABLE Requirement (
 id_requirement SERIAL PRIMARY KEY,
 requirement_name VARCHAR(50),
 requirement_description VARCHAR(255)
 );

CREATE TABLE Plan (
 id_plan SERIAL PRIMARY KEY,
 plan_name VARCHAR(20)
);

CREATE TABLE Test (
 id_test SERIAL PRIMARY KEY,
 test_name VARCHAR(50),
 test_description VARCHAR(255),
 initial_condition VARCHAR(20),
 id_plan INT REFERENCES Plan(id_plan) ON DELETE CASCADE
);

CREATE TABLE Requirement_test (
 id_test INT REFERENCES Test(id_test),
 id_requirement INT REFERENCES Requirement(id_requirement),
 PRIMARY KEY (id_test, id_requirement)
);

CREATE TABLE Stage (
 id_stage SERIAL PRIMARY KEY,
 stage_name VARCHAR(50),
 stage_description VARCHAR(255),
 expectation VARCHAR(255), 
 id_test INT REFERENCES Test(id_test) ON DELETE CASCADE
);

CREATE TABLE Campaign (
 id_campaign SERIAL PRIMARY KEY,
 campaign_name VARCHAR(50),
 software_version INT,
 start_at DATE,
 end_at DATE
);

CREATE TABLE Test_set (
 id_test_set SERIAL PRIMARY KEY,
 type_test_set Test_set_type,
 id_campaign INT REFERENCES Campaign(id_campaign)
);

CREATE TABLE Tester (
 id_tester SERIAL PRIMARY KEY,
 tester_name VARCHAR(20)
);


CREATE TABLE Test_passage (
 id_test_passage SERIAL PRIMARY KEY,
 test_passage_at TIMESTAMP,
 test_state Type_state DEFAULT 'WAITING',
 id_test_set INT REFERENCES Test_set(id_test_set) ON DELETE CASCADE, -- Permet de repondre a la question Supprimer les resultats quand un jeu de test est supprimé
 id_tester INT REFERENCES Tester(id_tester) ON DELETE SET NULL, -- Si un testeur quitte l'entreprise je garde l'historique de ses tests
 id_test INT REFERENCES Test(id_test) ON DELETE CASCADE -- Permet de repondre a la question Supprimer les resultats quand un jeu de test est supprimé
);

CREATE TABLE Stage_passage (
 id_stage_passage SERIAL PRIMARY KEY,
 state_stage Type_state,
 commentary VARCHAR(50),
 id_stage INT REFERENCES Stage(id_stage) ON DELETE CASCADE,
 id_test_passage INT REFERENCES Test_passage(id_test_passage) ON DELETE CASCADE
);


