import datetime
import mongoengine

# todo Use REST URL to fetch comments related to a commit?
from classes.github.issuecollection.edit import Edit
from classes.github.issuecollection.reactiongroup import ReactionGroup


class CommitComment(mongoengine.Document):
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
    path = mongoengine.StringField()  # The file path associated with the comment
    position = mongoengine.IntField()  # The line position associated with the comment

    # This repository seems to be the repository of the commit, but it is not necessarily the same as the 
    #   corresponding commitCommentThread
    repository = mongoengine.StringField(required=True)

    createdAt = mongoengine.DateTimeField(required=True)
    createdViaEmail = mongoengine.BooleanField(required=True)
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField(required=True)

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

    meta = {
        'db_alias': 'core',
        'collection': 'events.commitComment',
        'indexes': [
            {'fields': ['repository', 'commitOid', 'path', 'createdAt', 'body'], 'name': "timeline_index"}
        ]
    }
