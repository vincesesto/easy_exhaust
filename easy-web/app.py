import os
import jinja2
from datetime import datetime
from chalice import Chalice, Response
from chalicelib import db

app = Chalice(app_name='easy-web')

app.debug = True
_DB = None
DEFAULT_USERNAME = 'default'

def get_athlete_db():
    global _DB
    if _DB is None:
        _DB = db.InMemoryAthleteDB()
    return _DB

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

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
    strava_auth_url="http://www.strava.com/oauth/authorize?client_id=31940&response_type=code&redirect_uri=http://127.0.0.1:8000/exchange_token&approval_prompt=force&scope=profile:write,activity:write,activity:read_all"

    # Now return a response and redirect to new page
    context = {'strava_auth_url': strava_auth_url}
    template = render("chalicelib/templates/strava_auth_redirect.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })


#Then get this
#THIS IS THE CODE YOU WILL KEEP FOR THE USER TO GET BEARER TOKENS
#http://localhost/exchange_token?state=&code=c4e6eb4d70a1ff0845ff64661e6948e29c8f1003&scope=read,activity:write,profile:write

# Use something like this to get all the details from the retured url
@app.route('/exchange_token')
def exchange():
    # return dictionary of results
    resp = app.current_request.to_dict()
    token=resp['query_params']['code']
    easy_auth_url="http://127.0.0.1:8000/signup?code={}".format(token)

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
    
    context = {'strava_token': strava_token,
               'steem_name': steem_name }

    template = render("chalicelib/templates/all_finished.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })
