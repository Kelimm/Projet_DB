CREATE DOMAIN Type_state 
AS VARCHAR(7)
CHECK (VALUE IN ('OK', 'KO', 'WAITING'));

CREATE DOMAIN Test_set_type
AS VARCHAR(14)
CHECK (VALUE IN ('Non_regression', 'Functional'));

CREATE TABLE Requirement (
    id_requirement SERIAL PRIMARY KEY,
    requirement_name VARCHAR(50) NOT NULL,
    requirement_description VARCHAR(255)
);

CREATE TABLE Plan (
    id_plan SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL
);

CREATE TABLE Test (
    id_test SERIAL PRIMARY KEY,
    test_name VARCHAR(50) NOT NULL,
    test_description VARCHAR(255),
    initial_condition VARCHAR(255),
    id_plan INT NOT NULL REFERENCES Plan(id_plan) ON DELETE CASCADE
);

CREATE TABLE Requirement_test (
    id_test INT REFERENCES Test(id_test) ON DELETE CASCADE,
    id_requirement INT REFERENCES Requirement(id_requirement) ON DELETE CASCADE,
    PRIMARY KEY (id_test, id_requirement)
);

CREATE TABLE Stage (
    id_stage SERIAL PRIMARY KEY,
    stage_name VARCHAR(50) NOT NULL,
    stage_description VARCHAR(255),
    expectation VARCHAR(255) NOT NULL, 
    id_test INT NOT NULL REFERENCES Test(id_test) ON DELETE CASCADE
);

CREATE TABLE Campaign (
    id_campaign SERIAL PRIMARY KEY,
    campaign_name VARCHAR(50) NOT NULL,
    software_version VARCHAR(20) NOT NULL,
    start_at DATE NOT NULL,
    end_at DATE
);

CREATE TABLE Test_set (
    id_test_set SERIAL PRIMARY KEY,
    type_test_set Test_set_type NOT NULL,
    id_campaign INT NOT NULL REFERENCES Campaign(id_campaign) ON DELETE CASCADE
);

CREATE TABLE Tester (
    id_tester SERIAL PRIMARY KEY,
    tester_name VARCHAR(50) NOT NULL
);

CREATE TABLE Test_passage (
    id_test_passage SERIAL PRIMARY KEY,
    test_passage_at TIMESTAMP,
    test_state Type_state NOT NULL DEFAULT 'WAITING',
    id_test_set INT NOT NULL REFERENCES Test_set(id_test_set) ON DELETE CASCADE,
    id_tester INT REFERENCES Tester(id_tester) ON DELETE SET NULL,
    id_test INT NOT NULL REFERENCES Test(id_test) ON DELETE CASCADE
);

CREATE TABLE Stage_passage (
    id_stage_passage SERIAL PRIMARY KEY,
    state_stage Type_state NOT NULL DEFAULT 'WAITING',
    commentary VARCHAR(255),
    id_stage INT NOT NULL REFERENCES Stage(id_stage) ON DELETE CASCADE,
    id_test_passage INT NOT NULL REFERENCES Test_passage(id_test_passage) ON DELETE CASCADE
);
