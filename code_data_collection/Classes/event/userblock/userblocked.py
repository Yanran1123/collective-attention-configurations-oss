import datetime

import mongoengine


class UserBlockedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    blockDuration = mongoengine.StringField(required=True)
    """
    Values
    ONE_DAY
    The user was blocked for 1 day
    
    ONE_MONTH
    The user was blocked for 30 days
    
    ONE_WEEK
    The user was blocked for 7 days
    
    PERMANENT
    The user was blocked permanently
    
    THREE_DAYS
    The user was blocked for 3 days
    """

    blockedUser = mongoengine.StringField()  # The user that is blocked
    blockedUserType = mongoengine.StringField()

    # Associated issue or pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.userBlocked',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
