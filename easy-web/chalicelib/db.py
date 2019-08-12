
DEFAULT_USERNAME = 'default'

class InMemoryAthleteDB(object):
    def __init__(self, state=None):
        if state is None:
            state = {}
        self._state = state

    def list_all_athletes(self):
        all_athletes = []
        for username in self._state:
            all_athletes.extend(self.list_athletes(username))
        return all_athletes

    def list_athletes(self, username=DEFAULT_USERNAME):
        return list(self._state.get(username, {}).values())

    def list_all_athletes(self):
        all_athletes = []
        all_athletess.extend(self.list_athletes())
        return all_athletes

    def add_athlete(self, athlete, strava_token, activity_bearer, steemit_user=None, steemit_token=None, metadata=None, username=DEFAULT_USERNAME):
        if username not in self._state:
            self._state[username] = {}
        self._state[username][athlete] = {
            'athlete': athlete,
            'strava_token': strava_token,
            'activity_bearer': activity_bearer,
            'steemit_user': steemit_user,
            'steemit_token': steemit_token,
            'metadata': metadata if metadata is not None else {},
            'username': username
        }

    def get_athlete(self, athlete, username=DEFAULT_USERNAME):
        return self._state[username][athlete]

    def delete_athlete(self, athlete, username=DEFAULT_USERNAME):
        del self._state[username][athelte]

    def update_athlete(self, athlete, strava_token=None, activity_bearer=None, steemit_user=None, metadata=None, username=DEFAULT_USERNAME):
        item = self._state[username][athlete]
        if strava_token is not None:
            item['strava_token'] = strava_token
        if activity_bearer is not None:
            item['activity_bearer'] = activity_bearer
        if steemit_user is not None:
            item['steemit_user'] = steemit_user
        if metadata is not None:
            item['metadata'] = metadata

