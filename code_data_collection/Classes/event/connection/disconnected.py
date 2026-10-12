import datetime

import mongoengine


class DisconnectedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    isCrossRepository = mongoengine.BooleanField(required=True)

    # issue or pull request from which the issue was disconnected
    # The focal issue or pull request, e.g., isse #2 of 'Netflix/metaflow'
    sourceType = mongoengine.StringField(required=True)
    sourceRepository = mongoengine.StringField(required=True)
    sourceNumber = mongoengine.IntField(required=True)
    sourceId = mongoengine.ObjectIdField(required=True)

    # issue or pull request which was disconnected
    # The other pull request that is connected, e.g., pullRequest #204 of 'Netflix/metaflow'
    subjectType = mongoengine.StringField(required=True)
    subjectRepository = mongoengine.StringField(required=True)
    subjectNumber = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField()

    meta = {
        'db_alias': 'core',
        'collection': 'events.disconnected',
        'indexes': [
            {'fields': ['sourceRepository', 'sourceNumber', 'createdAt'], 'name': "timeline_index"}
        ]
    }
