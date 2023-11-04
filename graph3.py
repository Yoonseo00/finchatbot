from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64


app = Flask(__name__)

def budget_data():
    # CSV 파일에서 데이터 읽기
    csv_data = pd.read_csv('budget_data.csv')  # CSV 파일명은 실제 파일명으로 수정해야 합니다

    # CSV 파일에서 필요한 데이터 추출 (예를 들어, 'budget' 및 'total_spent' 열)
    Budget = csv_data['Budget'].sum()  # 예산
    Spent = csv_data['Spent'].sum()  # 총 소비 금액

    # 예산 사용률 계산
    budget_percentage = (Spent / Budget) * 100 if Budget > 0 else 0

    return Budget, Spent, budget_percentage


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
