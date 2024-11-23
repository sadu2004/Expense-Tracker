CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateUser`(
    IN p_username VARCHAR(255),
    IN p_password_hash VARCHAR(255)
)
BEGIN
    -- Validate username
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        -- Insert into users table
        INSERT INTO users (username, password_hash) VALUES (p_username, p_password_hash);

        -- Create user's expense table
        SET @expense_table_sql = CONCAT(
            'CREATE TABLE `', p_username, '` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                DATE_OF_EXPENSE DATE,
                TITLE VARCHAR(20),
                MONEY INT
            )'
        );
        PREPARE stmt FROM @expense_table_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- Create user's category table
        SET @category_table_sql = CONCAT(
            'CREATE TABLE `', p_username, '_cat` (
                category VARCHAR(50)
            )'
        );
        PREPARE stmt FROM @category_table_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- Create trigger on user's expense table to log inserts
        SET @trigger_sql = CONCAT(
            'CREATE TRIGGER `', p_username, '_expense_insert` ',
            'AFTER INSERT ON `', p_username, '` ',
            'FOR EACH ROW ',
            'BEGIN ',
                'INSERT INTO expense_log (username, expense_id, action, action_time) ',
                'VALUES (\'', p_username, '\', NEW.id, \'INSERT\', NOW());',
            'END;'
        );
        PREPARE stmt FROM @trigger_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;  -- Corrected line

    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END