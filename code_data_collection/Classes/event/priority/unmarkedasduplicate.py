import datetime

import mongoengine


class UnmarkedAsDuplicateEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField()

    # The Issue or PullRequest that is marked as duplicate
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.unmarkedAsDuplicate',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
