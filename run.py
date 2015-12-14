import pandas as pd
from flask import Flask, request, url_for, render_template
import sys

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
# @login_required
def index():
    return render_template('index.html')

@app.route('/opt2', methods=['GET','POST'])
def opt2():
    if '/var/www' in sys.path:
        metrics = pd.read_csv('yourServer/ex.csv')
    else:
        metrics = pd.read_csv('ex.csv')
    metrics.columns = [' ','Past 30 days', 'Past 90 days','Past year', 'Status']
    metrics['More details'] = "link"
    metricsH = metrics.to_html(classes="table table-hover",index=False)
    metricsH = metricsH.replace('border="1"', '')
    # dfH = dfH.replace('link', "<a href='http://example.com/'>Click</a>")
    metricsH = metricsH.replace('link', "<a href='#''>Click</a>")
    howMuch=6
    howMuchHi=12
    howMuchLo=0
    response = make_response(metricsH)
    response.headers["content-type"] = "text/plain"
    return response

@app.route('/opt1', methods=['GET','POST'])
def opt1():
    if '/var/www' in sys.path:
        metrics = pd.read_csv('ex/ex.csv')
    else:
        metrics = pd.read_csv('ex.csv')
    metrics.columns = [' ','Past 30 days', 'Past 90 days','Past year', 'Status']
    metrics['More details'] = "link"
    metricsH = metrics.to_html(classes="table table-hover",index=False)
    metricsH = metricsH.replace('border="1"', '')
    # dfH = dfH.replace('link', "<a href='http://example.com/'>Click</a>")
    metricsH = metricsH.replace('link', "<a href='#''>Click</a>")
    return render_template('index.html', totalAccts=100, totalBal=100, metricsH=metricsH)

if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=8000)


