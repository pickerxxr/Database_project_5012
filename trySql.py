import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};SERVER=localhost;DATABASE = Book_reader_db_liuyouzhe;InitialCatalog=dbo;UID=sa;PWD=***')

cur = conn.cursor()
if not cur:
    raise(NameError, '数据库连接失败')
re = cur.execute("SELECT 书号 FROM books_liuyouzhe").fetchall()
print(re)