CREATE DEFINER=`root`@`localhost` PROCEDURE `GetCategories`(
    IN p_username VARCHAR(255)
)
BEGIN
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        SET @table_name = CONCAT(p_username, '_cat');

        SET @select_cat_sql = CONCAT('SELECT category FROM `', @table_name, '`');

        PREPARE stmt FROM @select_cat_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END