DEFAULT_USERNAME = 'default'

class InMemoryActivityDB(object):
    def __init__(self, state=None):
        if state is None:
            state = {}
        self._state = state

    def list_all_activities(self):
        all_activities = []
        for username in self._state:
            all_activities.extend(self.list_activities(username))
        return all_activities

    def list_activities(self, username=DEFAULT_USERNAME):
        return list(self._state.get(username, {}).values())

    def add_activity(self, activity_id, strava_user, activity_date, type, title, duration, distance=None, 
                     description=None, photo=None, exhaust_up=None, metadata=None, username=DEFAULT_USERNAME):
        if username not in self._state:
            self._state[username] = {}
        self._state[username][activity_id] = {
            'activity_id': activity_id,
            'strava_user': strava_user,
            'activity_date': activity_date,
            'type': type,
            'title': title,
            'duration': duration,
            'distance': distance if distance is not None else "",
            'description': description if description is not None else "",
            'photo': photo if photo is not None else "",
            'exhaust_up': exhaust_up if exhaust_up is not None else "No",
            'metadata': metadata if metadata is not None else {},
            'username': username
        }
        return activity_id

    def get_activity(self, activity_id, username=DEFAULT_USERNAME):
        try:
            return self._state[username][activity_id]
        except:
            return None

    def delete_activity(self, activity_id, username=DEFAULT_USERNAME):
        del self._state[username][activity_id]

    def update_activity(self, activity_id, strava_user=None, activity_date=None, type=None, title=None, duration=None, distance=None,
                     description=None, photo=None, exhaust_up=None, metadata=None, username=DEFAULT_USERNAME):
        item = self._state[username][activity_id]
        if strava_user is not None:
            item['strava_user'] = strava_user
        if activity_date is not None:
            item['activity_date'] = activity_date
        if type is not None:
            item['type'] = type
        if title is not None:
            item['title'] = title
        if duration is not None:
            item['duration'] = duration
        if distance is not None:
            item['distance'] = distance
        if description is not None:
            item['description'] = description
        if photo is not None:
            item['photo'] = photo
        if exhaust_up is not None:
            item['exhaust_up'] = exhaust_up
        if metadata is not None:
            item['metadata'] = metadata

class DynamoDBActivityDB(object):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_activities(self):
        response = self._table.scan()
        return response['Items']

    def list_activities(self, username=DEFAULT_USERNAME):
        response = self._table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']

    def add_activity(self, activity_id, strava_user, activity_date, type, title, duration, distance=None,
                     description=None, photo=None, exhaust_up=None, metadata=None, username=DEFAULT_USERNAME):
        self._table.put_item(
            Item={
            'activity_id': activity_id,
            'strava_user': strava_user,
            'activity_date': activity_date,
            'type': type,
            'title': title,
            'duration': duration,
            'distance': distance if distance is not None else "",
            'description': description if description is not None else "",
            'photo': photo if photo is not None else "",
            'exhaust_up': exhaust_up if exhaust_up is not None else "No",
            'metadata': metadata if metadata is not None else {},
            'username': username
            }
        )
        return activity_id

    def get_activity(self, activity_id, username=DEFAULT_USERNAME):
        response = self._table.get_item(
            Key={
                'username': username,
                'activity_id': activity_id
            }
        )
        return response['Item']

    def delete_activity(self, activity_id, username=DEFAULT_USERNAME):
        self._table.delete_item(
            Key={
                'username': username,
                'activity_id': activity_id,
            }
        )

    def update_activity(self, activity_id, strava_user=None, activity_date=None, type=None, title=None, duration=None, distance=None,
                     description=None, photo=None, exhaust_up=None, metadata=None, username=DEFAULT_USERNAME):
        item = self.get_item(activity_id, username)
        if strava_user is not None:
            item['strava_user'] = strava_user
        if activity_date is not None:
            item['activity_date'] = activity_date
        if type is not None:
            item['type'] = type
        if title is not None:
            item['title'] = title
        if duration is not None:
            item['duration'] = duration
        if distance is not None:
            item['distance'] = distance
        if description is not None:
            item['description'] = description
        if photo is not None:
            item['photo'] = photo
        if exhaust_up is not None:
            item['exhaust_up'] = exhaust_up
        if metadata is not None:
            item['metadata'] = metadata
        self._table.put_item(Item=item)

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
        return athlete

    def get_athlete(self, athlete, username=DEFAULT_USERNAME):
        return self._state[username][athlete]

    def delete_athlete(self, athlete, username=DEFAULT_USERNAME):
        del self._state[username][athelte]

    def update_athlete(self, athlete, strava_token=None, activity_bearer=None, steemit_user=None, steemit_token=None, metadata=None, username=DEFAULT_USERNAME):
        item = self._state[username][athlete]
        if strava_token is not None:
            item['strava_token'] = strava_token
        if activity_bearer is not None:
            item['activity_bearer'] = activity_bearer
        if steemit_user is not None:
            item['steemit_user'] = steemit_user
        if steemit_token is not None:
            item['steemit_token'] = steemit_token
        if metadata is not None:
            item['metadata'] = metadata

class DynamoDBAthletes(object):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_athletes(self):
        response = self._table.scan()
        return response['Items']

    def list_athletes(self, username=DEFAULT_USERNAME):
        response = self._table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']

    def add_athlete(self, athlete, strava_token, activity_bearer, steemit_user=None,
                    steemit_token=None, metadata=None, username=DEFAULT_USERNAME):
        self._table.put_item(
            Item={
                'athlete': athlete,
                'strava_token': strava_token,
                'activity_bearer': activity_bearer,
                'steemit_user': steemit_user,
                'steemit_token': steemit_token,
                'metadata': metadata if metadata is not None else {},
                'username': username
            }
        )
        return athlete

    def get_athlete(self, athlete, username=DEFAULT_USERNAME):
        response = self._table.get_item(
            Key={
                'username': username,
                'token': token,
            },
        )
        return response['Item']

    def delete_athlete(self, athlete, username=DEFAULT_USERNAME):
        self._table.delete_item(
            Key={
                'username': username,
                'token': token,
            }
        )

    def update_athlete(self, athlete, strava_token=None, activity_bearer=None, steemit_user=None,
                       steemit_token=None, metadata=None, username=DEFAULT_USERNAME):
        item = self.get_item(athlete, username)
        if strava_token is not None:
            item['strava_token'] = strava_token
        if activity_bearer is not None:
            item['activity_bearer'] = activity_bearer
        if steemit_user is not None:
            item['steemit_user'] = steemit_user
        if steemit_token is not None:
            item['steemit_token'] = steemit_token
        if metadata is not None:
            item['metadata'] = metadata
        self._table.put_item(Item=item)
