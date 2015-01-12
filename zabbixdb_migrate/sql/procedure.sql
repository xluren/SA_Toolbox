-- add_partition PROCEDURE
DELIMITER //
CREATE PROCEDURE `add_partition` (IN table_name VARCHAR(100), IN partition_name VARCHAR(100), IN partitin_datetime VARCHAR(1000))
BEGIN
    SET @sql_str=concat('alter table ',table_name, ' add  partition(PARTITION ', partition_name,' VALUES LESS THAN (UNIX_TIMESTAMP("',partitin_datetime,'")));');
    select @sql_str;
    PREPARE add_sql from @sql_str;
    execute add_sql;
END//
DELIMITER ;

-- delete_partition PROCEDURE
DELIMITER //
CREATE PROCEDURE `delete_partition` (IN table_name VARCHAR(100),IN partition_name VARCHAR(100))
BEGIN
    SET @sql_str=concat('alter table ',@table_name,' drop partition ', @partition_name);
    PREPARE drop_sql from @sql_str;
    SELECT drop_sql;
    execute drop_sql;
END//
DELIMITER ;

