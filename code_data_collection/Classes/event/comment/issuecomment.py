import datetime

import mongoengine

from Classes.issuecollection.edit import Edit
from Classes.issuecollection.reactiongroup import ReactionGroup


class IssueComment(mongoengine.Document):
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

    createdAt = mongoengine.DateTimeField(required=True)
    createdViaEmail = mongoengine.BooleanField(required=True)
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    # The issue that is been commented; note that pull requests also have issue comment
    subjectType = mongoengine.StringField(required=True)  # issue(required) or pullRequest
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

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

    edits = mongoengine.EmbeddedDocumentListField(Edit)

    reactionGroups = mongoengine.EmbeddedDocumentListField(ReactionGroup)

    meta = {
        'db_alias': 'core',
        'collection': 'events.issueComment',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }




