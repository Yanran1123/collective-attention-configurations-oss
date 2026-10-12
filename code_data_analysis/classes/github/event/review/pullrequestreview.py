import datetime

import mongoengine

from classes.github.issuecollection.edit import Edit
from classes.github.issuecollection.reactiongroup import ReactionGroup


class PullRequestReview(mongoengine.Document):
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

    state = mongoengine.StringField(required=True)  # The current state of the pull request review
    """
    PullRequestReviewState
    The possible states of a pull request review.
    
    Values
    APPROVED
    A review allowing the pull request to merge.
    
    CHANGES_REQUESTED
    A review blocking the pull request from merging.
    
    COMMENTED
    An informational review.
    
    DISMISSED
    A review that has been dismissed.
    
    PENDING
    A review that has not yet been submitted.
    """

    commitOid = mongoengine.StringField()

    createdAt = mongoengine.DateTimeField(required=True)
    createdViaEmail = mongoengine.BooleanField(required=True)
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField(required=True)
    submittedAt = mongoengine.DateTimeField()

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

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

    onBehalfOfCount = mongoengine.IntField()
    onBehalfOfIds = mongoengine.ListField()  # object IDs of teams

    commentCount = mongoengine.IntField()
    reviewCommentIds = mongoengine.ListField()  # object Ids of pullRequestReviewComments

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.pullRequestReview',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
