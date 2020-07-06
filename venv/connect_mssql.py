# 数据库的工具汇总
import pyodbc

# 数据库的连接
def connect_mssql(user_id, user_pwd):
    try:
        conn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};'
                              'SERVER=localhost;'
                              'DATABASE = nba;'
                              'InitialCatalog=dbo;'
                              'UID=' + user_id + ';' + 'PWD=' + user_pwd)

        cursor = conn.cursor()
        return cursor
    except pyodbc.Error:
        print("连接失败")
    #
    # cursor.execute("""INSERT INTO NBA_players_test (player_id) VALUES(1)""")
    #
    # row = cursor.execute("""SELECT * FROM NBA_players_test""").fetchall()
    #
    # print(row)


def connect_directly():
    try:
        conn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};'
                              'SERVER=localhost;'
                              'DATABASE = nba;'
                              'InitialCatalog=dbo;'
                              'UID=' + 'sa' + ';' + 'PWD=' + '123456')

        cursor = conn.cursor()
        return cursor
    except pyodbc.Error:
        print("连接失败")


# 关闭连接
def close_conn(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except pyodbc.Error:
        print("数据库关闭错误")
    finally:
        cursor.close()
        conn.close()


