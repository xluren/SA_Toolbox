#!/bin/bash 
source ./db.conf 



mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} -e "drop database ${new_db_name};create database ${new_db_name}; "
mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} ${new_db_name} < ./sql/zabbx_init.sql
mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} ${new_db_name} < ./sql/procedure.sql 

for table_name  in  ${hisroty}
do 
    mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} -e "use zabbix; alter table ${table_name} remove partitioning;"
    mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} -e "use zabbix;ALTER TABLE ${table_name} PARTITION BY RANGE(clock)(PARTITION p20120606 VALUES LESS THAN (1338912000) ENGINE = TokuDB);"
    for((j=${hisroty_days};j>=-2;j--))
    do
        partition_date=`date "+%Y-%m-%d" -d "${j} days ago"` 
        partition_name="P"`echo ${partition_date}|tr -d "-"`
        echo ${table_name} ${partition_name} ${partition_date}
        mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password}  -e "use zabbix; call add_partition(\"${table_name}\",\"${partition_name}\",\"${partition_date}\");"
    done 
done

for table_name  in  ${trends}
do 
    mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password}  -e "use zabbix; alter table ${table_name} remove partitioning;"
    mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password}  -e "use zabbix;ALTER TABLE ${table_name} PARTITION BY RANGE(clock)(PARTITION p20120606 VALUES LESS THAN (1338912000) ENGINE = TokuDB);"
    for((j=${trends_months};j>=-2;j--))
    do
        partition_date=`date "+%Y-%m-01" -d "${j} months ago"` 
        partition_name="P"`echo ${partition_date}|tr -d "-"`
        echo ${table_name} ${partition_name} ${partition_date}
        mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password}  -e "use zabbix; call add_partition(\"${table_name}\",\"${partition_name}\",\"${partition_date}\");"
    done 
done
sql_str=""
for ignore_table in ${ignore_table_list}
do 
    sql_str=$sql_str" --ignore-table=$ignore_table "
done 
mysqldump -h ${old_db_host} -u ${old_db_user} -p${old_db_password} ${old_db_name} -t ${sql_str} > ./hello.sql
mysql -h ${new_db_host} -u ${new_db_user} -p${new_db_password} ${new_db_name} < ./hello.sql
