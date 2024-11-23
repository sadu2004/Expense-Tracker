DELIMITER //
CREATE TRIGGER AfterExpenseInsert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    SET @log_sql = CONCAT(
        'INSERT INTO expense_log (username, expense_id, action) VALUES (?, ?, ?)'
    );
    PREPARE stmt FROM @log_sql;
    SET @username = NEW.username;
    SET @expense_id = NEW.id;
    SET @action = 'INSERT';
    EXECUTE stmt USING @username, @expense_id, @action;
    DEALLOCATE PREPARE stmt;
END //
DELIMITER ;
