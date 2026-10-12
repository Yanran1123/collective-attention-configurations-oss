import mongoengine
import datetime

from classes.github.issuecollection.edit import Edit
from classes.github.issuecollection.reactiongroup import ReactionGroup
from classes.github.issuecollection.timelineitem import TimelineItem


class Issue(mongoengine.Document):
    """
    Difference between small and big data set, i.e., between v1 (version 1) and v2 (version 2)
    1. Add reactionGroups

    We do not include the following information in GitHub Issue object
    1. hovercard, which is a third party tool which is not affiliated to GitHub (github.com);
        detail needed to display a hovercard for a user
    """

    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # Note that the following data files of issue correspond to the comment that propose the issue
    repository = mongoengine.StringField(required=True)  # owner/name
    number = mongoengine.IntField(required=True)
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
    
    closed = mongoengine.BooleanField(required=True)
    closedAt = mongoengine.DateTimeField()

    # --------------------------
    # Issue Content related
    title = mongoengine.StringField(required=True)
    body = mongoengine.StringField(required=True)
    bodyHTML = mongoengine.StringField(required=True)
    bodyText = mongoengine.StringField(required=True)

    # The actor who edited the comment; except for the author, collaborators of a repo can edit the issue
    # The edits are also like comments done by the author;
    # if the edits are included, people can see it on the webpage, otherwise people cannot see it on the webpage.
    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()
    # Check if this comment was edited and includes and edit with the creation data
    includesCreatedEdit = mongoengine.BooleanField(required=True)
    lastEditedAt = mongoengine.DateTimeField()

    editCount = mongoengine.IntField()
    edits = mongoengine.EmbeddedDocumentListField(Edit)
    # ----------------------
    # ReactionGroup
    reactionGroups = mongoengine.EmbeddedDocumentListField(ReactionGroup)

    # ----------------------
    # Timeline items
    timeline = mongoengine.EmbeddedDocumentListField(TimelineItem)

    # todo add the reactionGroups

    meta = {
        'db_alias': 'core',
        'collection': 'issues',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "basic_index"},
            {'fields': ['repository', 'createdAt'], 'name': "repo_createdAt_index"},
            {'fields': ['repository', 'number', 'timeline.eventType', 'timeline.createdAt'], 'name': "timeline_index"},
            {'fields': ['author', 'authorType', 'createdAt'], 'name': "author_index"}
        ]
    }
