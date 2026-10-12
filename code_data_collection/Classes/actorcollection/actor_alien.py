import datetime

import mongoengine


class ActorAlien (mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # At least when this actor authored a commit, it did not sign up for GitHub
    # login = mongoengine.StringField()
    # # It seems to be users/humans
    # actorType = mongoengine.StringField()

    email = mongoengine.StringField(required=True)  # Identified by this field
    name = mongoengine.StringField()

    # avatar_url = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'actor.aliens',
        'indexes': [
            {'fields': ['email'], 'name': "email_index"}
        ]
    }
