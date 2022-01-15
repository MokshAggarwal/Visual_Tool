from flask import Flask, render_template, request, redirect, json, jsonify
from flask_cors import CORS
import folium, random, pandas as pd, numpy as np, pickle 
from overlap import wrapper

app = Flask(__name__)
CORS(app)
score_delhi = pickle.load(open('static/gtfs/Delhi/statistics/score_delhi.pkl','rb'))
score_bangalore = pickle.load(open('static/gtfs/Bangalore/statistics/score_bangalore.pkl','rb'))

# score_delhi

@app.route('/')
def home():
    cities = [{'name' : 'Delhi'}, {'name' : 'Bangalore'}]
    return render_template('home.html', data = cities)


@app.route('/', methods = {'POST'})
def dropdown():
    city_sel = str(request.form['comp_select'])
    return redirect(f"http://127.0.0.1:5000/city/{city_sel}")

@app.route('/city/<cityname>')
def city(cityname):
    # Read City Data
    return render_template('city.html')

@app.route('/city/<cityname>', methods = {'POST'})
def f1(cityname):
    option = str(request.form['options'])
    if option == 'Overlap':
        return redirect(f"http://127.0.0.1:5000/city/{cityname}/ovl")
    else:
        str_city = cityname + '.html'
        return render_template(str_city)

@app.route('/city/<cityname>/ovl')
def f2(cityname):
    return render_template('ovl.html')


@app.route('/city/<cityname>/ovl', methods = {'POST'})
def f3(cityname):
    route_sel = int(request.form['route'])
    thresh = float(request.form['thresh'])
    return wrapper(thresh, route_sel, cityname)

@app.route('/getScoreDelhi')
def getScoreDelhi():
    data = score_delhi.get(request.args['Ward_No'], {})
    try:
        data['None']=data[None]
        del data[None]
    except:
        pass
    return jsonify(data)

@app.route('/getScoreBangalore')
def getScoreBangalore():
    print(type(request.args['Ward_No']))
    data = score_bangalore.get(int(request.args['Ward_No']),{})
    # print(data)
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug = True)