-- Fixes the live-schema mismatch behind:
-- FOREIGN KEY (trainer_id) REFERENCES users(id)
-- The running API now writes Person.id, but the existing relations table still
-- expects User.id. Back up the database and stop the backend before running.
-- MySQL 8+ script; old table is retained as relations_user_ids_backup.

DELIMITER //

DROP PROCEDURE IF EXISTS migrate_relations_to_person_ids//

CREATE PROCEDURE migrate_relations_to_person_ids()
BEGIN
    DECLARE unmatched_relations BIGINT DEFAULT 0;

    DROP TABLE IF EXISTS relations_person_ids;

    CREATE TABLE relations_person_ids (
        client_id INT NOT NULL,
        trainer_id INT NOT NULL,
        PRIMARY KEY (client_id, trainer_id),
        CONSTRAINT fk_rel_person_client_20260928
            FOREIGN KEY (client_id) REFERENCES persons (id),
        CONSTRAINT fk_rel_person_trainer_20260928
            FOREIGN KEY (trainer_id) REFERENCES persons (id)
    ) ENGINE=InnoDB;

    SELECT COUNT(*) INTO unmatched_relations
    FROM relations AS old_relation
    LEFT JOIN persons AS client_person
        ON client_person.user_id = old_relation.client_id
    LEFT JOIN persons AS trainer_person
        ON trainer_person.user_id = old_relation.trainer_id
    WHERE client_person.id IS NULL OR trainer_person.id IS NULL;

    IF unmatched_relations > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Relations migration stopped: some relation user IDs have no linked Person. Reconcile those rows, then rerun.';
    END IF;

    INSERT INTO relations_person_ids (client_id, trainer_id)
    SELECT client_person.id, trainer_person.id
    FROM relations AS old_relation
    JOIN persons AS client_person
        ON client_person.user_id = old_relation.client_id
    JOIN persons AS trainer_person
        ON trainer_person.user_id = old_relation.trainer_id;

    RENAME TABLE
        relations TO relations_user_ids_backup,
        relations_person_ids TO relations;
END//

DELIMITER ;

CALL migrate_relations_to_person_ids();
DROP PROCEDURE migrate_relations_to_person_ids;

-- Verify the API works, then remove the archived table manually if desired:
-- DROP TABLE relations_user_ids_backup;
