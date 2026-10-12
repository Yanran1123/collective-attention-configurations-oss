import datetime

import mongoengine


# Referenced to a commit or commitComment
class ReferencedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    commitOid = mongoengine.StringField()
    commitRepository = mongoengine.StringField(required=True)

    isCrossRepository = mongoengine.BooleanField(required=True)
    isDirectReference = mongoengine.BooleanField(required=True)

    # issue or pull request which was referenced, i.e., the focal issue whose ReferencedEvent is checked
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.referenced',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
