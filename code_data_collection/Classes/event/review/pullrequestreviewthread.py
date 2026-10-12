import datetime

import mongoengine


class PullRequestReviewThread(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    isResolved = mongoengine.BooleanField(required=True)

    line = mongoengine.IntField()  # The line in the file to which this thread refers
    startLine = mongoengine.IntField()  # The start line in the file to which this thread refers (multi-line only)
    originalLine = mongoengine.IntField()  # The original line in the file to which this thread refers
    originalStartLine = mongoengine.IntField()
    # The original start line in the file to which this thread refers (multi-line only).

    resolvedBy = mongoengine.StringField()  # The user who resolved this thread
    resolvedByType = mongoengine.StringField()

    diffSide = mongoengine.StringField(required=True)  # The side of the diff on which this thread was placed
    """
    DiffSide
    The possible sides of a diff.
    
    Values
    LEFT
    The left side of the diff.
    
    RIGHT
    The right side of the diff.
    """
    startDiffSide = mongoengine.StringField()
    # The side of the diff that the first line of the thread starts on (multi-line only)

    commentCount = mongoengine.IntField(required=True)
    reviewCommentIds = mongoengine.ListField()  # object Ids of pullRequestReviewComments

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.pullRequestReviewThread',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "pr_index"}
        ]
    }
