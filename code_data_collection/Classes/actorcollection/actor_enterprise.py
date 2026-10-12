import datetime

import mongoengine


# EnterpriseUserAccount: https://developer.github.com/v4/object/enterpriseuseraccount/
class ActorEnterprise(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    login = mongoengine.StringField(required=True)
    actorType = mongoengine.StringField(required=True)

    email = mongoengine.StringField(required=True)
    name = mongoengine.StringField()

    avatarUrl = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'actor.enterprises',
        'indexes': [
            {'fields': ['login'], 'name': "login_index"}
        ]
    }
