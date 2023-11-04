from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('goal1.html')

@app.route('/goal2')
def goal_registration():
    return render_template('goal2.html')

@app.route('/set_budget', methods=['POST'])
def set_budget():
    budget = request.form.get('budgetAmount')

    # 여기에서 budget를 저장하거나 처리하는 로직을 추가할 수 있습니다.
    # 예를 들어, 데이터베이스에 저장하거나 세션에 저장할 수 있습니다.

    message = "목표 예산이 설정되었습니다."
    return render_template('goal2.html', message=message, budget=budget)

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
