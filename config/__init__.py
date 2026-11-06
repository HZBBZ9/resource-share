# 当数据库使用 MySQL 时，用 PyMySQL 作为驱动（无需编译 mysqlclient）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
