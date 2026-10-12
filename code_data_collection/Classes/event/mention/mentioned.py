import datetime

import mongoengine


class MentionedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # The actor is the account that is mentioned
    # For example, if user B writes a comment that @mentions user A, the actor of the mentionedEvent
    # is user A (the mentioned account), not user B (who made the comment)
    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    databaseId = mongoengine.IntField()

    # A focal issue or pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.mentioned',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
