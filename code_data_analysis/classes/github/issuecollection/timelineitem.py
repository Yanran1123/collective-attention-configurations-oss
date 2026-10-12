import mongoengine


class TimelineItem(mongoengine.EmbeddedDocument):

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField()  # PullRequestCommitComment and PullRequestReviewThread do not have createdAt
    eventType = mongoengine.StringField(required=True)
    eventId = mongoengine.ObjectIdField(required=True)

    """
    49 issue and pr events, plus "IssueCreated" and "PullRequestCreated"
    Note that I did not include the event "CommitCommentThread" and "PullRequestReviewThread", but included
    "CommitComment" and "PullRequestReviewComment"
    actionTypes = [
        "IssueCreated",
        "PullRequestCreated",
        "Commit",
        "AssignedEvent",
        "UnassignedEvent",
        "AutomaticBaseChangeFailed",
        "AutomaticBaseChangeSucceeded",
        "BaseRefChanged",
        "BaseRefForcePushed",
        "HeadRefDeleted",
        "HeadRefForcePushed",
        "HeadRefRestored",
        "CommentDeletedEvent",
        "CommitComment",
        "IssueComment",
        "PullRequestReviewComment",
        "ConnectedEvent",
        "CrossReferencedEvent",
        "DisconnectedEvent",
        "ReferencedEvent",
        "TransferredEvent",
        "Deployed",
        "DeploymentEnvironmentChanged",
        "LabeledEvent",
        "UnlabeledEvent",
        "MentionedEvent",
        "DemilestonedEvent",
        "MilestonedEvent",
        "Merged",
        "ClosedEvent",
        "LockedEvent",
        "MarkedAsDuplicateEvent",
        "PinnedEvent",
        "ReopenedEvent",
        "UnlockedEvent",
        "UnmarkedAsDuplicateEvent",
        "UnpinnedEvent",
        "AddedToProjectEvent",
        "ConvertedNoteToIssueEvent",
        "MovedColumnsInProjectEvent",
        "RemovedFromProjectEvent",
        "ConvertToDraft",
        "PullRequestReview",
        "ReadyForReview",
        "ReviewDismissed",
        "ReviewRequested",
        "ReviewRequestRemoved",
        "SubscribedEvent",
        "UnsubscribedEvent",
        "RenamedTitleEvent",
        "UserBlockedEvent"
    ]
    """

