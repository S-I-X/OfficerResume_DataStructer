import psycopg2
import csv
import sys
import codecs
import pymysql

def getCon(database=None, user=None, password=None, host=None, port=5432):
    """
    :param database: 数据库名称
    :param user: 该数据库的使用者
    :param password: 密码
    :param host: 数据库地址
    :param port: 数据库链接的端口号
    :return: 返回数据库链接
    """
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    print("Connection successful.")
    return conn


def getConMySQL(database=None, user=None, password=None, host=None, port=3306):
    """
    :param database: 数据库名称
    :param user: 该数据库的使用者
    :param password: 密码
    :param host: 数据库地址
    :param port: 数据库链接的端口号
    :return: 返回数据库链接
    """
    connMy = pymysql.connect(db=database, user=user, passwd=password, host=host, port=port, charset="utf8")
    print("MySQL Connection successful.")
    return connMy


def get_org_list(loc, My_cur):
    # My_Connection = getConMySQL(database='demo', user='root', password='root', host='opsrv.mapout.lan')
    # My_cur = My_Connection.cursor()
    select_sql = "SELECT org FROM demo.org_standard_map WHERE loc = '{0}';"
    finish_select_sql = select_sql.format(loc)
    My_cur.execute(finish_select_sql)
    results = My_cur.fetchall()
    result_list = []
    for item in results:
        #print('..........................',item[0])
        result_list.append(item[0])
    # My_cur.close()
    # My_Connection.close()
    return result_list

def set_org_to_map(loc, org, My_Connection, My_cur):
    # My_Connection = getConMySQL(database='demo', user='root', password='root', host='opsrv.mapout.lan')
    # My_cur = My_Connection.cursor()
    insert_sql = "INSERT demo.org_standard_map(loc, org) VALUES('{0}', '{1}');"
    finish_select_sql = insert_sql.format(loc, org)
    My_cur.execute(finish_select_sql)
    My_Connection.commit()
    # My_cur.close()
    # My_Connection.close()


def get_con_cur():
    My_Connection = getConMySQL(database='demo', user='root', password='root', host='opsrv.mapout.lan')
    My_cur = My_Connection.cursor()
    return My_Connection, My_cur

def db_close(My_Connection, My_cur):
    My_Connection.close()
    My_cur.close()


