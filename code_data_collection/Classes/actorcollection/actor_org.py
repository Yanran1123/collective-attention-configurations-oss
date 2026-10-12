import datetime

import mongoengine


# Organization: https://developer.github.com/v4/object/organization/
class ActorOrganization(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    login = mongoengine.StringField(required=True)
    actorType = mongoengine.StringField(required=True)

    email = mongoengine.StringField(required=True)
    name = mongoengine.StringField()

    avatarUrl = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'actor.organizations',
        'indexes': [
            {'fields': ['login'], 'name': "login_index"}
        ]
    }
