from flask import Flask, render_template, request, session, url_for, request, redirect, jsonify
import pymysql
from flask_socketio import SocketIO
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from flask import jsonify
from flask_bcrypt import Bcrypt

import graph1
import graph3
import consume_report
import advicee
import counsell
import alarm

def connectsql():
    conn = pymysql.connect(host='localhost', port=3306, user = 'root', passwd = '1234', db = 'test', charset='utf8')
    return conn

app = Flask(__name__)
app.secret_key = 'sample_secret'

bcrypt = Bcrypt(app)
socketio=SocketIO(app)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 로그인 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (userid,))
        user_data = cursor.fetchone()

        if bcrypt.check_password_hash(user_data['password'], userpw):
            session['username'] = user_data['username']

            conn = connectsql()
            cursor = conn.cursor()

            # 사용자의 목표 예산 여부 확인 쿼리
            query = "SELECT * FROM budget WHERE username = %s"
            cursor.execute(query, (session['username'],))
            budget_data = cursor.fetchall()

            cursor.close()
            conn.close()

            if budget_data:
                return redirect(url_for('set_budget'))
            else:
                return redirect(url_for('goal1'))
        else:
            return render_template('loginError.html')

    return render_template('login.html')

@app.route('/goal1')
def goal1():
    if 'username' in session:
        userid = session['username']
        return render_template('goal1.html', logininfo = userid)
    else:
        return render_template('loginError.html')

@app.route('/goal2')
def goal2():
    if 'username' in session:
        userid = session['username']
        return render_template('goal2.html', logininfo = userid)
    else:
        return render_template('loginError.html')

@app.route('/graph', methods=['GET','POST'])
def set_budget():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            conn = connectsql()
            cursor = conn.cursor()
            query = "SELECT * FROM budget WHERE username = %s"
            cursor.execute(query, (username,))
            data = cursor.fetchall()
            cursor.close()
            conn.close()
        
        for row in data:
            data = row[0]
        
        if data:
            Budget, Spent, budget_percentage=graph3.budget_data()
            circle_graph=graph3.display_budget()
            return render_template ('budget.html', circle_graph=circle_graph, Budget=Budget, Spent=Spent, budget_percentage=budget_percentage, logininfo = userid)
        else:
            userid = session['username']
            setbudget= request.form['budgetAmount']

            conn = connectsql()
            cursor = conn.cursor() 
            query = "INSERT INTO budget (username, budget) values (%s, %s)"
            value = (userid, setbudget)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()
            Budget, Spent, budget_percentage=graph3.budget_data()
            circle_graph=graph3.display_budget()
            return render_template('budget.html', circle_graph=circle_graph, Budget=Budget, Spent=Spent, budget_percentage=budget_percentage)
    else:
        if 'username' in session:
            userid = session['username']
            Budget, Spent, budget_percentage=graph3.budget_data()
            circle_graph=graph3.display_budget()
            return render_template ('budget.html', circle_graph=circle_graph, Budget=Budget, Spent=Spent, budget_percentage=budget_percentage, logininfo = userid)
        else:
            return render_template ('Error.html')

MIN_PASSWORD_LENGTH = 8
@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']
        userpw_confirm = request.form['pw_confirm']

        if userpw != userpw_confirm:
            return render_template('registpw.html')

        # 비밀번호 길이 체크
        if len(userpw) < MIN_PASSWORD_LENGTH:
            return render_template('shortpw.html')
        
        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        value = userid
        cursor.execute(query, value)
        data = cursor.fetchall()
        if data:
            return render_template('registError.html') 
        else:
            pw_hash = bcrypt.generate_password_hash(userpw).decode('utf-8')
            query = "INSERT INTO users (username, password) values (%s, %s)"
            value = (userid, pw_hash)
            cursor.execute(query, value)
            data = cursor.fetchall()
            conn.commit()
            return render_template('registSuccess.html', pw_hash=pw_hash)
        cursor.close()
        conn.close()
    else:
        return render_template('regist.html')       

#소비내역 추가 페이지
@app.route('/addspend', methods=['GET', 'POST'])
def addspend():
    if request.method == 'POST':
        if 'username' in session:
            userid = session['username']
            
            date = request.form['date']
            category = request.form['category']
            price = request.form['price']
            place = request.form['place']

            conn = connectsql()
            cursor = conn.cursor() 
            query = "INSERT INTO addspend (username, add_date, add_category, add_price, add_place) values (%s, %s, %s, %s, %s)"
            value = (userid, date, category, price, place)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('addspend'))
        else:
            return render_template('errorpage.html')
    else:
        if 'username' in session:
            username = session['username']
            return render_template ('AddSpend.html', logininfo = username)
        else:
            return render_template ('Error.html')

