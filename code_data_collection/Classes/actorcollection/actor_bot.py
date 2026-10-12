import datetime

import mongoengine


# Bot: https://developer.github.com/v4/object/bot/
class ActorBot(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    login = mongoengine.StringField(required=True)
    actorType = mongoengine.StringField(required=True)

    email = mongoengine.StringField(required=True)
    name = mongoengine.StringField()

    avatarUrl = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'actor.bots',
        'indexes': [
            {'fields': ['login'], 'name': "login_index"}
        ]
    }
