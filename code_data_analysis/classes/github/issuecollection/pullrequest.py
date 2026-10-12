"""
To open a pull request in a public repository, you must have write access to the head or the source branch or,
for organization-owned repositories, you must be a member of the organization that owns the repository to
open a pull request.
"""

import mongoengine
import datetime

from classes.github.issuecollection.associatedPR import AssociatedPR
from classes.github.issuecollection.edit import Edit
from classes.github.issuecollection.changedfile import ChangedFile
from classes.github.issuecollection.reactiongroup import ReactionGroup
from classes.github.issuecollection.suggestedreviewer import SuggestedReviewer
from classes.github.issuecollection.timelineitem import TimelineItem


class PullRequest(mongoengine.Document):
    """
    Difference between small and big data set, i.e., between v1 (version 1) and v2 (version 2)
    1. Add reactionGroups
    2. Exclude baseAssociatedPRs and headAssociatied PRs
        reason 1: Some pullRequests have long base or head associatedPRs, which slows down the progress
        reason 2: The information can be easily found (by prs with the same baseRefOid or headRefOid)
                if we need to recognize the connection among prs
        reason 3: It does not make sense why we need to get information about prs with this baseRef or headRef
                as the "head" ref

    We do not include the following information in GitHub PullRequest object
    1. hovercard, which is a third party tool which is not affiliated to GitHub (github.com);
    detail needed to display a hovercard for a user
    2. potentialMergeCommit, i.e., The commit that GitHub automatically generated to test if this pull request could
    be merged. This field will not return a value if the pull request is merged, or if the test merge commit is
    still being generated. See the mergeable field for more details on the mergeability of the pull request.
        reason 1: It sounds like a temporary attribute
    """
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    # Note that the following data files of pull request correspond to the comment that propose the pull request
    repository = mongoengine.StringField(required=True)  # owner/name
    number = mongoengine.IntField(required=True)
    author = mongoengine.StringField()
    authorType = mongoengine.StringField()
    authorAssociation = mongoengine.StringField(required=True)

    createdAt = mongoengine.DateTimeField(required=True)
    createdViaEmail = mongoengine.BooleanField(required=True)
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)
    permalink = mongoengine.StringField(required=True)  # The permanent static hyperlink to this pull request
    revertResourcePath = mongoengine.StringField(required=True)  # The HTTP path for reverting this pull request
    revertUrl = mongoengine.StringField(required=True)

    maintainerCanModify = mongoengine.BooleanField(required=True)  # Whether maintainers can modify the pull request

    baseRefName = mongoengine.StringField(required=True)
    # Identifies the oid of the base ref associated with the pull request, even if the ref has been deleted.
    baseRefOid = mongoengine.StringField(required=True)
    # nameWithOwner filed of the repository associated with this pull request's base ref
    baseRepository = mongoengine.StringField()  # owner/name
    # A list of pull requests with this baseRef as the [head ref??]
    baseAssociatedPRs = mongoengine.EmbeddedDocumentListField(AssociatedPR)

    headRefName = mongoengine.StringField(required=True)
    # Identifies the oid of the head ref associated with the pull request, even if the ref has been deleted.
    headRefOid = mongoengine.StringField(required=True)
    headRepository = mongoengine.StringField()  # owner/name
    # A list of pull requests with this headRef as the [head ref??]
    headAssociatedPRs = mongoengine.EmbeddedDocumentListField(AssociatedPR)

    additions = mongoengine.IntField(required=True)
    deletions = mongoengine.IntField(required=True)
    # The number of files changed by this pull request
    changedFilesCount = mongoengine.IntField(required=True)

    # Information for the checks of this pull request
    checksResourcePath = mongoengine.StringField(required=True)
    checksUrl = mongoengine.StringField(required=True)

    closed = mongoengine.BooleanField(required=True)
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
    # Whether or not the pull request can be merged based on the existence of merge conflicts.
    mergeable = mongoengine.StringField(required=True)
    """
    Values
    CONFLICTING
    The pull request cannot be merged due to merge conflicts.
    
    MERGEABLE
    The pull request can be merged.
    
    UNKNOWN
    The mergeability of the pull request is still being calculated.
    """
    merged = mongoengine.BooleanField(required=True)
    mergedAt = mongoengine.StringField()
    mergedBy = mongoengine.StringField()  # login of the actor
    mergedByType = mongoengine.StringField()  # type of the actor who merged this pull request

    # --------------------------
    # Pull-Request Content related
    title = mongoengine.StringField(required=True)
    body = mongoengine.StringField(required=True)
    bodyHTML = mongoengine.StringField(required=True)
    bodyText = mongoengine.StringField(required=True)

    # The actor who edited the comment; except for the author, collaborators of a repo can edit the issue
    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()
    # Check if this comment was edited and includes and edit with the creation data
    includesCreatedEdit = mongoengine.BooleanField(required=True)
    lastEditedAt = mongoengine.DateTimeField()
    editCount = mongoengine.IntField()
    
    # --------------------------
    # ReactionGroups
    reactionGroups = mongoengine.EmbeddedDocumentListField(ReactionGroup)

    # --------------------------
    # userContentEdits
    edits = mongoengine.EmbeddedDocumentListField(Edit)

    # --------------------------
    # File changes
    changedFiles = mongoengine.EmbeddedDocumentListField(ChangedFile)

    # --------------------------
    # SuggestedReviewers
    suggestedReviewers = mongoengine.EmbeddedDocumentListField(SuggestedReviewer)

    # --------------------------
    # Timeline items
    timeline = mongoengine.EmbeddedDocumentListField(TimelineItem)

    meta = {
        'db_alias': 'core',
        'collection': 'prs',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "basic_index"},
            {'fields': ['repository', 'createdAt'], 'name': "repo_createdAt_index"},
            {'fields': ['repository', 'number', 'timeline.eventType', 'timeline.createdAt'], 'name': "timeline_index"},
            {'fields': ['author', 'authorType', 'createdAt'], 'name': "author_index"}
        ]
    }
