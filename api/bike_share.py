import flask
from flask import g, jsonify, request, json
import sqlite3
import pickle
from datetime import datetime
import math
import numpy as np
import random

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')
model = pickle.load(open(("../models/xgboost.pkl"), 'rb'))

# queries
get_related_stations = "SELECT DEST_ID FROM related_stations WHERE SOURCE_ID = ?;"
get_cluster_id = "SELECT CLUSTER_ID FROM station_mapping WHERE STATION_ID = ?;"
get_id_by_station_name = "SELECT STATION_ID from stations where STATION_NAME = ?;"
get_stations = "SELECT * from stations;"
get_info_by_id = "SELECT STATION_NAME, LATITUDE, LONGITUDE from stations WHERE STATION_ID = ?;"


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("../database/stations.sql", mode='r') as f:
            db.cursor().executescript(f.read())
        with app.open_resource("../database/related_stations.sql", mode='r') as f:
            db.cursor().executescript(f.read())
        with app.open_resource("../database/station_mapping.sql", mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/home', methods=['GET'])
def get_all_stations():
    stations = query_db(get_stations)
    curr_time = datetime.now()
    st = []
    for station in stations:
        X = np.array([[get_cluster(station.get('STATION_ID'))[0].get('cluster_id'), seasons(curr_time.month),\
             curr_time.weekday(), curr_time.hour]])
        demand = model.predict(X)
        st.append({'station_name' : station.get('STATION_NAME'), 'station_id' : station.get('STATION_ID'),\
            'latitude' : station.get('LATITUDE'), 'longitude' : station.get('LONGITUDE'), 'demand' : math.ceil(demand[0]),\
                'availability' : random.randrange(7)})
    return jsonify(st)


@app.route('/get_demand', methods=['GET'])
def get_station():
    req = request.args.to_dict()
    data = json.loads(list(req.keys())[0])
    if data:
        date = data["date"]
        time = data["time"]
        station_name = data["station_name"]
        year = datetime.strptime(date, "%Y-%m-%d").year
        month = datetime.strptime(date, "%Y-%m-%d").month
        day = datetime.strptime(date, "%Y-%m-%d").day
        hour = datetime.strptime(time, "%H:%M").hour
        dayOfWeek = datetime(year, month, day).weekday()
        station_id = query_db(get_id_by_station_name, [station_name])[0].get('STATION_ID')
        related_stations = query_db(get_related_stations, [station_id])
        
        
        related_stations.insert(0 , {'dest_id' : station_id})
        curr_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        curr_time = datetime.strftime(datetime.now(), '%H:%M')

        i = 1
        while(i < len(related_stations)):
            if related_stations[i].get('dest_id') == related_stations[0].get('dest_id'):
                del related_stations[i]
            i = i + 1

        list_stations = []
        for i in range(len(related_stations)):
            clusted_station_id = query_db(get_cluster_id, [related_stations[i].get('dest_id')])
            list_stations.append([clusted_station_id[0].get('cluster_id'), month, dayOfWeek, hour])
        predict_vals = np.array(list_stations)
        prediction = model.predict(predict_vals)

        if date == curr_date and time == curr_time:
            availability = 1
        else:
            availability = "Not known"
        
        demand = []
        for i in range(len(related_stations)):
            st_id = related_stations[i].get('dest_id')
            name = query_db(get_info_by_id, [st_id])[0].get('STATION_NAME')
            lat =  query_db(get_info_by_id, [st_id])[0].get('LATITUDE')
            lon =   query_db(get_info_by_id, [st_id])[0].get('LONGITUDE')
            avail_func = lambda x: random.randrange(10) if availability == 1 else "Not Known"
            demand.append({"station_id" : st_id, "station_name" : name, "demand" : math.ceil(prediction[i]),\
                "availability": avail_func(availability), "latitude" : lat, "longitude" : lon})
    return jsonify(demand)     

def get_cluster(station_id):
    cluster_id = query_db(get_cluster_id, [station_id])
    return cluster_id

def seasons(month):
  # winter - very less usage
  if month == 12 or month == 1 or month == 2:
    return 0
  # spring - less usage
  elif month == 3 or month == 4 or month == 5:
    return 1
  # fall - frequent usage
  elif month == 9 or month == 10 or month == 11:
    return 2
  # summer - very frequent usage
  elif month == 6 or month == 7 or month == 8:
    return 3