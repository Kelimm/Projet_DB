# Base de données relationnelle : Projet
## Conception du modèle MEA

Pour faciliter l'analyse du sujet et la construction du modèle MEA, on commence par créer un **dictionnaire de données**. Il recense toutes les informations importantes et nécessaires à la création du MEA.

Dans cette étape, on ne pense pas encore aux tables : on se concentre d'abord sur la **compréhension des informations**.

On fait donc une première analyse du texte pour :
- repérer les informations présentes dans le sujet,
- les classer dans différentes catégories.
![image](https://hackmd.io/_uploads/H1VFxL8Cfl.png)
![image 2](https://hackmd.io/_uploads/SyBce8ICzl.png)

## Dictionnaire de données

### 1. Jaune clair : Plan de test
1. id_plan
2. nom_plan

### 2. Bleu : Test
3. id_test
4. nom_test
5. description_test
6. condition_initiale

### 3. Vert : Campagne
7. id_campagne
8. nom_campagne
9. version_logiciel
10. date_debut
11. date_fin

### 4. Rouge clair : Exigence
12. id_exigence
13. nom_exigence
14. description_exigence

### 5. Rose : Étape
15. id_etape
16. nom_etape
17. description_etape
18. attendu

### 6. Jaune foncé : Testeur
19. id_testeur
20. nom_testeur

### 7. Gris : Jeu de tests
21. id_jeu_test
22. type_jeu_test

### 8. Violet : Passage de test
23. id_passage_test
24. date_passage_test
25. etat_test

### 9. Rouge foncé : Passage d'étape
26. id_passage_etape
27. etat_etape
28. commentaire## Dictionnaire de données

## Matrice des dépendances fonctionnelles

Une fois le dictionnaire créé, on remarque que les attributs se regroupent en plusieurs catégories. Dans chaque groupe, on choisit l'attribut le plus approprié, c'est-à-dire l'** identifiant ** car unique , et on l'utilise comme **colonne de la matrice des dépendances fonctionnelles**.

Les colonnes retenues sont :
- id_plan
- id_test
- id_campagne
- id_exigence
- id_etape
- id_testeur
- id_jeu
- id_passage_test
- id_passage_etape

On obtient ainsi la matrice des dépendances fonctionnelles suivante :
![image](https://hackmd.io/_uploads/BJxGS8L0fe.png)
## Simplification des DF

À partir de la matrice, on obtient un ensemble de dépendances fonctionnelles. On peut maintenant supprimer :
- les DF **réflexives** (A → A),
- les DF **transitives** (A → C si A → B et B → C).

### DF conservées 

| Source | DF conservées |
|---|---|
| 1 (id_plan) | 1→2 |
| 3 (id_test) | 3→1, 3→4, 3→5, 3→6 |
| 7 (id_campagne) | 7→8, 7→9, 7→10, 7→11 |
| 12 (id_exigence) | 12→13, 12→14 |
| 15 (id_etape) | 15→3, 15→16, 15→17, 15→18 |
| 19 (id_testeur) | 19→20 |
| 21 (id_jeu) | 21→7, 21→22 |
| 23 (id_passage_test) | 23→3, 23→19, 23→21, 23→24, 23→25 |
| 26 (id_passage_etape) | 26→15, 26→23, 26→27, 26→28 |

### Pourquoi on supprime les autres

- **3→2** : car 3→1 et 1→2.
- **15→4, 5, 6** : car 15→3.
- **21→8, 9, 10, 11** : car 21→7.
- **23→4, 5, 6** : car 23→3.
- **23→20** : car 23→19.
- **23→22** : car 26→15 (et 15→3).
- **26→16, 17, 18** : car 26→15.
- **26→19, 20, 21, 24, 25** : car 26→23.

Après cette suppression, on obtient une **matrice des DF doublement simplifiée**, qui sert de base à la construction du modèle MEA.

![image](https://hackmd.io/_uploads/ryJfjrvCGl.png)

## Construction du MEA avec Mokodo

À partir de la matrice des DF simplifiée, on construit le MCD dans Mokodo en appliquant les règles vues en cours.

### Règles utilisées

1. **Attribut source seul → entité**
   L'attribut source devient l'identifiant. Les attributs qu'il détermine deviennent ses propriétés.

2. **Source elementaire -> Source elementaire**
   A → B avec B identifiant d'une autre entité : association entre les deux entités, max 1 côté A, max n côté B.

3. **Source non elementaire → association n,m**
   (A, B) → C : creation d'un lien N,M entre A et B

4. **Aucun attribut ne détermine l'autre → association n,n**
   Max n des deux côtés, elel n'apparait pas dans la matrice il faut les trouvers en analysant le sujet.

5. **Cardinalités**
   - max : vient des DF
   - min : vient des règles de gestion de l'énoncé (0 = facultatif, 1 = obligatoire)


Ces deux associations n'ont pas de propriété.

### Choix des cardinalités minimales

Les min ne viennent pas des DF mais de l'énoncé :
- **EXIGENCE `0,N`** côté test : certaines exigences n'ont aucun test associé (Q 22 : « exigences qui ont au moins un test associé »).
- **TEST `1,N`** côté exigence : un test valide une ou plusieurs exigences.
- **TESTEUR `0,N`** : un testeur peut exister sans avoir encore passé de test (Q 17 et 18).
- **PASSAGE_TEST `1,1`** côté testeur : un passage est toujours réalisé par un testeur.
- **PASSAGE_TEST `0,N`** côté passage d'étape : un test « en cours » n'a pas encore toutes ses étapes passées (Q 20).
- **JEU_TEST `1,N`** côté test : un jeu rassemble au moins un test. Côté test, `0,N` : un test peut ne pas encore être dans un jeu.

On obtient donc le MEA suivant :
![MCD](https://hackmd.io/_uploads/Byv68CYAfx.svg)

> **Note :** pour l'instant, on garde des **noms pour les associations** afin de mieux comprendre le modèle. L'association n,n entre TEST et EXIGENCE se nomme `LIEN_TEST_EXIGENCE`, pareil pour les autres.

---

 ## Passage du modèle MEA vers les Tables en intention
 
Pour passer du MEA au modèle relationnel (les tables), on applique les règles suivantes.

## 1. Les entités

- Chaque entité devient une table.
- Son identifiant devient la **clé primaire**, et ses attributs deviennent les colonnes.

## 2. Les associations

Le choix dépend des cardinalités maximales.

- **Association N,M** : on crée une **table de liaison** entre les deux tables. Elle contient les clés étrangères des deux tables, et ces deux clés forment ensemble sa clé primaire.
- **Association 1,N** : la table du côté de cardinalité maximale **1** reçoit, en **clé étrangère**, la clé primaire de la table du côté **N**.
- **Association 1,1** : le choix est libre. En général, la table qui a le moins d'attributs reçoit, en clé étrangère, la clé primaire de celle qui en a le plus. La clé étrangère doit être déclarée `UNIQUE`, sinon on retombe sur un 1,N.


**Nous obtenons donc les tables suivantes :**
 ```
CAMPAGNE(*id_campagne, nom_campagne, version_logiciel, date_debut,date_fin)
JEU_TEST(*id_jeu_test,type_jeu_test,#id_campagne)
PASSAGE_TEST(*id_passage_test,date_passage_test,etat_test,#id_jeu_test,#id_testeur,#id_test)
TESTEUR(*id_testeur, nom_testeur)
PASSAGE_ETAPE(*id_etape,etat_etape,commentaire, #id_passage_test,#id_etape)
ETAPE(*id_etape, nom_etape, description_etape, attendu, #id_test)
TEST(*id_test,nom_test,description_test, condition_initial, #id_plan)
PLAN(*id_plan, nom_plan)
EXIGENCE-TEST(*(#id_exigence,#id_test))
EXIGENCE(*id_exigence,nom_exigence,description_exigence)

 ```
 
 
# passage a l'ordinateur 

## creation des tables et domaines(SQL)
        
Nous commençons par créer nos tables et deux domaines en sql 

``` sql
CREATE DOMAIN Type_state 
AS VARCHAR(7)
CHECK (VALUE IN ('OK', 'KO', 'WAITING'));

CREATE DOMAIN Test_set_type
AS VARCHAR(14)
CHECK (VALUE IN ('Non_regression', 'Functional'));

CREATE TABLE Requirement (
 id_requirement INT PRIMARY KEY,
 requirement_name VARCHAR(20),
 requirement_description VARCHAR(255)
 );

CREATE TABLE Plan (
 id_plan INT PRIMARY KEY,
 plan_name VARCHAR(20)
);

CREATE TABLE Test (
 id_test INT PRIMARY KEY,
 test_name VARCHAR(20),
 test_description VARCHAR(255),
 condition_init INT,
 id_plan INT REFERENCES Plan(id_plan) ON DELETE CASCADE
);

CREATE TABLE Requirement_test (
 id_test INT REFERENCES Test(id_test),
 id_requirement INT REFERENCES Requirement(id_requirement),
 PRIMARY KEY (id_test, id_requirement)
);

CREATE TABLE Stage (
 id_stage INT PRIMARY KEY,
 stage_name VARCHAR(20),
 stage_description VARCHAR(255),
 expectation INT, 
 id_test INT REFERENCES Test(id_test) ON DELETE CASCADE
);

CREATE TABLE Campaign (
 id_campaign INTEGER PRIMARY KEY,
 campaign_name VARCHAR(20),
 software_version INTEGER,
 start_at DATE,
 end_at DATE
);

CREATE TABLE Test_set (
 id_test_set INTEGER PRIMARY KEY,
 type_test_set Test_set_type,
 id_campaign INTEGER REFERENCES Campaign(id_campaign)
);

CREATE TABLE Tester (
 id_tester INTEGER PRIMARY KEY,
 tester_name VARCHAR(20)
);


CREATE TABLE Test_passage (
 id_test_passage INTEGER PRIMARY KEY,
 test_passage_at DATE,
 test_state Type_state DEFAULT 'WAITING',
 id_test_set INTEGER REFERENCES Test_set(id_test_set) ON DELETE CASCADE, -- Permet de repondre a la question Supprimer les resultats quand un jeu de test est supprimé
 id_tester INTEGER REFERENCES Tester(id_tester) ON DELETE SET NULL, -- Si un testeur quitte l'entreprise je garde l'historique de ses tests
 id_test INT REFERENCES Test(id_test) ON DELETE CASCADE -- Permet de repondre a la question Supprimer les resultats quand un jeu de test est supprimé
);

CREATE TABLE Stage_passage (
 id_stage_passage INT PRIMARY KEY,
 state_stage Type_state,
 commentary VARCHAR(50),
 id_stage INT REFERENCES Stage(id_stage) ON DELETE CASCADE,
 id_test_passage INT REFERENCES Test_passage(id_test_passage) ON DELETE CASCADE
);
```

## Identification des triggers nécessaires

Les tables étant créées, nous passons à la création des triggers. Pour déterminer lesquels sont nécessaires, nous relisons l'énoncé et repérons les termes comme « automatiquement » ou « en fonction de », qui indiquent qu'une donnée doit être mise à jour d'elle-même à la suite d'un ajout, d'une modification ou d'une suppression dans une autre table. Nous en retenons deux.

![image](https://hackmd.io/_uploads/SJWDGChAMe.png)

### Trigger 1 (vert) : initialisation des étapes d'un test passé


**Raisonnement :** quand un test est rattaché à une campagne, rien n'a encore été exécuté, mais chaque étape devra recevoir un résultat. Il faut donc créer automatiquement une ligne de résultat par étape du test, avec l'état initial « En attente ». C'est ce qui permet à un test d'être « en cours » avant d'être terminé.

**Événement déclencheur :**
- **Ajout** d'un test dans une campagne (`INSERT` sur `PASSAGE_TEST`) : création des lignes `PASSAGE_ETAPE` en « En attente ».


``` sql
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
```
### Trigger 2 (rouge) : calcul de l'état du test passé et de sa date de passage

**Raisonnement :** l'état d'un test passé est une donnée dérivée de l'état de ses étapes, il ne doit pas être saisi à la main. Chaque fois qu'un résultat d'étape change, l'état du test passé doit être recalculé :
- au moins une étape « Échoué » → **KO** ;
- sinon, au moins une étape « En attente » → **WAINTING** ;
- sinon (toutes « Passé ») → **OK**.

La date de passage est mise à jour dans le même trigger.

**Événement déclencheur** (sur `PASSAGE_ETAPE`, avec mise à jour de `PASSAGE_TEST`) :
- **Modification** du résultat (par exemple « En attente » → « Passé ») : recalcul de l'état et de la date.

``` SQL
CREATE OR REPLACE FUNCTION update_test_passage_state()
RETURNS TRIGGER AS $$
	DECLARE
		new_state Type_state;
		nb_ko int;
		nb_waiting INT;
	BEGIN
		/*compter les étapes raté de ce test passé*/
		SELECT COUNT(*) INTO nb_ko
    		FROM stage_passage
    		WHERE id_test_passage = NEW.id_test_passage
      		AND state_stage = 'KO';

    		/*compter les étapes en attente de ce test passé*/
       	  	SELECT COUNT(*) INTO nb_waiting
    		FROM stage_passage
    		WHERE id_test_passage = NEW.id_test_passage
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
        	      WHERE id_test_passage = NEW.id_test_passage;
    		ELSE
		      UPDATE test_passage
        	      SET test_state = new_state,
            	      test_passage_at = CURRENT_DATE
        	      WHERE id_test_passage = NEW.id_test_passage;
    		END IF;
		RETURN NEW;

	END;
	$$ LANGUAGE plpgsql;

CREATE TRIGGER update_test_passage_state
    AFTER UPDATE OF state_stage ON stage_passage
    FOR EACH ROW
EXECUTE FUNCTION update_test_passage_state();

```
