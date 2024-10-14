-- ----------------------------------
-- Database Productivity 2
-- ----------------------------------
CREATE DATABASE IF NOT EXISTS `Productivity_2` DEFAULT CHARACTER SET utf8mb4;
USE `Productivity_2`;


-- ----------------------------------
-- Table "role"
-- ----------------------------------
CREATE TABLE IF NOT EXISTS role (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45),
    PRIMARY KEY (id)
);


-- ----------------------------------
-- Table "importance"
-- ----------------------------------
CREATE TABLE IF NOT EXISTS importance (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45),
    PRIMARY KEY (id)
);


-- ----------------------------------
-- Table "status"
-- ----------------------------------
CREATE TABLE IF NOT EXISTS status (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45),
    PRIMARY KEY (id)
);


-- ----------------------------------
-- Table "user"
-- ----------------------------------
CREATE TABLE IF NOT EXISTS user (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45),
    login VARCHAR(45) NOT NULL UNIQUE,
    password VARCHAR(30) NOT NULL,
    image MEDIUMBLOB,
    role_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (role_id) REFERENCES role (id)
);


-- ----------------------------------
-- Table "task"
-- ----------------------------------
CREATE TABLE IF NOT EXISTS task (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255),
    description TEXT(1000),
    importance_id INT NOT NULL,
    status_id INT NOT NULL,
    deadline DATETIME,
    user_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (importance_id) REFERENCES importance (id),
    FOREIGN KEY (status_id) REFERENCES status (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);