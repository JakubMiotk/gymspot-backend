-- MySQL migration: convert relations.client_id/trainer_id from users.id to persons.id.
-- Take a database backup and stop the backend before running this migration.
-- Rows without a matching Person are reported and will not be copied.

CREATE TABLE relations_person_ids (
    client_id INT NOT NULL,
    trainer_id INT NOT NULL,
    PRIMARY KEY (client_id, trainer_id),
    CONSTRAINT fk_rel_person_client_20260928
        FOREIGN KEY (client_id) REFERENCES persons (id),
    CONSTRAINT fk_rel_person_trainer_20260928
        FOREIGN KEY (trainer_id) REFERENCES persons (id)
) ENGINE=InnoDB;

INSERT INTO relations_person_ids (client_id, trainer_id)
SELECT client_person.id, trainer_person.id
FROM relations AS old_relation
JOIN persons AS client_person
    ON client_person.user_id = old_relation.client_id
JOIN persons AS trainer_person
    ON trainer_person.user_id = old_relation.trainer_id;

-- Review this count before switching tables. These relations lack a Person row
-- for at least one endpoint and cannot be represented using persons.id.
SELECT COUNT(*) AS relations_without_matching_person
FROM relations AS old_relation
LEFT JOIN persons AS client_person
    ON client_person.user_id = old_relation.client_id
LEFT JOIN persons AS trainer_person
    ON trainer_person.user_id = old_relation.trainer_id
WHERE client_person.id IS NULL OR trainer_person.id IS NULL;

-- Keep the old table as a rollback/archive copy until the application has been
-- verified against the migrated relations table.
RENAME TABLE
    relations TO relations_user_ids_backup,
    relations_person_ids TO relations;

-- Once the app is verified and the backup is no longer needed, remove it manually:
-- DROP TABLE relations_user_ids_backup;
