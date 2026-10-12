import datetime

import mongoengine


class ConnectedEvent(mongoengine.Document):
    """
    Event that connect an issue to a pull request OR a pull request to an issue
    """
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    isCrossRepository = mongoengine.BooleanField(required=True)

    # issue or pull request that made the reference
    # The focal issue -- E.g., issue #326 of repo uber/neuropod, when we check its ConnectedEvent
    sourceType = mongoengine.StringField(required=True)
    sourceRepository = mongoengine.StringField(required=True)
    sourceNumber = mongoengine.IntField(required=True)
    sourceId = mongoengine.ObjectIdField(required=True)

    # issue or pull request which was connected
    # The different connected pr -- E.g., pullRequest #364 of repo uber/neuropod
    subjectType = mongoengine.StringField(required=True)
    subjectRepository = mongoengine.StringField(required=True)
    subjectNumber = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField()

    meta = {
        'db_alias': 'core',
        'collection': 'events.connected',
        'indexes': [
            {'fields': ['sourceRepository', 'sourceNumber', 'createdAt'], 'name': "timeline_index"}
        ]
    }
