import mongoengine


class TimelineItem(mongoengine.EmbeddedDocument):

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField()  # PullRequestCommitComment and PullRequestReviewThread do not have createdAt
    eventType = mongoengine.StringField(required=True)
    eventId = mongoengine.ObjectIdField(required=True)
