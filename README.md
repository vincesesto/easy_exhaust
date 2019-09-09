# easy_exhaust

Application running on Chalice Python framework, deploying to AWS

## easy_web
## Web interface that allows users to get Strava Auth, Sign Up and provide extra details

### intex.html 
Welcome page with general information and sign up button to launch strava_auth_redirect.html

### strava_auth_redirect.html
Redirects to Strava to allow user to login and obtain api token, then launches sign_up.html

Includes the strava_auth function that creates the api auth url, then uses redirect page to send user to location

### sign_up.html
Allows user to provide their steemit_user name and then launches all_finished.html

Includes the sign_up function to get the details from the user input. 

### all_finished.html
Logs into Strava with api token, obtains a bearer token, then obtains basic user details

Includes all_finished function that does the work above and also adds user details to the athletes database

### Run easy-web locally to test
- Checkout the code
- export your AWS Profile:
```export AWS_PROFILE=work_account```
- Change into the easy-web directory and set up requirements
```cd easy_exhaust/easy-act; pip install -r requirements.txt```
- Run the dynamoDB creation script
```python createtable.py --table-type app```
- Verify you have a dynamoDB set up on your account
- Verify the new database details are in your .chalice/config.json file
- You can also add your other variables to the .chalice/config.json:
```
{
  "version": "2.0",
  "app_name": "easy-web",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "APP_TABLE_NAME": "<provided by chalice>",
        "APP_API_URL": "<provided by chalice>",
        "API_TOKEN": "<provided by strava>",
        "CLIENT_ID": <provided by strava>,
        "ATHLETE_URL_BASE": "https://www.strava.com/api/v3/athlete",
        "STRAVA_AUTH_URL": "https://www.strava.com/oauth/token"
      }
    }
  }
}
```
- Run the application locally to test
```chalice local```
- Access the url provided
```http://127.0.0.1:8000/```


## easy_act
## API that collects data from strava and posts to the activities database

### loop_athletes_db
This is the main function that is run by calling the URL: ```curl http://127.0.0.1:8000/loop | jq```

It is currently set up to only run when required but will look at setting this to occur every 2 hours or so.

### Run easy-act locally to test
- Perform the same as easy-web, including running ```chalice local```
- See if there are any athletes in the database:
```curl http://127.0.0.1:8000/athletes | jq```
- You can add a test user with a similar POST command:
```curl -H "Content-Type: application/json" -d '{"strava_id": "1746389", "strava_token": "f53de2ed2a5d40b3814f4927c315b8", "activity_bearer": "ccb18fbdd3e85f8f280eeb6dd24192897", "steemit_user": "test.vince.test", "steemit_token": "", "metadata": {}}' -X POST http://127.0.0.1:8000/athletes ```
- Check to see if your athlete is added
```curl http://127.0.0.1:8000/athletes | jq```
- You can then loop and see if the user has any activities with the following:
```curl http://127.0.0.1:8000/loop | jq```
- You can check to see if there are any activities in the database with the following:
```curl http://127.0.0.1:8000/activities | jq```

## easy_post
## API running periodically to post activities to Exhaust
