import datetime

import mongoengine


class UnlabeledEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    labelName = mongoengine.StringField(required=True)
    labelColor = mongoengine.StringField(required=True)
    labelId = mongoengine.ObjectIdField(required=True)

    # This part identifies the "Labelable" (issue or pull request) associated with the event
    labelableType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    labelableId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.unlabeled',
        'indexes': [
            {'fields': ['repository', 'number', 'labelableType', 'createdAt'], 'name': "timeline_index"}
        ]
    }
