import datetime

import mongoengine


# Convert a note on project card to issue
class ConvertedNoteToIssueEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField()

    databaseId = mongoengine.IntField()

    # Those fields are not actually available in the API
    projectNumber = mongoengine.IntField()
    projectCardUrl = mongoengine.StringField()
    projectColumnName = mongoengine.StringField()

    # The issue or pullRequest associated with the event
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.convertedNoteToIssue',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
