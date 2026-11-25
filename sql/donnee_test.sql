-- ============================================================================
-- Jeu de données fictives pour l'entraînement aux requêtes SQL
-- Projet : Gestion des tests fonctionnels
-- ============================================================================

BEGIN;

-- Nettoyage optionnel des tables existantes et réinitialisation des séquences
TRUNCATE TABLE 
    Stage_passage, 
    Test_passage, 
    Requirement_test, 
    Stage, 
    Test, 
    Test_set, 
    Campaign, 
    Tester, 
    Plan, 
    Requirement 
RESTART IDENTITY CASCADE;

-- 1. Exigences logicielles (Requirement) - VARCHAR(20)
INSERT INTO Requirement (requirement_name, requirement_description) VALUES
('REQ-AUTH-01', 'Authentification utilisateur par identifiant et mot de passe sécurisé'),
('REQ-AUTH-02', 'Verrouillage du compte après 3 tentatives de connexion échouées'),
('REQ-CART-01', 'Ajout et suppression d articles dans le panier d achat'),
('REQ-CART-02', 'Calcul automatique des remises et de la TVA dans le panier'),
('REQ-PAY-01',  'Paiement par carte bancaire via passerelle sécurisée 3DS'),
('REQ-EXPORT-01', 'Export de l historique des commandes au format PDF');

-- 2. Plans de test (Plan) - VARCHAR(20) (correction : <= 20 caractères)
INSERT INTO Plan (plan_name) VALUES
('Plan_Auth'),
('Plan_Achat'),
('Plan_Facturation');

-- 3. Tests fonctionnels (Test) - VARCHAR(20)
INSERT INTO Test (test_name, test_description, condition_init, id_plan) VALUES
('TST_LOGIN_OK',    'Connexion réussie avec un compte actif valide', 100, 1),
('TST_LOGIN_LOCK',  'Blocage du compte après 3 mauvais mots de passe', 100, 1),
('TST_CART_ADD',    'Ajout de plusieurs produits et mise à jour des quantités', 200, 2),
('TST_CART_PROMO',  'Application d un code promotionnel de 10 pourcents', 201, 2),
('TST_PAY_CB',      'Validation d un paiement CB accepté', 300, 2),
('TST_PDF_EXPORT',  'Génération de la facture PDF après commande', 400, 3);

-- 4. Association Exigences <-> Tests (Requirement_test)
INSERT INTO Requirement_test (id_test, id_requirement) VALUES
(1, 1),
(2, 1),
(2, 2),
(3, 3),
(4, 3),
(4, 4),
(5, 5),
(6, 6);

-- 5. Étapes des tests (Stage) - VARCHAR(20)
INSERT INTO Stage (stage_name, stage_description, expectation, id_test) VALUES
('STG_1_1', 'Saisir un email et un mot de passe valides', 1, 1),
('STG_1_2', 'Cliquer sur le bouton Se connecter et vérifier la redirection', 200, 1),
('STG_2_1', 'Saisir 3 fois un mot de passe erroné', 401, 2),
('STG_2_2', 'Tenter une 4ème connexion avec le bon mot de passe', 403, 2),
('STG_3_1', 'Ajouter 2 articles distincts au panier', 2, 3),
('STG_3_2', 'Modifier la quantité du premier article à 3', 4, 3),
('STG_4_1', 'Entrer le code PROMO10 dans le champ dédié', 10, 4),
('STG_4_2', 'Vérifier le recalcul du montant TTC', 90, 4),
('STG_5_1', 'Renseigner les numéros de carte de test valide', 1, 5),
('STG_5_2', 'Valider le défi 3D-Secure', 200, 5),
('STG_6_1', 'Cliquer sur Télécharger la facture sur une commande payée', 200, 6);

-- 6. Campagnes de test (Campaign) - VARCHAR(20)
INSERT INTO Campaign (campaign_name, software_version, start_at, end_at) VALUES
('Campagne_v1.0', 100, '2026-09-01', '2026-09-10'),
('Campagne_v1.1', 110, '2026-10-05', '2026-10-15'),
('Campagne_v2.0', 200, '2026-11-10', NULL);

-- 7. Jeux de tests (Test_set)
INSERT INTO Test_set (type_test_set, id_campaign) VALUES
('Functional',     1),
('Non_regression', 1),
('Functional',     2),
('Non_regression', 2),
('Functional',     3),
('Non_regression', 3);

-- 8. Testeurs (Tester) - VARCHAR(20)
INSERT INTO Tester (tester_name) VALUES
('Alice Martin'),
('Bob Dupont'),
('Charlie Bernard'),
('Diane Leroy');

ALTER TABLE Test_passage DISABLE TRIGGER init_stage_passage;

-- 9. Passages de tests (Test_passage)
INSERT INTO Test_passage (test_passage_at, test_state, id_test_set, id_tester, id_test) VALUES
('2026-09-02', 'OK',      1, 1, 1),
('2026-09-03', 'KO',      1, 1, 2),
('2026-09-04', 'OK',      1, 2, 3),
('2026-09-05', 'KO',      1, 2, 4),
('2026-09-06', 'OK',      2, 3, 5),
('2026-10-06', 'OK',      4, 1, 1),
('2026-10-07', 'OK',      3, 1, 2),
('2026-10-08', 'OK',      3, 2, 4),
('2026-10-09', 'KO',      3, 4, 6),
('2026-11-12', 'OK',      6, 3, 1),
('2026-11-13', 'KO',      6, 2, 3),
('2026-11-15', 'WAITING', 5, 4, 6);

-- 10. Passages des étapes (Stage_passage) - VARCHAR(50)
INSERT INTO Stage_passage (state_stage, commentary, id_stage, id_test_passage) VALUES
('OK', 'Connexion fluide en moins de 1s', 1, 1),
('OK', 'Redirection tableau de bord conforme', 2, 1),
('OK', '3 erreurs bien détectées', 3, 2),
('KO', 'Le compte reste accessible au 4eme essai', 4, 2),
('OK', 'Articles bien ajoutés', 5, 3),
('OK', 'Total panier mis à jour', 6, 3),
('OK', 'Code promo reconnu', 7, 4),
('KO', 'Remise appliquée sur le TTC au lieu du HT', 8, 4),
('OK', 'Carte acceptée', 9, 5),
('OK', 'Validation 3DS réussie', 10, 5),
('OK', 'RAS', 1, 6),
('OK', 'RAS', 2, 6),
('OK', '3 tentatives bloquées', 3, 7),
('OK', 'Compte verrouillé pendant 15 min', 4, 7),
('OK', 'Code promo valide', 7, 8),
('OK', 'Calcul TVA et remise corrigés', 8, 8),
('KO', 'Timeout serveur lors de la génération PDF', 11, 9),
('OK', 'Authentification OK sur v2', 1, 10),
('OK', 'Session ouverte', 2, 10),
('OK', 'Ajout initial OK', 5, 11),
('KO', 'Quantité bloquée à 1 après rafraîchissement', 6, 11),
('WAITING', 'En attente de déploiement correctif', 11, 12);
ALTER TABLE Test_passage ENABLE TRIGGER init_stage_passage;
COMMIT;

