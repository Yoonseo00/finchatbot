import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def display_budget():
    # 엑셀 파일에서 데이터 읽기
    excel_data = pd.read_excel('budget_data.xlsx')  # 엑셀 파일명은 실제 파일명으로 수정해야 합니다

    # 엑셀 파일에서 필요한 데이터 추출 (예를 들어, 'budget' 및 'total_spent' 열)
    Budget = excel_data['Budget'].sum()  # 예산
    Spent = excel_data['Spent'].sum()  # 총 소비 금액

    # 예산 사용률 계산
    budget_percentage = (Spent / Budget) * 100 if Budget > 0 else 0

    return render_template('budget.html', Budget=Budget, Spent=Spent, budget_percentage=budget_percentage)

@app.route('/index')
def index():
    df = load_data('C:/finchatbot/exdata.csv')
    category_avg=category_avg_for_last_3_months(df)
    graph = generate_graph(df)
    current_month_total_expense=calculate_current_month_total_expense(df)
    previous_3_months_total_expense = calculate_monthly_total_expense(df)
    exceeded_categories = find_exceeded_categories(df, category_avg)

    age_group=None
    comparison_graph = []
    exceeded_categories_avg = None

    if request.method == 'POST':
        age_group = request.form.get('age_group')  # 사용자가 선택한 연령대 (웹 페이지에서 설정)
        age_category_data = load_age_category_data(age_group)
        category_consume_current_month = category_consume_for_current_month(df)  # 이번 달 카테고리별 소비금액
        comparison_graph = generate_comparison_graph(age_category_data, category_consume_current_month)
        exceeded_categories_avg=find_exceeded_age_group(df,age_group)

    return render_template('index.html', graph=graph, current_month_total_expense=current_month_total_expense, previous_3_months_total_expense=previous_3_months_total_expense, exceeded_categories=exceeded_categories, age_group=age_group, comparison_graph=comparison_graph,exceeded_categories_avg=exceeded_categories_avg, results=[])

if __name__ == '__main__':
    app.run(debug=True)
