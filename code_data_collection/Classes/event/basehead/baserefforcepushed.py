import datetime
import mongoengine


class BaseRefForcePushed(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    refName = mongoengine.StringField()
    refPrefix = mongoengine.StringField()
    refOid = mongoengine.StringField()
    beforeCommitOid = mongoengine.StringField()
    afterCommitOid = mongoengine.StringField()

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.baseRefForcePushed',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
