"""
To open a pull request in a public repository, you must have write access to the head or the source branch or,
for organization-owned repositories, you must be a member of the organization that owns the repository to
open a pull request.
"""

import mongoengine
import datetime

from Classes.issuecollection.associatedPR import AssociatedPR
from Classes.issuecollection.edit import Edit
from Classes.issuecollection.changedfile import ChangedFile
from Classes.issuecollection.suggestedreviewer import SuggestedReviewer
from Classes.issuecollection.timelineitem import TimelineItem


class PullRequest(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # Note that the following data files of pull request correspond to the comment that propose the pull request
    repository = mongoengine.StringField(required=True)  # owner/name
    number = mongoengine.IntField(required=True)
    author = mongoengine.StringField()
    authorType = mongoengine.StringField()
    authorAssociation = mongoengine.StringField()

    createdAt = mongoengine.DateTimeField()
    createdViaEmail = mongoengine.BooleanField()
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField()

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField()
    url = mongoengine.StringField()
    permalink = mongoengine.StringField()  # The permanent static hyperlink to this pull request
    revertResourcePath = mongoengine.StringField()  # The HTTP path for reverting this pull request
    revertUrl = mongoengine.StringField()

    maintainerCanModify = mongoengine.BooleanField()  # Whether maintainers can modify the pull request

    baseRefName = mongoengine.StringField()
    # GitObject id of the commit the base refers to
    baseRefOid = mongoengine.StringField()
    # nameWithOwner filed of the repository associated with this pull request's base ref
    baseRepository = mongoengine.StringField()  # owner/name
    baseAssociatedPRs = mongoengine.EmbeddedDocumentListField(AssociatedPR)

    headRefName = mongoengine.StringField()
    headRefOid = mongoengine.StringField()
    headRepository = mongoengine.StringField()  # owner/name
    headAssociatedPRs = mongoengine.EmbeddedDocumentListField(AssociatedPR)

    additions = mongoengine.IntField()
    deletions = mongoengine.IntField()
    # The number of changed files in this pull request
    changedFilesCount = mongoengine.IntField()
    changedFiles = mongoengine.EmbeddedDocumentListField(ChangedFile)

    # Information for the checks of this pull request
    checksResourcePath = mongoengine.StringField()
    checksUrl = mongoengine.StringField()

    closed = mongoengine.BooleanField()
    closedAt = mongoengine.DateTimeField()

    # GitObject id the merge commit
    mergeCommit = mongoengine.StringField()  # Git object id of the merge commit
    # mergeStateStatus = mongoengine.StringField()  # This access is changed
    """
    Values
    BEHIND
    The head ref is out of date.
    
    BLOCKED
    The merge is blocked.
    
    CLEAN
    Mergeable and passing commit status.
    
    DIRTY
    The merge commit cannot be cleanly created.
    
    DRAFT
    The merge is blocked due to the pull request being a draft.
    
    HAS_HOOKS
    Mergeable with passing commit status and pre-receive hooks.
    
    UNKNOWN
    The state cannot currently be determined.
    
    UNSTABLE
    Mergeable with non-passing commit status.
    """
    mergeable = mongoengine.StringField()
    """
    Values
    CONFLICTING
    The pull request cannot be merged due to merge conflicts.
    
    MERGEABLE
    The pull request can be merged.
    
    UNKNOWN
    The mergeability of the pull request is still being calculated.
    """
    merged = mongoengine.BooleanField()
    mergedAt = mongoengine.StringField()
    mergedBy = mongoengine.StringField()  # login of the actor
    mergedByType = mongoengine.StringField()  # type of the actor who merged this pull request

    # --------------------------
    # Pull-Request Content related
    title = mongoengine.StringField()
    body = mongoengine.StringField()
    bodyHTML = mongoengine.StringField()
    bodyText = mongoengine.StringField()

    # The actor who edited the comment; except for the author, collaborators of a repo can edit the issue
    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()
    # Check if this comment was edited and includes and edit with the creation data
    includesCreatedEdit = mongoengine.BooleanField()
    lastEditedAt = mongoengine.DateTimeField()
    # userContentEdits
    editCount = mongoengine.IntField()
    edits = mongoengine.EmbeddedDocumentListField(Edit)
    # --------------------------

    suggestedReviewers = mongoengine.EmbeddedDocumentListField(SuggestedReviewer)

    # Timeline items
    timeline = mongoengine.EmbeddedDocumentListField(TimelineItem)

    # todo add the reactionGroups

    meta = {
        'db_alias': 'core',
        'collection': 'prs',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "basic_index"}
        ]
    }
