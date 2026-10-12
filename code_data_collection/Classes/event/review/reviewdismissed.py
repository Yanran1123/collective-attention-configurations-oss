import datetime

import mongoengine


class ReviewDismissed(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    dismissalMessage = mongoengine.StringField()
    # Identifies the optional message associated with the 'review_dismissed' event.
    dismissalMessageHTML = mongoengine.StringField()
    # Identifies the optional message associated with the event, rendered to HTML.

    previousReviewState = mongoengine.StringField()

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    commitOid = mongoengine.StringField()  # Identifies the commit which caused the review to become stale.
    review = mongoengine.ObjectIdField()  # Identifies the review associated with the 'review_dismissed' event.

    meta = {
        'db_alias': 'core',
        'collection': 'events.reviewDismissed',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
