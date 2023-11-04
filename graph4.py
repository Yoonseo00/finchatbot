import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def generate_budget_spent_pie_chart(csv_file):
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    # CSV 파일에서 데이터를 불러오기
    df = pd.read_csv(csv_file)

    # 데이터에서 목표예산과 총 소비금액을 가져오기
    budget = df['Budget'].sum()
    total_spent = df['Spent'].sum()

    # 원 그래프 데이터 생성
    data = [budget - total_spent, total_spent]
    categories = ['남은 예산', '총 소비금액']

    # 원 그래프 그리기
    plt.figure(figsize=(6, 6))
    plt.pie(data, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title('예산 및 소비 현황')

    # 그래프를 이미지로 저장
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # 이미지를 파일로 저장
    with open('budget_spent_pie_chart.png', 'wb') as f:
        f.write(buffer.read())

    # 버퍼 닫기
    buffer.close()
