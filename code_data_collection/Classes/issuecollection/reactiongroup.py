import datetime

import mongoengine


class ReactionGroup(mongoengine.EmbeddedDocument):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    content = mongoengine.StringField(required=True)
    """
    Values
    CONFUSED
    Represents the :confused: emoji.
    
    EYES
    Represents the :eyes: emoji.
    
    HEART
    Represents the :heart: emoji.
    
    HOORAY
    Represents the :hooray: emoji.
    
    LAUGH
    Represents the :laugh: emoji.
    
    ROCKET
    Represents the :rocket: emoji.
    
    THUMBS_DOWN
    Represents the :-1: emoji.
    
    THUMBS_UP
    Represents the :+1: emoji.
    """
    createdAt = mongoengine.DateTimeField()
    userCount = mongoengine.IntField()  # How many users react the certain content

    # The subject that was reacted to; as this is an embedded document, we don't need this information
    # subjectType = mongoengine.StringField(required=True)
    # subjectID = mongoengine.ObjectIdField()
    """
    CommitComment
    Issue
    IssueComment
    PullRequest
    PullRequestReview
    PullRequestReviewComment
    TeamDiscussion
    TeamDiscussionComment
    """
