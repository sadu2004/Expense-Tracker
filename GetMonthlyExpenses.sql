CREATE DEFINER=`root`@`localhost` PROCEDURE `GetMonthlyExpenses`(
    IN p_username VARCHAR(255)
)
BEGIN
    -- Validate the username to prevent SQL injection
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        -- Set the table name
        SET @table_name = p_username;

        -- Construct the SQL query
        SET @select_monthly_sql = CONCAT(
            'SELECT TITLE, SUM(MONEY) AS TOTAL_EXPENSE FROM `', @table_name, '` ',
            'WHERE DATE_OF_EXPENSE BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE() ',
            'GROUP BY TITLE'
        );

        -- Prepare and execute the statement
        PREPARE stmt FROM @select_monthly_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    ELSE
        -- Handle invalid usernames
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END