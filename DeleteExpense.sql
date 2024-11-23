CREATE DEFINER=`root`@`localhost` PROCEDURE `DeleteExpense`(
    IN p_username VARCHAR(255),
    IN p_expense_id INT
)
BEGIN
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        SET @expense_id = p_expense_id;
        SET @table_name = p_username;

        SET @delete_sql = CONCAT('DELETE FROM `', @table_name, '` WHERE id = ?');

        PREPARE stmt FROM @delete_sql;
        EXECUTE stmt USING @expense_id;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END