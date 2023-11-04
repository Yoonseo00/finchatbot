from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/main')
def Main():
    return render_template('Main.html')

@app.route('/alarm')
def Alarm():
    return render_template("Alarm.html")

@app.route('/addspend')
def AddSpend():
    return render_template("AddSpend.html")

@app.route('/spendlist')
def SpendList():
    return render_template("SpendList.html")

@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        print(result)
        return render_template("AddResult.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)