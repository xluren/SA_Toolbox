db_migrate for zabbix  from mysql 5.5 with innodb  to   Percona-Server 5.6 with tokudb
*   1.硬件磁盘阵列做好 done 
*   2.系统装好 done 
*   3.文件系统改成xfs  done 
*   4.数据库安装 引擎弄好 done  这里选择如下:

    ``[root@test procedure]# rpm -qa |grep -iE 'mysql|percona|toku'
    Percona-Server-server-56-5.6.21-rel70.1.el6.x86_64
    percona-release-0.1-3.noarch
    mysql-community-release-el6-5.noarch
    mysql-community-common-5.6.22-2.el6.x86_64
    Percona-Server-client-56-5.6.21-rel70.1.el6.x86_64
    Percona-Server-tokudb-56-5.6.21-rel70.1.el6.x86_64
    mysql-community-libs-5.6.22-2.el6.x86_64
    Percona-Server-shared-56-5.6.21-rel70.1.el6.x86_64```
*   5.mysql数据同步(最重要的).......
    需要准备的东西
    *   A.表结构 zabbix_init.sql
    *   B.存储过程 produce.sql 
    *   C.run.sh 主要执行脚本 time sh -x run.sh

    基本的思路：
    *   1.主库运行
    *   2.在新的机器上执行 sh -x run.sh 
        *   1.drop 老库如果存在的话，创建新库;
        *   2.初始化表结构,主要是部分表的引擎改为了tokudb,表上已经有一个默认的分区，很久之前
        *   3.创建procedure,call procedure 增加partition,history 默认36天，trends 默认718天
        *   4.导出原来机器上老库的数据库，然后导入到新库
        *   5.done
    *   3.trends* 表 慢慢的同步
*   7.zabbix_server 切数据库
    *   1.新库变主库
    *   2.老库变从库
    *   3.增加proxy,所有的读操作打到老库上面，所有的写操作到主库上面
    *   4.这样不影响原始数据的读操作;同时服务影响时间最小。
