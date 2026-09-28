-- Migration from account IDs (users.id) to domain IDs (persons.id).
-- Requires 20260928_relations_use_person_ids.sql to have been reviewed/applied.
-- Back up the database and stop the backend before running this migration.
--
-- Stage mapped copies first. Rows with no linked Person are omitted from staging;
-- review the orphan counts below and create/link Persons or reconcile those rows
-- before running the final RENAME TABLE statement.

CREATE TABLE trainings_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    trainer_id INT NOT NULL,
    client_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    training_date DATETIME NOT NULL,
    status ENUM('planned','started','canceled','missed','completed_paid','completed_unpaid') NOT NULL DEFAULT 'planned',
    note VARCHAR(255) NULL,
    KEY ix_trainings_person_ids_trainer (trainer_id),
    KEY ix_trainings_person_ids_client (client_id),
    CONSTRAINT fk_training_trainer_person_ids FOREIGN KEY (trainer_id) REFERENCES persons(id),
    CONSTRAINT fk_training_client_person_ids FOREIGN KEY (client_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO trainings_person_ids (id, trainer_id, client_id, created_at, training_date, status, note)
SELECT t.id, pt.id, pc.id, t.created_at, t.training_date, t.status, t.note
FROM trainings t
JOIN persons pt ON pt.user_id = t.trainer_id
JOIN persons pc ON pc.user_id = t.client_id;

CREATE TABLE measurements_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    date DATETIME NOT NULL,
    weight DECIMAL(4,1) NOT NULL,
    height SMALLINT NOT NULL,
    body_fat DECIMAL(3,1) NULL,
    visceral_fat TINYINT UNSIGNED NULL,
    fat_mass DECIMAL(4,1) NULL,
    muscle_mass DECIMAL(4,1) NULL,
    note VARCHAR(255) NULL,
    KEY ix_measurements_person_ids_person (person_id),
    CONSTRAINT fk_measurement_person_ids FOREIGN KEY (person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO measurements_person_ids (id, person_id, date, weight, height, body_fat, visceral_fat, fat_mass, muscle_mass, note)
SELECT m.id, p.id, m.date, m.weight, m.height, m.body_fat, m.visceral_fat, m.fat_mass, m.muscle_mass, m.note
FROM measurements m JOIN persons p ON p.user_id = m.user_id;

CREATE TABLE payments_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    from_person_id INT NOT NULL,
    to_person_id INT NOT NULL,
    date DATETIME NOT NULL,
    value INT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'payment',
    KEY ix_payments_person_ids_from (from_person_id),
    KEY ix_payments_person_ids_to (to_person_id),
    CONSTRAINT fk_payment_from_person_ids FOREIGN KEY (from_person_id) REFERENCES persons(id),
    CONSTRAINT fk_payment_to_person_ids FOREIGN KEY (to_person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO payments_person_ids (id, from_person_id, to_person_id, date, value, type)
SELECT x.id, pf.id, pt.id, x.date, x.value, x.type
FROM payments x
JOIN persons pf ON pf.user_id = x.from_user_id
JOIN persons pt ON pt.user_id = x.to_user_id;

CREATE TABLE debts_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    value INT NOT NULL,
    KEY ix_debts_person_ids_person (person_id),
    CONSTRAINT fk_debt_person_ids FOREIGN KEY (person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO debts_person_ids (id, person_id, value)
SELECT d.id, p.id, d.value FROM debts d JOIN persons p ON p.user_id = d.user_id;

CREATE TABLE excess_payments_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    value INT NOT NULL,
    KEY ix_excess_person_ids_person (person_id),
    CONSTRAINT fk_excess_person_ids FOREIGN KEY (person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO excess_payments_person_ids (id, person_id, value)
SELECT e.id, p.id, e.value FROM excess_payments e JOIN persons p ON p.user_id = e.user_id;

CREATE TABLE documentation_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    exercise_name VARCHAR(255) NOT NULL,
    exercise_description TEXT NULL,
    exercise_video VARCHAR(255) NULL,
    exercise_type VARCHAR(45) NULL,
    exercise_body_parts VARCHAR(255) NULL,
    author_person_id INT NOT NULL,
    KEY ix_documentation_person_ids_author (author_person_id),
    CONSTRAINT fk_documentation_author_person_ids FOREIGN KEY (author_person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO documentation_person_ids (id, exercise_name, exercise_description, exercise_video, exercise_type, exercise_body_parts, author_person_id)
SELECT d.id, d.exercise_name, d.exercise_description, d.exercise_video, d.exercise_type, d.exercise_body_parts, p.id
FROM documentation d JOIN persons p ON p.user_id = d.author;

CREATE TABLE push_subscriptions_person_ids (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    endpoint VARCHAR(512) NOT NULL,
    p256dh VARCHAR(255) NOT NULL,
    auth VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_push_person_ids_endpoint (endpoint),
    KEY ix_push_person_ids_person (person_id),
    CONSTRAINT fk_push_person_ids_person FOREIGN KEY (person_id) REFERENCES persons(id)
) ENGINE=InnoDB;
INSERT INTO push_subscriptions_person_ids (id, person_id, endpoint, p256dh, auth, created_at, updated_at)
SELECT s.id, p.id, s.endpoint, s.p256dh, s.auth, s.created_at, s.updated_at
FROM push_subscriptions s JOIN persons p ON p.user_id = s.user_id;

-- PRE-FLIGHT: every count below must be zero before proceeding.
SELECT 'trainings' AS table_name, COUNT(*) AS orphan_rows
FROM trainings t LEFT JOIN persons pc ON pc.user_id = t.client_id LEFT JOIN persons pt ON pt.user_id = t.trainer_id
WHERE pc.id IS NULL OR pt.id IS NULL
UNION ALL
SELECT 'measurements', COUNT(*) FROM measurements m LEFT JOIN persons p ON p.user_id = m.user_id WHERE p.id IS NULL
UNION ALL
SELECT 'payments', COUNT(*) FROM payments x LEFT JOIN persons pf ON pf.user_id = x.from_user_id LEFT JOIN persons pt ON pt.user_id = x.to_user_id WHERE pf.id IS NULL OR pt.id IS NULL
UNION ALL
SELECT 'debts', COUNT(*) FROM debts d LEFT JOIN persons p ON p.user_id = d.user_id WHERE p.id IS NULL
UNION ALL
SELECT 'excess_payments', COUNT(*) FROM excess_payments e LEFT JOIN persons p ON p.user_id = e.user_id WHERE p.id IS NULL
UNION ALL
SELECT 'documentation', COUNT(*) FROM documentation d LEFT JOIN persons p ON p.user_id = d.author WHERE p.id IS NULL
UNION ALL
SELECT 'push_subscriptions', COUNT(*) FROM push_subscriptions s LEFT JOIN persons p ON p.user_id = s.user_id WHERE p.id IS NULL;

-- Compare staged row counts with originals; do not continue if any differ.
SELECT 'trainings' AS table_name, (SELECT COUNT(*) FROM trainings) AS old_rows, (SELECT COUNT(*) FROM trainings_person_ids) AS staged_rows
UNION ALL SELECT 'measurements', (SELECT COUNT(*) FROM measurements), (SELECT COUNT(*) FROM measurements_person_ids)
UNION ALL SELECT 'payments', (SELECT COUNT(*) FROM payments), (SELECT COUNT(*) FROM payments_person_ids)
UNION ALL SELECT 'debts', (SELECT COUNT(*) FROM debts), (SELECT COUNT(*) FROM debts_person_ids)
UNION ALL SELECT 'excess_payments', (SELECT COUNT(*) FROM excess_payments), (SELECT COUNT(*) FROM excess_payments_person_ids)
UNION ALL SELECT 'documentation', (SELECT COUNT(*) FROM documentation), (SELECT COUNT(*) FROM documentation_person_ids)
UNION ALL SELECT 'push_subscriptions', (SELECT COUNT(*) FROM push_subscriptions), (SELECT COUNT(*) FROM push_subscriptions_person_ids);

-- Run only after all orphan and row-count checks are reconciled.
-- Existing dependent tables reference training/payment IDs, which are preserved.
RENAME TABLE
    trainings TO trainings_user_ids_backup,
    trainings_person_ids TO trainings,
    measurements TO measurements_user_ids_backup,
    measurements_person_ids TO measurements,
    payments TO payments_user_ids_backup,
    payments_person_ids TO payments,
    debts TO debts_user_ids_backup,
    debts_person_ids TO debts,
    excess_payments TO excess_payments_user_ids_backup,
    excess_payments_person_ids TO excess_payments,
    documentation TO documentation_user_ids_backup,
    documentation_person_ids TO documentation,
    push_subscriptions TO push_subscriptions_user_ids_backup,
    push_subscriptions_person_ids TO push_subscriptions;

-- RENAME TABLE updates existing foreign-key targets to the *_user_ids_backup tables.
-- Repoint dependent rows to the replacement tables (IDs were preserved above).
ALTER TABLE measurements_segmental_fat
    DROP FOREIGN KEY measurements_segmental_fat_ibfk_1,
    ADD CONSTRAINT fk_segmental_fat_measurement_person_ids
        FOREIGN KEY (measurement_id) REFERENCES measurements (id);
ALTER TABLE measurements_segmental_fat_free
    DROP FOREIGN KEY measurements_segmental_fat_free_ibfk_1,
    ADD CONSTRAINT fk_segmental_fat_free_measurement_person_ids
        FOREIGN KEY (measurement_id) REFERENCES measurements (id);
ALTER TABLE training_exercises
    DROP FOREIGN KEY training_exercises_ibfk_1,
    ADD CONSTRAINT fk_training_exercises_training_person_ids
        FOREIGN KEY (training_id) REFERENCES trainings (id);
ALTER TABLE exercises
    DROP FOREIGN KEY exercises_ibfk_1,
    ADD CONSTRAINT fk_exercise_documentation_person_ids
        FOREIGN KEY (documented_exercise_id) REFERENCES documentation (id);

-- Keep *_user_ids_backup tables until the application has been verified.
-- The old relations table backup from 20260928_relations_use_person_ids.sql can
-- also be removed only after validation.
