import datetime

import mongoengine


# Represents a mention made by one issue or pull request to another
class CrossReferencedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)  # Identifies when the object was created
    referencedAt = mongoengine.DateTimeField(required=True)  # Identifies when the reference was made

    resourcePath = mongoengine.StringField(required=True)  # The HTTP path for this pull request (?)
    url = mongoengine.StringField(required=True)  # The HTTP URL for this pull request

    isCrossRepository = mongoengine.BooleanField(required=True)  # reference originated in a different repo
    willCloseTarget = mongoengine.BooleanField(required=True)

    # source: Issue or pull request that made the reference
    # An issue that is different from the focal issue
    sourceType = mongoengine.StringField(required=True)
    sourceRepository = mongoengine.StringField(required=True)
    sourceNumber = mongoengine.IntField(required=True)
    sourceId = mongoengine.ObjectIdField()

    # target: Issue or pull request to which the reference was made
    # The focal issue. For instance, if we check the CrossReferencedEvent of issue #22 of tensorflow/tensorflow, 
    # the target includes information about this issue
    targetType = mongoengine.StringField(required=True)
    targetRepository = mongoengine.StringField(required=True)
    targetNumber = mongoengine.IntField(required=True)
    targetId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.crossReferenced',
        'indexes': [
            {'fields': ['targetRepository', 'targetNumber', 'createdAt'], 'name': "timeline_index"}
        ]
    }
