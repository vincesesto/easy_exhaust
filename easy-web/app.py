import os
import jinja2
import requests
import boto3
from datetime import datetime
from chalice import Chalice, Response
from chalicelib import db

app = Chalice(app_name='easy-web')

app.debug = True
_DB = None
DEFAULT_USERNAME = 'default'
api_token = '6769ae72996e05a36ac38d546871dd63982b2651'
client_id = 31940
athlete_url_base = 'https://www.strava.com/api/v3/athlete'
strava_auth_url = 'https://www.strava.com/oauth/token'
APP_API_URL = 'https://n9oya74pbg.execute-api.ap-southeast-2.amazonaws.com/api/'

def get_inmemory_athlete_db():
    global _DB
    if _DB is None:
        _DB = db.InMemoryAthleteDB()
    return _DB

def get_athlete_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBAthletes(
            boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
        )
    return _DB

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

def update_activity_bearer(user_key):
    # Update their latest_bearer for the user so you can check more activity
    # Update this in the database
    try:
       response = requests.post(strava_auth_url,
                            params={'client_id': client_id, 'client_secret': api_token, 'code': user_key,
                            'grant_type': 'authorization_code'})
       access_info = dict()
       activity_data = response.json()
       access_info['access_token'] = activity_data['access_token']
       return access_info
    except:
        print("Log - An Error occurred trying to authenticate with the {} Strava token".format(user_key))
        return False

def check_new_user(activity_bearer):
        # Search through users strava details
        # Verify it is not in db already
        bearer_header = "Bearer " + str(activity_bearer)
        headers = {'Content-Type': 'application/json', 'Authorization': bearer_header}
        response = requests.get( athlete_url_base, headers=headers )
        data = response.json()
        return data

@app.route('/athletes', methods=['GET'])
def get_athletes():
    return get_athlete_db().list_athletes()

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

@app.route('/')
def index():
    welcome_page = {
        "title": "No Posts Yet",
        "content": "",
        "create_date": ""
    }
 
    context = {"welcome_page": welcome_page}

    template = render("chalicelib/templates/index.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })

@app.route('/signup')
def sign_up():
    resp = app.current_request.to_dict()
    signup_token=resp['query_params']['code']
    context = {'signup_token': signup_token}

    template = render("chalicelib/templates/sign_up.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })

@app.route('/strava_auth')
def strava_auth():           
    # Redirect to strava auth 
    strava_auth_url="http://www.strava.com/oauth/authorize?client_id=31940&response_type=code&redirect_uri={}exchange_token&approval_prompt=force&scope=profile:write,activity:write,activity:read_all".format(APP_API_URL)

    # Now return a response and redirect to new page
    context = {'strava_auth_url': strava_auth_url}
    template = render("chalicelib/templates/strava_auth_redirect.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })

# Use something like this to get all the details from the retured url
@app.route('/exchange_token')
def exchange():
    # return dictionary of results
    resp = app.current_request.to_dict()
    token=resp['query_params']['code']
    easy_auth_url="{}signup?code={}".format(APP_API_URL, token)

    context = {'strava_auth_url': easy_auth_url}

    template = render("chalicelib/templates/strava_auth_redirect.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })

@app.route('/all_finished')
def all_finished():
    resp = app.current_request.to_dict()
    strava_token=resp['query_params']['strava_token']
    steem_name=resp['query_params']['steem_name']

    # Get the user activity bearer from strava
    activity_bearer = update_activity_bearer(strava_token)

    print(activity_bearer)

    # Get extra details from strava
    values = check_new_user(activity_bearer['access_token'])

    print(values)
    
    # post details to the database

    new_user = {"athlete": values['id'], "strava_token": strava_token, "activity_bearer": activity_bearer, "steemit_user": steem_name, "steemit_token": None,  "metadata": {}}

    print(new_user)

    get_athlete_db().add_athlete(
        athlete=str(values['id']),
        strava_token=strava_token,
        activity_bearer=activity_bearer['access_token'],
        steemit_user=steem_name,
        steemit_token=None,
        metadata={},
    )
    
    context = {'strava_token': strava_token,
               'steem_name': steem_name }

    template = render("chalicelib/templates/all_finished.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })
