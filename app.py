from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='C:/capston/templates')

# 간단한 사용자 데이터베이스를 시뮬레이션합니다. 실제로는 데이터베이스를 사용해야 합니다.
users = {
    'user1': 'password1',
    'user2': 'password2'
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return "로그인 성공!"  # 실제로는 세션을 설정하거나 리다이렉션을 사용할 수 있습니다.
        else:
            return "로그인 실패. 다시 시도하세요."
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)