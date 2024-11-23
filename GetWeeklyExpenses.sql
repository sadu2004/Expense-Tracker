CREATE DEFINER=`root`@`localhost` PROCEDURE `GetWeeklyExpenses`(
    IN p_username VARCHAR(255)
)
BEGIN
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        SET @table_name = p_username;
        SET @select_weekly_sql = CONCAT(
            'SELECT TITLE, SUM(MONEY) AS TOTAL_EXPENSE FROM `', @table_name,
            '` WHERE DATE_OF_EXPENSE BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE() GROUP BY TITLE'
        );

        PREPARE stmt FROM @select_weekly_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END