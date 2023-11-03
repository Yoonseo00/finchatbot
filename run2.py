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

if __name__ == '__main__':
    app.run(debug=True)
