from flask import Flask, render_template, request

import pandas as pd
import matplotlib.pyplot as plt
import pymysql
from datetime import datetime, timedelta

from io import BytesIO
import base64

app = Flask(__name__, template_folder='C:/finchatbot/templates')

# 데이터를 불러와 DataFrame으로 반환하는 함수
def load_data():
    conn=pymysql.connect(host='127.0.0.1', user='root', password='1234', db='test', charset='utf8')
    cur=conn.cursor()

    query='select * from addspend'

    df = pd.read_sql(query, conn)
    # 연결 종료
    conn.close()

    df['add_date'] = pd.to_datetime(df['add_date'])


    return df

#연령대별로 나뉜 카테고리별 소비 금액 불러오는 함수
def load_age_category_data(age_group):
    age_category_data=pd.read_csv('C:/finchatbot/age_category_data.csv')
    age_category_data = age_category_data[age_category_data['연령대'] == age_group]

    return age_category_data

# 현재 달 데이터 필터링 함수
def filter_data_for_current_month(df):

    # 현재 날짜 가져오기
    current_date = datetime.now()

    # 현재 달의 첫 날과 마지막 날 계산
    current_month_first_day = datetime(current_date.year, current_date.month, 1)
    current_month_last_day = datetime(current_date.year, current_date.month, current_date.day)

    # 현재 달의 데이터 필터링
    current_month_data = df[
        (df['add_date'] >= current_month_first_day) &
        (df['add_date'] <= current_month_last_day)
    ]

    return current_month_data

# 현재 달의 총 소비액 계산 함수
def calculate_current_month_total_expense(df):

    current_month_data=filter_data_for_current_month(df)
   
    # 현재 달의 총 소비 금액 계산
    current_month_total_expense = current_month_data['add_price'].sum()

    return current_month_total_expense

# 현재 달의 카테고리별 소비 금액 계산 함수
def category_consume_for_current_month(df):

    current_month_data=filter_data_for_current_month(df)

    category_consume_current_month = current_month_data.groupby('add_category')['add_price'].sum().to_dict()
    
    return category_consume_current_month


# 최근 3개월치 데이터 필터링 함수
def filter_data_for_last_3_months(df):
    # 현재 날짜 계산
    end_date = datetime.now()

    # 현재 월과 연도 가져오기
    end_month = end_date.month
    end_year = end_date.year

    # 3개월 전 날짜 계산
    if end_month < 3:
    # 현재 월이 1월, 2월, 3월인 경우, 이전 연도의 10월, 11월, 12월 데이터를 포함
        start_month = 9 + end_month
        start_year = end_year - 1
    else:
    # 그 외의 경우, 현재 월로부터 3개월 전까지 데이터를 포함
        start_month = end_month - 3
        start_year = end_year

    # 직전 달의 마지막 날짜 계산 (현재 월의 1일에서 1일을 빼면 직전 달의 마지막 날짜)
    end_date = datetime(end_year, end_month, 1) - timedelta(days=1)

    # 시작 날짜 계산
    start_date = datetime(start_year, start_month, 1)

    # 최근 3개월치 데이터 필터링
    filtered_data = df[(df['add_date'] >= start_date) & (df['add_date'] <= end_date)]

    return filtered_data


# 최근 3개월 카테고리별 평균 소비 금액 계산 함수
def category_avg_for_last_3_months(df):

    filtered_data=filter_data_for_last_3_months(df)
    category_sum = filtered_data.groupby('add_category')['add_price'].sum()  # 각 카테고리별 금액의 합을 계산
    category_avg = category_sum / 3  # 3으로 나누어 평균을 계산
    category_avg = category_avg.to_dict()  # 결과를 딕셔너리로 변환

    return category_avg


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

    # 직전 3개월의 총 소비 금액 계산
    previous_3_months_total_expense = filtered_data.groupby(filtered_data['add_date'].dt.strftime('%Y-%m'))['add_price'].sum().to_dict()

    return previous_3_months_total_expense

#최근 3개월 카테고리별 평균 소비금액보다 많이 소비한 카테고리 계산 함수
def find_exceeded_categories(df, category_avg):

    #현재 월 데이터 가져오기
    current_month_data = category_consume_for_current_month(df)

    # 초과한 카테고리와 그 차이를 저장하는 딕셔너리
    exceeded_categories = {}

    for category in current_month_data:
        if current_month_data[category] > category_avg.get(category, 0):
            exceeded_amount = current_month_data[category] - category_avg[category]
            exceeded_categories[category] = exceeded_amount

    return exceeded_categories

# 사용자가 선택한 연령대의 카테고리별 소비금액보다 많이 소비한 카테고리 계산 함수

def find_exceeded_age_group(df, age_group):
    age_category_data = load_age_category_data(age_group)
    age_category_avg = age_category_data.set_index('카테고리')['평균소비금액'].to_dict()
    
    current_month_data = category_consume_for_current_month(df)
    
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