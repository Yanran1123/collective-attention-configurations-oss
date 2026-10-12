import datetime

import mongoengine


class RemovedFromProjectEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()

    # Those fields are not actually available in the API
    projectNumber = mongoengine.IntField()
    projectColumnName = mongoengine.StringField()

    # The issue or pullRequest associated with the event
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.removedFromProject',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
