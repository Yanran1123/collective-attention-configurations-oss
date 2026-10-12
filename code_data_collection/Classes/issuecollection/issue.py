import mongoengine
import datetime

from Classes.issuecollection.edit import Edit
from Classes.issuecollection.timelineitem import TimelineItem


class Issue(mongoengine.Document):

    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # Note that the following data files of issue correspond to the comment that propose the issue
    repository = mongoengine.StringField(required=True)  # owner/name
    number = mongoengine.IntField(required=True)
    author = mongoengine.StringField()
    authorType = mongoengine.StringField()
    authorAssociation = mongoengine.StringField()
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

    createdAt = mongoengine.DateTimeField()
    createdViaEmail = mongoengine.BooleanField()

    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField()

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField()
    url = mongoengine.StringField()
    
    closed = mongoengine.BooleanField()
    closedAt = mongoengine.DateTimeField()

    # --------------------------
    # Issue Content related
    title = mongoengine.StringField()
    body = mongoengine.StringField()
    bodyHTML = mongoengine.StringField()
    bodyText = mongoengine.StringField()

    # The actor who edited the comment; except for the author, collaborators of a repo can edit the issue
    # The edits are also like comments done by the author;
    # if the edits are included, people can see it on the webpage, otherwise people cannot see it on the webpage.
    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()
    # Check if this comment was edited and includes and edit with the creation data
    includesCreatedEdit = mongoengine.BooleanField()
    lastEditedAt = mongoengine.DateTimeField()

    editCount = mongoengine.IntField()
    edits = mongoengine.EmbeddedDocumentListField(Edit)
    # ----------------------

    # Timeline items
    timeline = mongoengine.EmbeddedDocumentListField(TimelineItem)

    # todo add the reactionGroups

    meta = {
        'db_alias': 'core',
        'collection': 'issues',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "basic_index"}
        ]
    }
