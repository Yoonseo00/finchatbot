from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pymysql
import graph1



app = Flask(__name__)

def connectsql():
    conn = pymysql.connect(host='localhost', user = 'root', passwd = '1234', db = 'test', charset='utf8')
    return conn

def budget_data():
    conn = connectsql()
    cursor = conn.cursor()
    
    budget_query = "SELECT budget FROM budget;" 
    cursor.execute(budget_query)
    budget_tuple = cursor.fetchone()
    Budget = budget_tuple[0] if budget_tuple else 0
    
    df=graph1.load_data()
    Spent=graph1.calculate_current_month_total_expense(df)


    # 예산 사용률 계산
    budget_percentage = (Spent / Budget) * 100 if Budget > 0 else 0

    return Budget, Spent, budget_percentage
    
    cursor.close()
    conn.close()



def display_budget():
    Budget, Spent, budget_percentage = budget_data()

    # 원 그래프 데이터 생성
    remaining_budget = max(0, Budget - Spent)  # 음수가 아니도록 예산에서 이미 사용된 금액을 빼줍니다.
    data = [remaining_budget, Spent]
    categories = ['남은 예산', '총 소비금액']

    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 13

    # 원 그래프 생성
    fig, ax = plt.subplots(figsize=(7,7))

    if remaining_budget == 0:
        # Budget-Spent가 음수이면서 이미 사용된 금액이 예산을 초과할 때
        ax.pie(data, labels=categories, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#D94925'])
    else:
        ax.pie(data, labels=categories, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#ff9999'])

    ax.set_title('예산 및 소비 현황', fontsize=20, fontweight='bold')


    # 이미지를 바이트로 변환하고 base64로 인코딩
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return graph_url
