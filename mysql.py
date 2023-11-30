import pymysql

def connectsql():
    conn = pymysql.connect(host='localhost', port=3306, user = 'root', passwd = '1234', db = 'test', charset='utf8')
    return conn