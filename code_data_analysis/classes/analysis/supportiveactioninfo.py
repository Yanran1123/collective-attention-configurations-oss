import mongoengine


class SupportiveAction(mongoengine.Document):

    actionId = mongoengine.ObjectIdField(required=True)  # id in the db1_small (MongoDB)
    actionType = mongoengine.StringField(required=True)  # 51 types in total
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

    actorLogin = mongoengine.StringField(required=True)  # For Alien, it is the email address
    actorType = mongoengine.StringField(required=True)  # Alien, Bot, Organization, User （in our sample）
    """
    Notes:
    1. The actor and actorType of an action can be '' or None; 
    2. If the action is an commit, issueComment, pullRequestReview, commitComment, or pullRequestReviewComment,
        the actor is the author! (not the committer for a specific commit) 
    """
    actorAssociation = mongoengine.StringField()
    """
    Values for Comment type of events: IssueCreated, PullRequestCreated, CommitComment, IssueComment,
        PullRequestReviewComment and PullRequestReview
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

    repository = mongoengine.StringField(required=True)
    subjectType = mongoengine.StringField()  # PullRequest or Issue
    number = mongoengine.IntField()

    createdAt = mongoengine.DateTimeField()  # No missing value
    publishedAt = mongoengine.DateTimeField()  # has many missing values
    updatedAt = mongoengine.DateTimeField()  # has many missing values

    # ********************
    # R3: Text, sentiment scores, isToxic information of each comment
    commentText = mongoengine.StringField()  # The body text of each comment
    # Use TextBlob, which is a simpler library for processing textual data and can also be used for sentiment analysis
    polarity = mongoengine.FloatField()  # -1 negative, 1 positive, neutral 0
    subjectivity = mongoengine.FloatField()  # The higher the value, the more subjective
    # Use NLTK  and VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon 
    #   and rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media
    neg = mongoengine.FloatField()  # Negativity, 0 to 1
    neu = mongoengine.FloatField()  # Neutrality, 0 to 1
    pos = mongoengine.FloatField()  # Positivity, 0 to 1
    compound = mongoengine.FloatField()  # Compound score, -1 (most negative) to 1 (most positive)

    # From an online Hackathon
    isToxic = mongoengine.IntField()  # 1 if Toxic, otherwise not toxic; threshold possibility is 0.6 for any
        # one of the labels: 'Hate', 'Insult', 'Obscene', 'Severe Toxic', 'Threat', 'Toxic'

    meta = {
        'db_alias': 'analysis',
        'collection': 'supportive_actions',
        'indexes': [
            {'fields': ['repository', 'subjectType', 'number'], 'name': "subject_index"},
            {'fields': ['actionType', 'actionId'], 'name': "actionType_index"},
            {'fields': ['actorType', 'actorLogin'], 'name': "actorType_index"},
            {'fields': ['actionId'], 'name': "actionId_index"},
            {'fields': ['actorLogin'], 'name': "actorLogin_index"},
            {'fields': ['createdAt'], 'name': "time_index"}
        ]
    }
