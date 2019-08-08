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

@app.route('/')
def index():
    welcome_page = {
        "title": "No Posts Yet",
        "content": "",
        "create_date": ""
    }
 
    context = {
        "welcome_page": welcome_page,
    }

    template = render("chalicelib/templates/index.html", context)
    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })



