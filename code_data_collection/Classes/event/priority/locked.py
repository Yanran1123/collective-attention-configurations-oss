import datetime

import mongoengine


class LockedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    lockReason = mongoengine.StringField()
    """
    Values
    OFF_TOPIC
    The issue or pull request was locked because the conversation was off-topic.
    
    RESOLVED
    The issue or pull request was locked because the conversation was resolved.
    
    SPAM
    The issue or pull request was locked because the conversation was spam.
    
    TOO_HEATED
    The issue or pull request was locked because the conversation was too heated.
    """

    # Lockable: Object that was locked
    lockableType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    lockableId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.locked',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
