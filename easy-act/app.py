import requests
import json
import boto3
import os
from chalice import Chalice
from chalicelib import db
from datetime import datetime, timedelta

app = Chalice(app_name='easy-act')

app.debug = True
_DB = None
_ATHLETEDB = None
_ACTIVITYDB = None
DEFAULT_USERNAME = 'default'

def list_all_athlete_ids():
    # Go through the database and get all the athlete ids ready to search for activities
    response = requests.get('http://127.0.0.1:8000/athletes')
    token_list = []
    for i in response.json():
        entry = {}
        entry["strava_token"] = i['strava_token']
        entry["activity_bearer"] = i['activity_bearer']
        token_list.append(entry)
    return token_list

def list_all_activity_ids():
    # Go through the activity database and get all activities not posted to exhaust
    response = requests.get('http://127.0.0.1:8000/activities')
    activity_list = []
    for i in response.json():
        if i['exhaust_up'] == "No":
            activity_list.append(i)
    return activity_list

def does_activity_exist(activity_id):
    # Double check if the activity is already in our database
    url = "http://127.0.0.1:8000/activities/{}".format(activity_id)
    response = requests.get(url)
    if response:
        try:
            return response.json()['activity_id']
        except:
            print("Log - The Activity Database is empty with no activities present")
            return False
    else:
        return False

def check_for_activities(activity_token):
    # activity bearer is needed as part of the data
    print("Log - Searching For New Activities")
    bearer_header = "Bearer " + activity_token
    headers = {'Content-Type': 'application/json', 'Authorization': bearer_header}
    t = datetime.now() - timedelta(days=7)
    parameters = {"after": int(t.strftime("%s"))}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=parameters )
    activity_data = response.json()
    return activity_data

def check_additional_data(activity_id, activity_token):
    # Use the activity ID to get additional data
    bearer_header = "Bearer " + activity_token
    headers = {'Content-Type': 'application/json', 'Authorization': bearer_header}
    activity_parameters = {"id": activity_id}
    activity_url = "https://www.strava.com/api/v3/activities/" + str(activity_id)
    additional_response = requests.get( activity_url, headers=headers, params=activity_parameters )
    additional_data = additional_response.json()
    return additional_data

def get_inmemory_athlete_db():
    global _ATHLETEDB
    if _ATHLETEDB is None:
        _ATHLETEDB = db.InMemoryAthleteDB()
    return _ATHLETEDB

def get_athlete_db():
    global _ATHLETEDB
    if _ATHLETEDB is None:
        _ATHLETEDB = db.DynamoDBAthletes(
            boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
        )
    return _ATHLETEDB

def get_activity_db():
    global _ACTIVITYDB
    if _ACTIVITYDB is None:
        _ACTIVITYDB = db.InMemoryActivityDB()
    return _ACTIVITYDB

@app.route('/athletes', methods=['GET'])
def get_athletes():
    return get_athlete_db().list_all_athletes()

@app.route('/athletes/{athlete}', methods=['GET'])
def get_athlete(athlete):
    return get_athlete_db().get_athlete(athlete)

@app.route('/athletes/{athlete}', methods=['DELETE'])
def delete_athlete(athlete):
    return get_athlete_db().delete_athlete(athlete)

@app.route('/athletes', methods=['POST'])
def add_new_athlete():
    body = app.current_request.json_body
    return get_athlete_db().add_athlete(
        athlete=body['strava_id'],
        strava_token=body['strava_token'],
        activity_bearer=body['activity_bearer'],
        steemit_user=body['steemit_user'],
        steemit_token=body['steemit_token'],
        metadata=body.get('metadata'),
    )

@app.route('/athletes/{athlete}', methods=['PUT'])
def update_athlete(athlete):
    body = app.current_request.json_body
    get_athlete_db().update_athlete(
        athlete,
        strava_token=body.get('strava_token'),
        activity_bearer=body.get('activity_bearer'),
        steemit_user=body.get('steemit_user'),
        steemit_token=body.get('steemit_token'),
        metadata=body.get('metadata'))

@app.route('/activities', methods=['GET'])
def get_activities():
    return get_activity_db().list_activities()

@app.route('/activities', methods=['POST'])
def add_new_activities():
    body = app.current_request.json_body
    return get_activity_db().add_activity(
        activity_id=body['activity_id'],
        strava_user=body['strava_user'],
        activity_date=body['activity_date'],
        type=body['type'],
        title=body['title'],
        distance=body['distance'],
        duration=body['duration'],
        description=body['description'],
        photo=body['photo'],
        exhaust_up=body['exhaust_up'],
        metadata=body.get('metadata'),
    )

@app.route('/activities/{activity_id}', methods=['GET'])
def get_activity(activity_id):
    return get_activity_db().get_activity(activity_id)

@app.route('/activities/{activity_id}', methods=['DELETE'])
def delete_activity(activity_id):
    return get_activity_db().delete_activity(athlete)

@app.route('/activities/{activity_id}', methods=['PUT'])
def update_activity(activity_id):
    body = app.current_request.json_body
    get_activity_db().update_activity(
        activity_id,
        strava_user=body.get('strava_user'),
        activity_date=body.get('activity_date'),
        type=body.get('type'),
        title=body.get('title'),
        distance=body.get('distance'),
        duration=body.get('duration'),
        description=body.get('description'),
        photo=body.get('photo'),
        exhaust_up=body.get('exhaust_up'),
        metadata=body.get('metadata'))

@app.route('/loop', methods=['GET'])
def loop_athletes_db():
    # loop through the athletes db and get the activity_bearer of each
    #client_id = 31940
    #client_secret = "6769ae72996e05a36ac38d546871dd63982b2651"
    token_list = list_all_athlete_ids()
    for i in token_list:
        activity_data = check_for_activities(i['activity_bearer'])

        # Only want Runs Bikes Swims Yoga
        desired_activities = ("Run", "Ride", "Swim", "Yoga")
        if str(activity_data[-1]['type']) not in desired_activities:
                break
        # only add the new activity if it does not exist
        if not does_activity_exist(activity_data[-1]['id']):
            additional_data = check_additional_data(activity_data[-1]['id'],i['activity_bearer'])

            # Only Run, Bike or Hikes can be uploaded if they have a valid GPX file
            print(str(activity_data[-1]['external_id']))

            activity_description = "This activity was uploaded via the Exhaust API. For more details on this {}, feel free to checkout Strava at https://www.strava.com/activities/{}".format(str(activity_data[-1]['type']), str(activity_data[-1]['id']))

            activity = '{"activity_id": "' + str(activity_data[-1]['id']) + '", "strava_user": ' + str(activity_data[-1]['athlete']['id']) + ', "activity_date": "' + str(additional_data['start_date_local']) + '", "type": "' + str(activity_data[-1]['type']) + '", "title": "' + str(activity_data[-1]['name']) + '", "duration": ' + str(activity_data[-1]['elapsed_time']) + ', "distance": ' + str(activity_data[-1]['distance']) + ', "description": "' + activity_description + '", "photo": "", "exhaust_up": "No", "metadata": {}}'

            response = requests.post("http://127.0.0.1:8000/activities",
                             data=activity, headers={"Content-Type": "application/json"})
