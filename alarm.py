import pymysql
import graph1

def badge():

    conn=pymysql.connect(host='127.0.0.1', user='root', password='1234', db='test', charset='utf8')
    cur=conn.cursor()

    budget_query = "SELECT budget FROM budget;" 
    cur.execute(budget_query)
    budget = cur.fetchone()


    df=graph1.load_data()
    total_expense=graph1.calculate_current_month_total_expense(df)


    if budget is not None:
        # budget이 None이 아닌 경우에만 적절한 인덱스로 접근
        badge_notification = total_expense > budget[0]


    # 연결 종료
    cur.close()
    conn.close()

    return badge_notification