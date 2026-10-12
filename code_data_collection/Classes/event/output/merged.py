import datetime
import mongoengine


class Merged(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    commitOid = mongoengine.StringField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    mergeRefType = mongoengine.StringField()
    mergeRefName = mongoengine.StringField()
    mergeRefPrefix = mongoengine.StringField()
    mergeRefOid = mongoengine.StringField()  # Commit, tag, blob, or tree

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.merged',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
