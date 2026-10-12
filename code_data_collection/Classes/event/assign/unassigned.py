import datetime
import mongoengine


class UnassignedEvent(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    # Assignee identifies the user or mannequin that was assigned.
    assignee = mongoengine.StringField()
    assigneeType = mongoengine.StringField()

    # The assignable associated with the event
    assignableType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    assignableId = mongoengine.ObjectIdField(required=True)  # The object ID of the associated issue/pullRequest

    meta = {
        'db_alias': 'core',
        'collection': 'events.unassigned',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
