SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `user` (
  `user_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `student_no` VARCHAR(20) NOT NULL UNIQUE,
  `user_name` VARCHAR(50) NOT NULL,
  `gender` VARCHAR(10) NULL,
  `phone` VARCHAR(20) NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'student',
  `credit_score` INT NOT NULL DEFAULT 100,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `verify_status` VARCHAR(20) NOT NULL DEFAULT 'verified',
  `avatar_url` VARCHAR(255) NULL,
  `bio` VARCHAR(255) NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login_time` DATETIME NULL,
  INDEX `idx_user_status` (`status`),
  INDEX `idx_user_verify_status` (`verify_status`)
);

CREATE TABLE IF NOT EXISTS `product` (
  `product_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `seller_id` BIGINT NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `description` TEXT NULL,
  `price` DECIMAL(10, 2) NOT NULL,
  `category_name` VARCHAR(50) NOT NULL,
  `trade_location` VARCHAR(100) NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'ON_SALE',
  `publish_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_product_seller` (`seller_id`),
  INDEX `idx_product_status` (`status`),
  CONSTRAINT `fk_product_seller`
    FOREIGN KEY (`seller_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `order_info` (
  `order_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `product_id` BIGINT NOT NULL,
  `buyer_id` BIGINT NOT NULL,
  `seller_id` BIGINT NOT NULL,
  `order_amount` DECIMAL(10, 2) NOT NULL,
  `order_status` VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  `trade_method` VARCHAR(20) NOT NULL DEFAULT 'offline',
  `trade_location` VARCHAR(100) NOT NULL,
  `buyer_note` VARCHAR(255) NULL,
  `cancel_reason` VARCHAR(255) NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `finish_time` DATETIME NULL,
  INDEX `idx_order_buyer_status` (`buyer_id`, `order_status`),
  INDEX `idx_order_seller_status` (`seller_id`, `order_status`),
  INDEX `idx_order_product` (`product_id`),
  CONSTRAINT `fk_order_product`
    FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_order_buyer`
    FOREIGN KEY (`buyer_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_order_seller`
    FOREIGN KEY (`seller_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `review` (
  `review_id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `order_id` BIGINT NOT NULL,
  `reviewer_id` BIGINT NOT NULL,
  `reviewed_user_id` BIGINT NOT NULL,
  `score` INT NOT NULL,
  `content` VARCHAR(255) NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_review_order` (`order_id`),
  INDEX `idx_review_reviewed_user` (`reviewed_user_id`),
  CONSTRAINT `fk_review_order`
    FOREIGN KEY (`order_id`) REFERENCES `order_info` (`order_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_review_reviewer`
    FOREIGN KEY (`reviewer_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_review_reviewed_user`
    FOREIGN KEY (`reviewed_user_id`) REFERENCES `user` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `chk_review_score` CHECK (`score` BETWEEN 1 AND 5)
);
