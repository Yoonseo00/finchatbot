import pymysql

conn=pymysql.connect(host='127.0.0.1', user='chaerin', password='1234', db='finchatbotdb', charset='utf8')

cur=conn.cursor()

query="select * from user"
cur.execute(query)
result=cur.fetchall()

print(result)