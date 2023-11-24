from flask import Flask, render_template, request, session, url_for, request, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'sample_secret'

def connectsql():
    conn = pymysql.connect(host='localhost', port=3306, user = 'root', passwd = '1234', db = 'test', charset='utf8')
    return conn

import graph1
import graph3

#임시(페이지 이동을 위한 페이지)
@app.route('/main')
def Main():
    return render_template('Main.html')

#로그아웃
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for(''))

#로그인
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        logininfo = request.form['id']
        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        value = (userid, userpw)
        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for row in data:
            data = row[0]
        
        if data:
            session['username'] = request.form['id']
            session['password'] = request.form['pw']
            return render_template('loginSuccess.html', logininfo = logininfo)
        else:
            return render_template('loginError.html')
    else:
        return render_template ('login.html')

#회원가입
@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        value = userid
        cursor.execute(query, value)
        data = (cursor.fetchall())
        if data:
            return render_template('registError.html') 
        else:
            query = "INSERT INTO users (username, password) values (%s, %s)"
            value = (userid, userpw)
            cursor.execute(query, value)
            data = cursor.fetchall()
            conn.commit()
            return render_template('registSuccess.html')
        cursor.close()
        conn.close()
    else:
        return render_template('regist.html')

#과소비알림페이지
@app.route('/alarm')
def Alarm():
    return render_template("Alarm.html")

#소비내역 추가 페이지
@app.route('/addspend')
def AddSpend():
    return render_template("AddSpend.html")

#상세 소비내역 페이지
@app.route('/spendlist')
def SpendList():
    return render_template("SpendList.html")


#목표예산이 없습니다 화면
@app.route('/')
def main():
    return render_template('goal1.html')

#목표예산 등록하면 이동
@app.route('/goal2')
def goal_registration():
    return render_template('goal2.html')

#목표예산 등록
@app.route('/set_budget', methods=['POST'])
def set_budget():
    budget = request.form.get('budgetAmount')

    # 여기에서 budget를 저장하거나 처리하는 로직을 추가할 수 있습니다.
    # 예를 들어, 데이터베이스에 저장하거나 세션에 저장할 수 있습니다.

    message = "목표 예산이 설정되었습니다."
    return render_template('goal2.html', message=message, budget=budget)  

#목표예산 등록 시 원그래프 화면
@app.route('/graph')
def circle_graph():

    Budget, Spent, budget_percentage=graph3.budget_data()
    circle_graph=graph3.display_budget()
    return render_template('budget.html', circle_graph=circle_graph, Budget=Budget, Spent=Spent, budget_percentage=budget_percentage)


@app.route('/index', methods=['GET', 'POST'])
def graph():
    df = graph1.load_data('C:/finchatbot/exdata.csv')
    category_avg=graph1.category_avg_for_last_3_months(df)
    graph = graph1.generate_graph(df)
    current_month_total_expense=graph1.calculate_current_month_total_expense(df)
    previous_3_months_total_expense = graph1.calculate_monthly_total_expense(df)
    exceeded_categories = graph1.find_exceeded_categories(df, category_avg)

    age_group=None
    comparison_graph = []
    exceeded_categories_avg = None

    if request.method == 'POST':
        age_group = request.form.get('age_group')  # 사용자가 선택한 연령대 (웹 페이지에서 설정)
        age_category_data = graph1.load_age_category_data(age_group)
        category_consume_current_month = graph1.category_consume_for_current_month(df)  # 이번 달 카테고리별 소비금액
        comparison_graph = graph1.generate_comparison_graph(age_category_data, category_consume_current_month)
        exceeded_categories_avg=graph1.find_exceeded_age_group(df,age_group)

    return render_template('index.html', graph=graph, current_month_total_expense=current_month_total_expense, previous_3_months_total_expense=previous_3_months_total_expense, exceeded_categories=exceeded_categories, age_group=age_group, comparison_graph=comparison_graph,exceeded_categories_avg=exceeded_categories_avg, results=[])



if __name__ == '__main__':
    app.run(debug=True)