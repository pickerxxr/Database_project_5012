import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};SERVER=localhost;DATABASE = '
                      'Book_reader_db_liuyouzhe;InitialCatalog=dbo;UID=sa;PWD=123456')

cur = conn.cursor()
if not cur:
    raise(NameError, '数据库连接失败')
cur.execute("CREATE TABLE NBA_players_test(player_id int IDENTITY NOT NULL)")

test_result = cur.execute("SELECT * FROM NBA_players_test").fetchall()
print(test_result)