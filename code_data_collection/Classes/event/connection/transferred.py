import datetime

import mongoengine


# https://docs.github.com/en/github/managing-your-work-on-github/transferring-an-issue-to-another-repository
class TransferredEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    fromRepository = mongoengine.StringField()

    # The focal issue (can also be PullRequest because this event is also in timelineItems of a pullRequest), 
    # whose transferredEvents are checked
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.transferred',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
