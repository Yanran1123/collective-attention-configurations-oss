import datetime

import mongoengine


class CommentDeletedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    
    databaseId = mongoengine.IntField()

    # Whose comment is deleted, the object ID of an issue/pullRequest
    subjectType = mongoengine.StringField()
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.commentDeleted',
        'indexes': [
            {'fields': ['createdAt'], 'name': "timeline_index"}
        ]
    }
