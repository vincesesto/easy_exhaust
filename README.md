# easy_exhaust

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