@app.route('/spendlist', methods=['GET', 'POST'])
def spendlist():
    if 'username' in session:
        username = session['username']
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT username, add_date, add_category, add_price, add_place FROM addspend WHERE username = %s ORDER BY add_date DESC"
        cursor.execute(query, (username,))
        data_list = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        conn = connectsql()
        cursor = conn.cursor() 
        query = "SELECT SUM(add_price) AS totalsum FROM addspend WHERE username = %s"
        cursor.execute(query, (username,))
        total_price = cursor.fetchall()[0][0]

        conn.commit()
        cursor.close()
        conn.close()
        return render_template('SpendList.html', datalist = data_list, total_price=total_price, logininfo=username)
    else:
        return render_template ('Error.html')
    
@app.route('/select', methods=['GET', 'POST'])
def select():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            category = request.form['category']

            conn = connectsql()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            query = "SELECT username, add_date, add_category, add_price, add_place FROM addspend WHERE username = %s AND add_category = %s ORDER BY add_date DESC"
            cursor.execute(query, (username, category))
            data_list = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()

            conn = connectsql()
            cursor = conn.cursor(pymysql.cursors.DictCursor) 
            query = "SELECT SUM(add_price) AS sum FROM addspend WHERE username = %s AND add_category = %s"
            cursor.execute(query, (username, category))
            result = cursor.fetchall()
            if result and result[0]['sum'] is not None:
                price = result[0]['sum']
            else:
                price = 0
            cursor.close()
            conn.close()

            return render_template('select.html', datalist=data_list, category=category, price=price, logininfo=username)

        else:
            return render_template('Error.html')  # 세션에 사용자 이름이 없는 경우 에러 템플릿 렌더링
    else:
        return render_template('Error.html')  # GET 요청의 경우 에러 템플릿 렌더링

@app.route('/index', methods=['GET', 'POST'])
def graph():

    badge_notification=alarm.badge()

    df = graph1.load_data()
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

    df = graph1.load_data()

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

    df = graph1.load_data()

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

@app.route('/counsel')
def counsel():
    initial_message = "안녕하세요. 저는 머니버디라고 합니다. 소비에 대한 분석과 관련된 지식과 정보를 제공할 수 있으며, 다양한 소비내역에 대해 분석할 수 있습니다. 또한 재테크와 절약에 대한 조언도 할 수 있으니 어떤 질문이든지 제게 물어보세요. 최선을 다해 도움을 드리도록 하겠습니다!"
    return render_template('counsel.html', initial_message=initial_message)


@app.route('/get_response', methods=['POST'])
def get_response():

    user_message = request.form['user_message']
    print(f"Received user message: {user_message}")
    bot_response= counsell.generate_counsel_response(user_message)
    print(f"Generated bot response: {bot_response}")
    return jsonify({'user_message': user_message, 'bot_response': bot_response})



@app.route('/cardopt')
def index():
    return render_template('cardopt.html')

@app.route('/creditcard')
def show_credit_card():
    return render_template('selecspend_cre.html')

@app.route('/checkcard')
def show_check_card():
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

# 카드 저장 함수
def save_to_mysql1(user_choice):
    conn = connectsql()
    cursor = conn.cursor()
    
    delete_sql = "DELETE FROM cre_data"
    cursor.execute(delete_sql)

    # CSV 파일 읽기
    df = pd.read_csv('creditcard.csv')

    # 사용자가 선택한 금액 범위에 따른 '기준실적' 열 필터링
    if user_choice == 'under_300000':
        filtered_data = df[df['기준실적'] < 300000][['카드명', '내용', 'embedding']]
    elif user_choice == '300000_400000':
        filtered_data = df[(df['기준실적'] < 400000)][['카드명', '내용', 'embedding']]
    elif user_choice == '400000_500000':
        filtered_data = df[(df['기준실적'] < 500000)][['카드명', '내용', 'embedding']]
    else:
        filtered_data = df[df['기준실적'] >= 500000][['카드명', '내용', 'embedding']]


    # MySQL에 데이터 저장
    for index, row in filtered_data.iterrows():
        card_name = row['카드명']
        card_content = row['내용']
        card_embedding = row['embedding']
        
        sql = "INSERT INTO cre_data (card_name, card_content, card_embedding) VALUES (%s, %s, %s)"
        val = (card_name, card_content, card_embedding)
        cursor.execute(sql, val)

    conn.commit()
    
