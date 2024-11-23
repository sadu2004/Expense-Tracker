CREATE DEFINER=`root`@`localhost` PROCEDURE `AddCategory`(
    IN p_username VARCHAR(255),
    IN p_category_name VARCHAR(50)
)
BEGIN
    IF p_username REGEXP '^[A-Za-z][A-Za-z0-9_]*$' THEN
        SET @p_category_name = p_category_name;
        SET @table_name = CONCAT(p_username, '_cat');

        SET @insert_cat_sql = CONCAT('INSERT INTO `', @table_name, '` (category) VALUES (?)');

        PREPARE stmt FROM @insert_cat_sql;
        EXECUTE stmt USING @p_category_name;
        DEALLOCATE PREPARE stmt;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username';
    END IF;
END