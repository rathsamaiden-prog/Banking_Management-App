USE bankdb;

INSERT INTO users (username, password, first_name, last_name, ssn, address, phone, status) VALUES
('jdoe', 'hashed_pw1', 'John', 'Doe', '123-45-6789', '123 Main St, NY', '555-1234', 'approved'),
('asmith', 'hashed_pw2', 'Alice', 'Smith', '987-65-4321', '456 Oak Ave, CA', '555-5678', 'approved'),
('bwayne', 'hashed_pw3', 'Bruce', 'Wayne', '111-22-3333', '1007 Mountain Dr, Gotham', '555-0000', 'pending');

INSERT INTO admin (admin_id, username, password) VALUES
(1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$s0rpGvRTf0JKgqfbvUNZug$/MCFfcCJW8tls2t9NinjmMw4IMexwmC6uolDOTEmxlA');

INSERT INTO bank_accounts (account_number, user_id, balance) VALUES
(100001, 1, 1500.75),
(100002, 2, 3200.50),
(100003, 3, 500.00);

INSERT INTO cards (user_id, card_number, expiry_date, ccv) VALUES
(1, '4111111111111111', '12/27', '123'),
(2, '5500000000000004', '11/26', '456'),
(3, '340000000000009', '10/25', '789');

SELECT * FROM admin;
SELECT * FROM bank_accounts;
SELECT * FROM cards;
SELECT * FROM users;

delete from users where user_id = 10;

delete from users where user_id = 2;