import datetime
import mongoengine

from Classes.event.otherpronly.deployment import Deployment


class Deployed(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    databaseId = mongoengine.IntField()

    refType = mongoengine.StringField()
    refName = mongoengine.StringField()
    refPrefix = mongoengine.StringField()
    refOid = mongoengine.StringField()  # Commit, tag, blob, or tree

    deployment = mongoengine.EmbeddedDocumentField(Deployment)

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.deployed',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
