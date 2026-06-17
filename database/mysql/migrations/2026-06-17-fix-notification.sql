-- This script assumes the wrapper has detected an existing legacy `notification`
-- table and is invoking the migration to transform it to the new schema.

CREATE TABLE IF NOT EXISTS notification_new (
  notification_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  receiver_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  is_read TINYINT(1) DEFAULT 0,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_notification_receiver (receiver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copy data from legacy table into the new table (best-effort)
INSERT INTO notification_new (notification_id, receiver_id, content, is_read, create_time)
SELECT
  COALESCE(notification_id, msg_id, 0) AS notification_id,
  receiver_id,
  content,
  COALESCE(is_read, 0) AS is_read,
  COALESCE(create_time, NOW()) AS create_time
FROM notification
ORDER BY create_time ASC;

-- Fix AUTO_INCREMENT
SET @m := (SELECT MAX(notification_id) FROM notification_new);
SET @ai := IFNULL(@m, 0) + 1;
SET @s1 = CONCAT('ALTER TABLE notification_new AUTO_INCREMENT = ', @ai);
PREPARE pst1 FROM @s1; EXECUTE pst1; DEALLOCATE PREPARE pst1;

-- Backup old table if necessary
SET @has_backup := (
  SELECT COUNT(*) FROM information_schema.tables
  WHERE table_schema = DATABASE() AND table_name = 'notification_old'
);
IF (@has_backup = 1) THEN
  SET @r1 = 'RENAME TABLE notification_old TO notification_old_bak';
  PREPARE pr1 FROM @r1; EXECUTE pr1; DEALLOCATE PREPARE pr1;
END IF;

-- Atomically replace table
SET @r2 = 'RENAME TABLE notification TO notification_old, notification_new TO notification';
PREPARE pr2 FROM @r2; EXECUTE pr2; DEALLOCATE PREPARE pr2;

-- Note: do not add FK here to avoid cross-table ordering issues; add later if desired.
-- DROP TABLE notification_old;
