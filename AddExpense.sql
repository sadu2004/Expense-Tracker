CREATE DEFINER=`root`@`localhost` PROCEDURE `AddExpense`(
    IN p_username VARCHAR(255),
    IN p_date_of_expense DATE,
    IN p_title VARCHAR(20),
    IN p_money INT
)
BEGIN
    -- Validate that p_username contains only allowed characters to prevent SQL injection
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        -- Assign parameters to user-defined session variables
        SET @p_date_of_expense = p_date_of_expense;
        SET @p_title = p_title;
        SET @p_money = p_money;
        SET @table_name = p_username;

        -- Build the SQL statement
        SET @insert_sql = CONCAT('INSERT INTO `', @table_name, '` (DATE_OF_EXPENSE, TITLE, MONEY) VALUES (?, ?, ?)');

        PREPARE stmt FROM @insert_sql;
        EXECUTE stmt USING @p_date_of_expense, @p_title, @p_money;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END