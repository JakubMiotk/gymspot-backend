ALTER TABLE payments
ADD COLUMN IF NOT EXISTS type VARCHAR(50) NOT NULL DEFAULT 'payment';

UPDATE payments
SET type = 'payment'
WHERE type IS NULL OR type = '';