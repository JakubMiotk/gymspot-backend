ALTER TABLE trainings
MODIFY COLUMN status ENUM(
    'planned',
    'completed',
    'canceled',
    'started',
    'missed',
    'completed_paid',
    'completed_unpaid'
) NOT NULL DEFAULT 'planned';

UPDATE trainings
SET status = 'completed_unpaid'
WHERE status = 'completed';

ALTER TABLE trainings
MODIFY COLUMN status ENUM(
    'planned',
    'started',
    'canceled',
    'missed',
    'completed_paid',
    'completed_unpaid'
) NOT NULL DEFAULT 'planned';

ALTER TABLE trainings
DROP COLUMN IF EXISTS is_paid;