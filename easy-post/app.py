import requests
import json
import boto3
import os
from beem import Steem
from chalice import Chalice
from chalicelib import db
from datetime import datetime, timedelta
from decimal import Decimal

app = Chalice(app_name='easy-post')

app.debug = True
_DB = None
_ATHLETEDB = None
_ACTIVITYDB = None
DEFAULT_USERNAME = 'default'
client_secret = os.environ['API_TOKEN']
client_id = os.environ['CLIENT_ID']
strava_auth_url = os.environ['STRAVA_AUTH_URL']
easy_act_api = os.environ['APP_API_URL']
exhaust_token = os.environ['EXHAUST_TOKEN']
s3_bucket = os.environ['S3_BUCKET_NAME']
posting_keys = os.environ['POSTING_KEY']

steem = Steem(
    keys=[posting_keys,]
)


def download_description(activity_id):
    print(activity_id)
    s3 = boto3.resource('s3')
    obj = s3.Object(s3_bucket, str(activity_id))
    body = obj.get()['Body'].read()
    return body.decode("utf-8")

def get_exhaust_token(athlete_id):
    # Go through the database and get all the athlete ids ready to search for activities
    athlete_url = easy_act_api + "athletes/" + athlete_id
    response = requests.get(athlete_url)
    token_list = []
    for i in response.json():
        token_list.append(i)
    return token_list

def list_all_activity_ids():
    # Go through the activity database and get all activities not posted to exhaust
    response = requests.get('http://127.0.0.1:8000/activities')
    activity_list = []
    for i in response.json():
        if i['exhaust_up'] == "No":
            activity_list.append(i)
    return activity_list

def get_activity_db():
    global _ACTIVITYDB
    if _ACTIVITYDB is None:
        _ACTIVITYDB = db.DynamoDBActivityDB(
            boto3.resource('dynamodb').Table(
                os.environ['ACT_TABLE_NAME'])
        )
    return _ACTIVITYDB

def get_athlete_db():
    global _ATHLETEDB
    if _ATHLETEDB is None:
        _ATHLETEDB = db.DynamoDBAthletes(
            boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
        )
    return _ATHLETEDB

@app.route('/athletes', methods=['GET'])
def get_athletes():
    return get_athlete_db().list_all_athletes()

@app.route('/athletes/{athlete}', methods=['GET'])
def get_athlete(athlete):
    return get_athlete_db().get_athlete(athlete)

@app.route('/activities', methods=['GET'])
def get_activities():
    return get_activity_db().list_all_activities()

@app.route('/activities/{activity_id}', methods=['GET'])
def get_activity(activity_id):
    try:
        return get_activity_db().get_activity(activity_id)
    except:
        return None

@app.route('/activities/{activity_id}', methods=['DELETE'])
def delete_activity(activity_id):
    return get_activity_db().delete_activity(activity_id)

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


# Get activities from the activities database
# Wrap it all together and post it to exhaust
@app.route('/post_to_steemit', methods=['GET'])
def loop_activities_db():
    posting_list = list_all_activity_ids()
    for i in posting_list:
        if str(i['title']) != "Weekly Report":
            print("Not a weekly report, next")
            continue

        print("Testing Vince")
        post_title = "@{} {}".format(i['activity_id'], i['title'])
        post_author = i['activity_id']
        post_permlink = "weekly_report_{}".format(datetime.now().strftime('%s'))
        post_app = "myapp/0.0.1"
        post_tags = "exhaust running fitnation runningproject sportstalk"
        post_body = download_description(int(i['strava_user']))

        print("Testing Vince")

        parse_body = True
        self_vote = True

        steem.post(post_title, post_body, author=post_author, tags=post_tags, parse_body=parse_body, self_vote=self_vote)

        break

        headers = '{"Authorization": "Token ' + str(exhaust_token) + '"}'
        headers = {'Authorization': 'Token f0fe1e22a00295f4dbca86557166e43e9e4e7cc1'}
        print(headers)
        response = requests.post(headers=headers, url=url, data=exhaust_post)

        print(response.content)
        if response.reason == 'Created':
            update_activity = '{"activity_id": "' + str(i['activity_id']) + '", "exhaust_up": "Yes"}'
            print(update_activity)
            url = "http://127.0.0.1:8000/activities/" + str(i['activity_id'])
            response = requests.put(url, data=update_activity, headers={"Content-Type": "application/json"})

