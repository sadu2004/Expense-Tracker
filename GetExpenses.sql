CREATE DEFINER=`root`@`localhost` PROCEDURE `GetExpenses`(
    IN p_username VARCHAR(255)
)
BEGIN
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        SET @table_name = p_username;

        SET @select_sql = CONCAT('SELECT id, DATE_OF_EXPENSE, TITLE, MONEY FROM `', @table_name, '`');

        PREPARE stmt FROM @select_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END