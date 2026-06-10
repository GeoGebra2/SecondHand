SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `favorite` (
  `favorite_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `product_id` BIGINT NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_favorite_user_product` (`user_id`, `product_id`),
  INDEX `idx_favorite_user` (`user_id`),
  INDEX `idx_favorite_product` (`product_id`),
  CONSTRAINT `fk_favorite_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_favorite_product`
    FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `notification` (
  `notification_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `receiver_id` BIGINT NOT NULL,
  `content` VARCHAR(255) NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_notification_receiver` (`receiver_id`),
  CONSTRAINT `fk_notification_receiver`
    FOREIGN KEY (`receiver_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE
);
