from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pymysql



app = Flask(__name__)

def connect_to_db():
    # MySQL 데이터베이스 연결 설정
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='1234',
        database='finchatbot',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def budget_data():
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        # 예산과 총 소비금액 가져오기
        cursor.execute('SELECT SUM(Budget) as Budget, SUM(Spent) as Spent FROM budget_data')
        result = cursor.fetchone()  # 결과 가져오기

        Budget = result['Budget'] if result['Budget'] else 0
        Spent = result['Spent'] if result['Spent'] else 0

        # 예산 사용률 계산
        budget_percentage = (Spent / Budget) * 100 if Budget > 0 else 0

        return Budget, Spent, budget_percentage

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

    finally:
        cursor.close()
        conn.close()



def display_budget():

    Budget, Spent,budget_percentage=budget_data()
    # 원 그래프 데이터 생성
    data = [Budget - Spent, Spent]
    categories = ['남은 예산', '총 소비금액']

    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False

    # 원 그래프 생성
    fig, ax = plt.subplots()
    ax.pie(data, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.set_title('예산 및 소비 현황')

    # 이미지를 바이트로 변환하고 base64로 인코딩
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return graph_url
