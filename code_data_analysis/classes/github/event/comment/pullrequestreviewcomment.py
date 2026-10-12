import datetime

import mongoengine

from classes.github.issuecollection.edit import Edit
from classes.github.issuecollection.reactiongroup import ReactionGroup


class PullRequestReviewComment(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    author = mongoengine.StringField()
    authorType = mongoengine.StringField()
    authorAssociation = mongoengine.StringField(required=True)
    """
    Values
    COLLABORATOR
    Author has been invited to collaborate on the repository.

    CONTRIBUTOR
    Author has previously committed to the repository.

    FIRST_TIMER
    Author has not previously committed to GitHub.

    FIRST_TIME_CONTRIBUTOR
    Author has not previously committed to the repository.

    MEMBER
    Author is a member of the organization that owns the repository.

    NONE
    Author has no association with the repository.

    OWNER
    Author is the owner of the repository.
    """

    commitOid = mongoengine.StringField()
    originalCommitOid = mongoengine.StringField()

    diffHunk = mongoengine.StringField(required=True)  # The diff hunk to which the comment applies
    path = mongoengine.StringField()  # The path to which the comment applies
    position = mongoengine.IntField()  # The line index in the diff to which the comment applies.
    originalPosition = mongoengine.IntField(required=True)

    outdated = mongoengine.BooleanField(required=True)

    state = mongoengine.StringField(required=True)  # The current state of the comment
    """
    PullRequestReviewCommentState
    The possible states of a pull request review comment.
    
    Values
    PENDING
    A comment that is part of a pending review
    
    SUBMITTED
    A comment that is part of a submitted review
    """

    createdAt = mongoengine.DateTimeField(required=True)
    createdViaEmail = mongoengine.BooleanField(required=True)
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField(required=True)
    draftedAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    isMinimized = mongoengine.BooleanField(required=True)
    minimizedReason = mongoengine.StringField()

    body = mongoengine.StringField(required=True)
    bodyHTML = mongoengine.StringField(required=True)
    bodyText = mongoengine.StringField(required=True)

    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()
    includesCreatedEdit = mongoengine.BooleanField(required=True)
    lastEditedAt = mongoengine.DateTimeField()
    editCount = mongoengine.IntField(required=True)

    # Only first 50 edits
    edits = mongoengine.EmbeddedDocumentListField(Edit)

    reactionGroups = mongoengine.EmbeddedDocumentListField(ReactionGroup)

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    pullRequestReviewId = mongoengine.ObjectIdField()  # The pullRequestReview associated with this review comment
    pullRequestReviewThreadId = mongoengine.ObjectIdField()  # The pullRequestReviewThread associated with this review comment
    replyToCommentId = mongoengine.ObjectIdField()  # The pullRequestReviewComment that is a reply to

    meta = {
        'db_alias': 'core',
        'collection': 'events.pullRequestReviewComment',
        'indexes': [
            {'fields': ['repository', 'commitOid', 'path', 'createdAt', 'body'], 'name': "timeline_index"}
        ]
    }

