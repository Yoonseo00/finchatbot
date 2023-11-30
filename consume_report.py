from flask import Flask, render_template, request

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='C:/finchatbot/templates')

import graph1

df = graph1.load_data()

def monthly_spending(dataframe, year, month):

    selected_data = dataframe[(dataframe['add_date'].dt.year == year) & (dataframe['add_date'].dt.month == month)]
    total_spending = selected_data['add_price'].sum()

    return total_spending

def top3_categories_for_month(dataframe, year, month):
    selected_data = dataframe[(dataframe['add_date'].dt.year == year) & (dataframe['add_date'].dt.month == month)]

    # 카테고리별 소비액 합계를 계산
    category_spending = selected_data.groupby('add_category')['add_price'].sum()

    # 소비액이 많은 순서대로 정렬하고 top3를 반환
    top3_categories = category_spending.sort_values(ascending=False).head(3)

    result_string = "그 중 가장 많이 사용한 상위 3개의 카테고리는 "
    result_string += ", ".join([f"{category}: {spending}원" for category, spending in top3_categories.items()])


    return result_string