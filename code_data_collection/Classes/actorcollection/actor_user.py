import datetime

import mongoengine

from Classes.actorcollection.repo_association import RepoAssociation


# User: https://developer.github.com/v4/object/user/
class ActorUser(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    login = mongoengine.StringField(required=True)
    actorType = mongoengine.StringField(required=True)

    email = mongoengine.StringField(required=True)
    name = mongoengine.StringField()

    avatarUrl = mongoengine.StringField()

    repoAssociation = mongoengine.EmbeddedDocumentListField(RepoAssociation)

    meta = {
        'db_alias': 'core',
        'collection': 'actor.users',
        'indexes': [
            {'fields': ['login'], 'name': "login_index"}
        ]
    }
