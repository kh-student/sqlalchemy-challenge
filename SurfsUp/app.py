# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# establish tables 
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session (link) from python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# set up dates from precipitation analysis
@app.route('/')
def homepage():
    """Honolulu, Hawaii Climate API"""
    return (
        f'Available routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # find the date one year ago from the last date in the database
    session = Session(engine)

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent = dt.datetime.strptime(most_recent, '%Y-%m-%d')
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    session.close()

    # query precipitation data for the last 12 months
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= start_date).all()

    session.close()
    
    # convert the query results to a dictionary with date as key and prcp as value
    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)

@app.route('/api/v1.0/stations')
def stations():
    # return json list of all stations from dataset
    session = Session(engine)

    stations = session.query(Station.station, Station.name).all()

    session.close()

# create and jsonify dictionary
    all_stations = []
    for station, name in stations:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
# query dates and temp observations of the most active station for the prev year
# most active station: USC00519281
    
# find the date one year ago from the last date in the database
    session = Session(engine)

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent[0]
    start_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)

    session.close()

# query last 12 months data from most active station
    session = Session(engine)

    tobs_9281 = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == 'USC00519281') \
        .filter(Measurement.date >= start_date).all()

    session.close()

# create and jsonify dictionary
    data_9281 = []
    for date, tobs in tobs_9281:
        tob_dict = {}
        tob_dict['date'] = date
        tob_dict['tobs'] = tobs
        data_9281.append(tob_dict)

    return jsonify(data_9281)

# return list of min, max, and avg temperature for a specified start date
@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)

    stats = session.query(
        Measurement.date, \
        func.min(Measurement.tobs), \
        func.max(Measurement.tobs), \
        func.avg(Measurement.tobs)) \
        .filter(Measurement.date >= start) \
        .group_by(Measurement.date) \
        .all()
    
    session.close()

# create and jsonify dictionary
    start_list = []
    for date, min, max, avg in stats:
        start_dict = {}
        start_dict['date'] = date
        start_dict['min'] = min
        start_dict['max'] = max
        start_dict['avg'] = avg
        start_list.append(start_dict)

    return jsonify(start_list)

# return list of min, max, and avg temperature for specified start to end dates
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    session = Session(engine)

    stats = session.query(
        Measurement.date, \
        func.min(Measurement.tobs), \
        func.max(Measurement.tobs), \
        func.avg(Measurement.tobs)) \
        .filter(Measurement.date >= start) \
        .filter(Measurement.date <= end) \
        .group_by(Measurement.date) \
        .all()

    session.close()

# create and jsonify dictionary
    start_end_list = []
    for date, min, max, avg in stats:
        start_end_dict = {}
        start_end_dict['date'] = date
        start_end_dict['min'] = min
        start_end_dict['max'] = max
        start_end_dict['avg'] = avg
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)