def save_to_mysql2(user_choice):
    conn = connectsql()
    cursor = conn.cursor()
    
    delete_sql = "DELETE FROM chk_data"
    cursor.execute(delete_sql)

    # CSV 파일 읽기
    df = pd.read_csv('checkcard.csv')

    # 사용자가 선택한 금액 범위에 따른 '기준실적' 열 필터링
    if user_choice == 'under_300000':
        filtered_data = df[df['기준실적'] < 300000][['카드명', '내용', 'embedding']]
    elif user_choice == '300000_400000':
        filtered_data = df[(df['기준실적'] < 400000)][['카드명', '내용', 'embedding']]
    elif user_choice == '400000_500000':
        filtered_data = df[(df['기준실적'] < 500000)][['카드명', '내용', 'embedding']]
    else:
        filtered_data = df[df['기준실적'] >= 500000][['카드명', '내용', 'embedding']]


    # MySQL에 데이터 저장
    for index, row in filtered_data.iterrows():
        card_name = row['카드명']
        card_content = row['내용']
        card_embedding = row['embedding']
        
        sql = "INSERT INTO chk_data (card_name, card_content, card_embedding) VALUES (%s, %s, %s)"
        val = (card_name, card_content, card_embedding)
        cursor.execute(sql, val)

    conn.commit()


# 카드 필터링 및 저장 후 recomcard_cre.html로 이동
@app.route('/filter_cards1', methods=['POST'])
def filter_cards1():
    if request.method == 'POST':
        # 사용자가 선택한 데이터
        user_choice = request.form['card_amount']

        # 데이터 저장 함수 호출
        save_to_mysql1(user_choice)
        
        # recomcard_cre.html로 이동
        return render_template('recomcard_cre.html')
    
@app.route('/filter_cards2', methods=['POST'])
def filter_cards2():
    if request.method == 'POST':
        # 사용자가 선택한 데이터
        user_choice = request.form['card_amount']

        # 데이터 저장 함수 호출
        save_to_mysql2(user_choice)
        
        # recomcard_cre.html로 이동
        return render_template('recomcard_chk.html')


@app.route('/get_recommendation1', methods=['POST'])
def recommend_cards1():
    if request.method == 'POST':
        user_preference = request.form['user_preference']
        conn = connectsql()
        cursor = conn.cursor()

        # MySQL에서 저장된 데이터 가져오기
        sql = "SELECT * FROM cre_data"
        cursor.execute(sql)
        filtered_data = cursor.fetchall()

        user_embedding = embed_user_response([user_preference])

        best_match = None
        highest_similarity = 0.0

        for data in filtered_data:
            # 데이터베이스에서 가져온 문자열 데이터를 벡터로 변환
            card_embedding_str = data[2]
            card_embedding = embed_card_benefits([card_embedding_str])

            # 유사도 계산
            similarity = calculate_similarity(card_embedding, user_embedding)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = data[0]

        matched_content = next((data[1] for data in filtered_data if data[0] == best_match), None)

        return render_template('recomcard_cre.html', recommendation=best_match, user_input=user_preference, matched_content=matched_content)
    
@app.route('/get_recommendation2', methods=['POST'])
def recommend_cards2():
    if request.method == 'POST':
        user_preference = request.form['user_preference']
        conn = connectsql()
        cursor = conn.cursor()

        # MySQL에서 저장된 데이터 가져오기
        sql = "SELECT * FROM chk_data"
        cursor.execute(sql)
        filtered_data = cursor.fetchall()

        user_embedding = embed_user_response([user_preference])

        best_match = None
        highest_similarity = 0.0

        for data in filtered_data:
            # 데이터베이스에서 가져온 문자열 데이터를 벡터로 변환
            card_embedding_str = data[2]
            card_embedding = embed_card_benefits([card_embedding_str])

            # 유사도 계산
            similarity = calculate_similarity(card_embedding, user_embedding)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = data[0]

        matched_content = next((data[1] for data in filtered_data if data[0] == best_match), None)

        return render_template('recomcard_chk.html', recommendation=best_match, user_input=user_preference, matched_content=matched_content)

#과소비알림페이지
@app.route('/alarm')
def Alarm():

    badge_notification=alarm.badge()

    if badge_notification:
        message = "해당 월의 목표 예산을 초과했습니다.\n\n챗봇에게 조언을 구해보세요!"
        html_message = message.replace('\n', '<br>')
    else:
        message = "예산에 맞게 아껴쓰고 있어요.\n\n궁금한 점이 있다면 챗봇에게 조언을 구해보세요!"
        html_message = message.replace('\n', '<br>')

    return render_template("Alarm.html", badge_notification=badge_notification, html_message=html_message)        


if __name__ == '__main__':
    socketio.run(app, debug=True)