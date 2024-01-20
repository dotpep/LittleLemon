CREATE TABLE `Order`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `status` TINYINT(1) NOT NULL,
    `total` DECIMAL(8, 2) NOT NULL,
    `date` DATETIME NOT NULL,
    `user` BIGINT NULL,
    `delivery_crew` BIGINT NULL
);
ALTER TABLE
    `Order` ADD INDEX `order_status_date_index`(`status`, `date`);
ALTER TABLE
    `Order` ADD PRIMARY KEY `order_id_primary`(`id`);
ALTER TABLE
    `Order` ADD UNIQUE `order_user_unique`(`user`);
ALTER TABLE
    `Order` ADD UNIQUE `order_delivery_crew_unique`(`delivery_crew`);
CREATE TABLE `User`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `group` VARCHAR(255) NOT NULL
);
ALTER TABLE
    `User` ADD PRIMARY KEY `user_id_primary`(`id`);
CREATE TABLE `OrderItem`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(8, 2) NOT NULL,
    `price` DECIMAL(8, 2) NOT NULL,
    `order` BIGINT NULL,
    `menuitem` BIGINT NULL
);
ALTER TABLE
    `OrderItem` ADD PRIMARY KEY `orderitem_id_primary`(`id`);
ALTER TABLE
    `OrderItem` ADD UNIQUE `orderitem_order_unique`(`order`);
ALTER TABLE
    `OrderItem` ADD UNIQUE `orderitem_menuitem_unique`(`menuitem`);
CREATE TABLE `MenuItem`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `price` DECIMAL(8, 2) NOT NULL,
    `featured` TINYINT(1) NOT NULL,
    `category` BIGINT NULL
);
ALTER TABLE
    `MenuItem` ADD INDEX `menuitem_title_price_featured_index`(`title`, `price`, `featured`);
ALTER TABLE
    `MenuItem` ADD PRIMARY KEY `menuitem_id_primary`(`id`);
ALTER TABLE
    `MenuItem` ADD UNIQUE `menuitem_category_unique`(`category`);
CREATE TABLE `Cart`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(8, 2) NOT NULL,
    `price` DECIMAL(8, 2) NOT NULL,
    `user` BIGINT NULL,
    `menuitem` BIGINT NULL
);
ALTER TABLE
    `Cart` ADD PRIMARY KEY `cart_id_primary`(`id`);
ALTER TABLE
    `Cart` ADD UNIQUE `cart_user_unique`(`user`);
ALTER TABLE
    `Cart` ADD UNIQUE `cart_menuitem_unique`(`menuitem`);
CREATE TABLE `Category`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `slug` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NOT NULL
);
ALTER TABLE
    `Category` ADD INDEX `category_title_index`(`title`);
ALTER TABLE
    `Category` ADD PRIMARY KEY `category_id_primary`(`id`);
ALTER TABLE
    `OrderItem` ADD CONSTRAINT `orderitem_menuitem_foreign` FOREIGN KEY(`menuitem`) REFERENCES `Order`(`date`);
ALTER TABLE
    `Order` ADD CONSTRAINT `order_user_foreign` FOREIGN KEY(`user`) REFERENCES `User`(`username`);
ALTER TABLE
    `OrderItem` ADD CONSTRAINT `orderitem_menuitem_foreign` FOREIGN KEY(`menuitem`) REFERENCES `MenuItem`(`title`);
ALTER TABLE
    `Order` ADD CONSTRAINT `order_delivery_crew_foreign` FOREIGN KEY(`delivery_crew`) REFERENCES `User`(`group`);
ALTER TABLE
    `Cart` ADD CONSTRAINT `cart_menuitem_foreign` FOREIGN KEY(`menuitem`) REFERENCES `MenuItem`(`title`);
ALTER TABLE
    `Cart` ADD CONSTRAINT `cart_user_foreign` FOREIGN KEY(`user`) REFERENCES `User`(`username`);
ALTER TABLE
    `MenuItem` ADD CONSTRAINT `menuitem_category_foreign` FOREIGN KEY(`category`) REFERENCES `Category`(`title`);