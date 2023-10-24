from flask import Flask, render_template, request

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from io import BytesIO
import base64

app = Flask(__name__, template_folder='C:/finchatbot/templates')

# 데이터를 불러와 DataFrame으로 반환하는 함수
def load_data(file_path):
    # CSV 파일에서 데이터를 불러옵니다.
    df = pd.read_csv(file_path)
    # 날짜를 datetime 형식으로 변환합니다.
    df['날짜'] = pd.to_datetime(df['날짜'])


    return df

#연령대별로 나뉜 카테고리별 소비 금액 불러오는 함수
def load_age_category_data(age_group):
    age_category_data=pd.read_csv('C:/finchatbot/age_category_data.csv')
    age_category_data = age_category_data[age_category_data['연령대'] == age_group]

    return age_category_data

# 현재 달의 카테고리별 소비 금액 계산 함수
def current_consume_for_current_months(df):

    current_month = datetime.now().month
    filtered_data = df[df['날짜'].dt.month == current_month]

    current_consume = filtered_data.groupby('카테고리')['금액'].sum().to_dict()
    
    return current_consume


# 최근 3개월치 데이터 필터링 함수
def filter_data_for_last_3_months(df):
    # 현재 날짜 계산
    end_date = datetime.now()

    # 3개월 전 날짜 계산
    start_date = end_date - timedelta(days=90)
    
    # 최근 3개월치 데이터 필터링
    filtered_data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)]
    
    return filtered_data

# 최근 3개월 카테고리별 평균 소비 금액 계산 함수
def category_avg_for_last_3_months(df):

    filtered_data = filter_data_for_last_3_months(df)
    category_avg = filtered_data.groupby('카테고리')['금액'].mean()

    # 카테고리별 평균을 딕셔너리로 변환
    category_avg_dict = category_avg.to_dict()
    
    return category_avg_dict


# 3개월 평균 소비 그래프 생성 함수
def generate_graph(df):

    # 그래프 생성 코드
    # 한글 폰트 설정
    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False

    # 그래프를 그리기 위한 데이터를 준비합니다.

    category_avg=category_avg_for_last_3_months(df)

    labels = list(category_avg.keys())
    values = list(category_avg.values())

    # 막대 그래프를 그립니다.
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.xlabel('카테고리')
    plt.ylabel('평균 소비 금액')
    plt.title('카테고리별 평균 소비 금액 (최근 3개월)')

    # 그래프를 이미지로 변환
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    return graph_url


# 월별로 그룹화하여 총 소비 금액 계산 함수
def calculate_monthly_total_expense(df):
    filtered_data = filter_data_for_last_3_months(df)
    monthly_total_expense = filtered_data.groupby(filtered_data['날짜'].dt.strftime('%Y-%m'))['금액'].sum().to_dict()
    
    return monthly_total_expense

#최근 3개월 카테고리별 평균 소비금액보다 많이 소비한 카테고리 계산 함수
def find_exceeded_categories(df, category_avg):

    #현재 월 데이터 가져오기
    current_month = datetime.now().month
    current_month_data = df[df['날짜'].dt.month == current_month]

    # 초과한 카테고리와 그 차이를 저장하는 딕셔너리
    exceeded_categories = {}

    for category in current_month_data['카테고리'].unique():
        category_expense = current_month_data[current_month_data['카테고리'] == category]['금액'].sum()
        if category_expense > category_avg.get(category, 0):
            exceeded_amount = category_expense - category_avg[category]
            exceeded_categories[category] = exceeded_amount

    return exceeded_categories

# 사용자가 선택한 연령대의 카테고리별 소비금액보다 많이 소비한 카테고리 계산 함수

def find_categories_exceeding_age_group(df, age_group):
    age_category_data = load_age_category_data(age_group)
    age_category_avg = age_category_data.set_index('카테고리')['평균소비금액'].to_dict()
    
    current_month_data = current_consume_for_current_months(df)
    
    exceeded_categories = {}
    for category in current_month_data:
        if category in age_category_avg:
            if current_month_data[category] > age_category_avg[category]:
                exceeded_amount = current_month_data[category] - age_category_avg[category]
                exceeded_categories[category] = exceeded_amount
    
    return exceeded_categories

#비교 그래프 생성 함수
def generate_comparison_graph(age_category_data, current_month_data):
    categories = age_category_data['카테고리']
    age_category_avg = age_category_data['평균소비금액']
    
     # 'current_month_data'가 딕셔너리로 주어진 경우, 데이터를 리스트로 변환
    if isinstance(current_month_data, dict):
        current_month_avg = [current_month_data.get(category, 0) for category in categories]
    else:
        current_month_avg = current_month_data

    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    bar_positions = range(len(categories))

    plt.bar(
        [p - bar_width / 2 for p in bar_positions],
        age_category_avg,
        bar_width,
        label='연령대별 평균 소비금액'
    )

    plt.bar(
        [p + bar_width / 2 for p in bar_positions],
        current_month_avg,
        bar_width,
        label='이번 달 소비금액'
    )

    plt.xlabel('카테고리')
    plt.ylabel('소비금액')
    plt.title('연령대별 평균 소비금액 및 이번 달 소비금액 비교')
    plt.xticks(bar_positions, categories, rotation=45)
    plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    return [graph_url]
    
    
    


@app.route('/', methods=['GET', 'POST'])
def index():
    df = load_data('C:/finchatbot/exdata.csv')
    current_month_data=current_consume_for_current_months(df)
    category_avg=category_avg_for_last_3_months(df)
    graph = generate_graph(df)
    monthly_total_expense = calculate_monthly_total_expense(df)
    exceeded_categories = find_exceeded_categories(df, category_avg)
    comparison_graph = []
    exceeded_categories_avg = None

    if request.method == 'POST':
        age_group = request.form.get('age_group')  # 사용자가 선택한 연령대 (웹 페이지에서 설정)
        age_category_data = load_age_category_data(age_group)
        current_month_avg = current_consume_for_current_months(df)  # 이번 달 카테고리별 소비금액
        comparison_graph = generate_comparison_graph(age_category_data, current_month_avg)
        exceeded_categories_avg=find_categories_exceeding_age_group(df,age_group)

    return render_template('index.html', graph=graph, monthly_total_expense=monthly_total_expense, exceeded_categories=exceeded_categories, comparison_graph=comparison_graph,exceeded_categories_avg=exceeded_categories_avg, results=[])


if __name__ == '__main__':
    app.run(debug=True)