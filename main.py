from flask import Flask, render_template, request, session, url_for, request, redirect
import pymysql
from flask_socketio import SocketIO
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'sample_secret'

def connectsql():
    conn = pymysql.connect(host='localhost', port=3306, user = 'root', passwd = '1234', db = 'test', charset='utf8')
    return conn

socketio=SocketIO(app)

import graph1
import graph3
import consume_report
import advicee
import counsell

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

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/report', methods=['GET'])
def report():

    selected_year = request.args.get('year')
    selected_month = request.args.get('month')

    selected_year = int(selected_year) if selected_year else 0
    selected_month = int(selected_month) if selected_month else 0

    df = graph1.load_data('C:/finchatbot/exdata.csv')

    selected_month_data = consume_report.monthly_spending(df, selected_year, selected_month)
    
    # 목표 예산 데이터 가져오기
    budget = graph3.budget_data()
    # 선택한 달의 카테고리별 소비 금액 계산 후 상위 3개 출력
    selected_month_top3 = consume_report.top3_categories_for_month(df, selected_year, selected_month)
    
    # 현재 달의 목표 예산 대비 추가 사용 계산
    additional_spending=selected_month_data - budget
    current_month_overspending_amount = additional_spending[0]

    if current_month_overspending_amount <= 0:
        current_month_overspending_amount = "0"



    return render_template('report.html',
                           selected_year=selected_year,
                           selected_month=selected_month,
                           selected_month_data=selected_month_data,
                           selected_month_top3=selected_month_top3,
                           current_month_overspending_amount=current_month_overspending_amount)


@app.route('/advice', methods=['GET'])
def advice():

    df = graph1.load_data('C:/finchatbot/exdata.csv')

    current_month_data=graph1.calculate_current_month_total_expense(df)
    current_category_data=graph1.category_consume_for_current_month(df)
    category_avg=graph1.category_avg_for_last_3_months(df)
    current_exceed_category=graph1.find_exceeded_categories(df, category_avg)

    user_message = "이번 달 소비 분석을 해주세요."
    socketio.start_background_task(target=generate_and_emit_advice_response, user_message=user_message, current_month_data=current_month_data, current_category_data=current_category_data, current_exceed_category=current_exceed_category)

    return render_template('advice.html', user_message=user_message)

def generate_and_emit_advice_response(user_message, current_month_data, current_category_data, current_exceed_category):
    system_message = advicee.generate_advice_response(user_message, current_month_data, current_category_data,
                                              current_exceed_category)
    socketio.emit('advice_response', {'system_message': system_message})

@app.route('/counsel', methods=['GET', 'POST'])
def counsel():

    if request.method == 'POST':
        user_message = request.form['user_input']
        print(f"Received user input: {user_message}")
        system_message = counsell.generate_counsel_response(user_message)
        print(f"Generated bot response: {system_message}")

         # 사용자에게 응답 메시지를 소켓을 통해 전송

        socketio.emit('user_input_response', {'bot_message': system_message}, namespace='/counsel')
        return render_template('counsel.html', user_message=user_message, system_message=system_message)

    # GET 요청에 대한 기본 응답 (페이지를 처음 열 때)
    initial_message = "안녕하세요. 저는 finchatbot이라고 합니다. 소비에 대한 분석과 관련된 지식과 정보를 제공할 수 있으며, 다양한 소비내역에 대해 분석할 수 있습니다.<br>또한 재테크와 절약에 대한 조언도 할 수 있으니 어떤 질문이든지 제게 물어보세요.<br>최선을 다해 도움을 드리도록 하겠습니다!"

    return render_template('counsel.html', initial_message=initial_message)

@app.route('/cardopt')
def index():
    return render_template('cardopt.html')

@app.route('/creditcard')
def show_credit_card():
    return render_template('creditcard.html')

@app.route('/checkcard')
def show_check_card():
    return render_template('checkcard.html')

@app.route('/selec1')
def show_selec_spend1():
    return render_template('selecspend_cre.html')

@app.route('/selec2')
def show_selec_spend2():
    return render_template('selecspend_chk.html')

# KoBERT 관련 설정
tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertModel.from_pretrained("monologg/kobert")

# KoBERT를 활용한 함수들
def embed_user_response(user_response):
    # 사용자 응답을 임베딩하는 함수
    tokens = tokenizer.batch_encode_plus(user_response, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    user_embedding = outputs.last_hidden_state.mean(dim=1)
    return user_embedding

def embed_card_benefits(card_benefits):
    # 카드 혜택을 임베딩하는 함수
    tokens = tokenizer.batch_encode_plus(card_benefits, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    card_embedding = outputs.last_hidden_state.mean(dim=1)
    return card_embedding

def calculate_similarity(embedding1, embedding2):
    # 유사도를 계산하는 함수
    return cosine_similarity(embedding1, embedding2)[0][0]

@app.route('/recom1')
def recom1():
    return render_template('recomcard_cre.html')

@app.route('/recom2')
def recom2():
    return render_template('recomcard_chk.html')

@app.route('/get_recommendation1', methods=['POST'])
def get_recommendation1():
    if request.method == 'POST':
        user_preference = request.form['user_preference']
        
        df = pd.read_csv('creditcard.csv')

        # 사용자 응답을 임베딩
        user_embedding = embed_user_response([user_preference])

        # embedded_card_data.csv 파일을 불러와 카드 혜택의 임베딩값을 저장
        card_data = pd.read_csv('C:/finchatbot/creditcard.csv')

        # 유사도 계산 및 추천
        best_match = None
        highest_similarity = 0.0

        for index, row in card_data.iterrows():
            card_embedding = embed_card_benefits([row['embedding']])
            similarity = calculate_similarity(card_embedding, user_embedding)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = row['카드명']
                
        matched_content = df[df['카드명'] == best_match]['내용'].values

        return render_template('recomcard_cre.html', recommendation=best_match, user_input=user_preference, matched_content=matched_content)
    
@app.route('/get_recommendation2', methods=['POST'])
def get_recommendation2():
    if request.method == 'POST':
        user_preference = request.form['user_preference']
        
        df = pd.read_csv('checkcard.csv')

        # 사용자 응답을 임베딩
        user_embedding = embed_user_response([user_preference])

        # embedded_card_data.csv 파일을 불러와 카드 혜택의 임베딩값을 저장
        card_data = pd.read_csv('C:/finchatbot/checkcard.csv')

        # 유사도 계산 및 추천
        best_match = None
        highest_similarity = 0.0

        for index, row in card_data.iterrows():
            card_embedding = embed_card_benefits([row['embedding']])
            similarity = calculate_similarity(card_embedding, user_embedding)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = row['카드명']
                
        matched_content = df[df['카드명'] == best_match]['내용'].values

        return render_template('recomcard_chk.html', recommendation=best_match, user_input=user_preference, matched_content=matched_content)

        


if __name__ == '__main__':
    socketio.run(app, debug=True)