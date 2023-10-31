from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route('/main')
def main():
    return render_template('Main.html')

if __name__ == '__main__':
    app.run()
