-- Idempotent: create notification table if it does not exist with the expected schema
-- This will ensure fresh clones (empty DB) have the notification table for the app.

CREATE TABLE IF NOT EXISTS notification (
  notification_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  receiver_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  is_read TINYINT(1) DEFAULT 0,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_notification_receiver (receiver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Note: foreign key to user.user_id is intentionally omitted here to avoid ordering issues
-- during initial initialization. Add FKs in a later, explicit migration if desired.
