USE bankdb;

-- HASHED PASSWORD IS Pass123$
INSERT INTO users (username, password, first_name, last_name, ssn, address, phone, status) VALUES
('jdoe', '$argon2id$v=19$m=65536,t=3,p=4$UpQAaUwimrLsmG1XrIXJQw$WnoTLTDtIV7NyARC8StuAOCJSA+BXWccwVvQg315G2Q', 'John', 'Doe', '123-45-6789', '123 Main St, NY', '(717) 555-1234', 'pending'),
('asmith', '$argon2id$v=19$m=65536,t=3,p=4$UpQAaUwimrLsmG1XrIXJQw$WnoTLTDtIV7NyARC8StuAOCJSA+BXWccwVvQg315G2Q', 'Alice', 'Smith', '987-65-4321', '456 Oak Ave, CA', '(717) 555-5678', 'pending'),
('bwayne', '$argon2id$v=19$m=65536,t=3,p=4$UpQAaUwimrLsmG1XrIXJQw$WnoTLTDtIV7NyARC8StuAOCJSA+BXWccwVvQg315G2Q', 'Bruce', 'Wayne', '111-22-3333', '1007 Mountain Dr, Gotham', '(717) 555-0000', 'pending');

-- HASHED PASSWORD IS Admin$$$
INSERT INTO admin (admin_id, username, password) VALUES
(1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$A+vUG+lNGvXFFB5s80hmDw$4yg2TugPD7SAqOuFgq0OUKoms+b3XcF3gVvtTifgicE');

INSERT INTO bank_accounts (account_number, user_id, balance) VALUES
(10001, 1, 0.00),
(10002, 2, 0.00),
(10003, 3, 0.00);

INSERT INTO cards (user_id, card_number, expiry_date, cvv) VALUES
(1, '4111 1111 1111 1111', '12/27', '123'),
(2, '5500 0000 0000 0004', '11/26', '456'),
(3, '3400 0000 0000 0091', '10/30', '789');

INSERT INTO cards (user_id, card_number, expiry_date, cvv) VALUES
(1, '4222 2222 2222 2222', '01/30', '1234');

SELECT * FROM admin;
SELECT * FROM bank_accounts;
SELECT * FROM cards;
SELECT * FROM users;

delete from cards where card_id = 13;
update users set status = 'approved' Where user_id = 2;

SELECT c.*, concat(u.first_name,' ',u.last_name) name FROM cards c JOIN users u USING (user_id) WHERE user_id = 1;