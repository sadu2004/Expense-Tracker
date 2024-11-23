CREATE TABLE expense_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    expense_id INT,
    action VARCHAR(50),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);