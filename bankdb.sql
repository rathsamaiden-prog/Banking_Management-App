CREATE DATABASE bankdb;
USE bankdb;

CREATE TABLE users (
    user_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    ssn VARCHAR(11) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(15),
    status VARCHAR(8) DEFAULT 'pending'
) ENGINE=InnoDB;

CREATE TABLE admin (
    admin_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE bank_accounts (
    account_number INT NOT NULL UNIQUE PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE cards (
    card_id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    card_number VARCHAR(16) NOT NULL,
    expiry_date VARCHAR(5) NOT NULL,
    ccv VARCHAR(4) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;





