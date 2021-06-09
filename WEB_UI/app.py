from flask import Flask, render_template, request
import requests
import os

CALCULATOR_URL = "https://calculator-http-function.azurewebsites.net/api/http-triggered-calculator?code=0GvuUWV7az1UquaW1lJBaLJ6r/Ao8lrQBgm6kS94MRf86eCDqZksKQ=="
STAT_FILE = 'stat.csv'

app = Flask(__name__)


def substitute(formula):
    return formula.replace('integral', '\\int').replace(' ', '\ ')


def calculate_equation(problem, name):
    try:
        r = requests.post(CALCULATOR_URL, json={"question": problem.replace('\\ ', ' '), "username": name})
        if r.status_code != 200:
            print(r.status_code)
            raise Exception("Bad request")
        return substitute(r.json()["response"])
    except Exception as e:
        return '!@#$Error!@#$'


@app.route('/', methods=['GET'])
def root():
    return render_template('index.html', original_equation='x^2 + 2x = 0')


@app.route('/calculate', methods=['POST'])
def calculate():
    problem = request.form['problem']
    name = request.form['name']
    print(name)
    return render_template("index.html", original_equation=problem, answer=calculate_equation(problem, name))


@app.route('/statistics', methods=['GET'])
def statistics():
    if not os.path.exists(STAT_FILE):
        res = []
    else:
        with open(STAT_FILE) as f:
            res = [(line[:line.index(',')].strip(', '), line[line.rindex(','):].strip(', ')) for line in f.readlines() if line]
    return render_template('statistics.html', items=res)


@app.route("/update_statistics", methods=['GET', 'POST'])
def update_stat():
    new_stat = request.json
    print(new_stat)
    with open(STAT_FILE, 'w') as stat:
        for entry in new_stat['users']:
            print(f"{entry['username']}, {entry['count']}", file=stat)
    return '', 200



if __name__ == "__main__":
    app.run('127.0.0.1', 8000)
