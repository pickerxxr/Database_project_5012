import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};SERVER=localhost;DATABASE = '
                      'Book_reader_db_liuyouzhe;InitialCatalog=dbo;UID=sa;PWD=123456')

cursor = conn.cursor()
if not cursor:
    raise(NameError, '数据库连接失败')



cursor.execute("""INSERT INTO NBA_players_test (player_id) VALUES(1)""")

row = cursor.execute("""SELECT * FROM NBA_players_test""").fetchall()

print(row)
