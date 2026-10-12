import datetime

import mongoengine


class ClosedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    # Closable: Issue, Milestone (identified by number; but in milestoned, it is titl),
    # Project(identified by number), or PullRequest
    closableType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    closableId = mongoengine.ObjectIdField(required=True)

    # Closer: Object which triggered the creation of this event -- Commit or PullRequest
    closerType = mongoengine.StringField()
    closerRepository = mongoengine.StringField()
    pullRequestNumber = mongoengine.IntField()
    commitOid = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'events.closed',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
