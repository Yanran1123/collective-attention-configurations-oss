import mongoengine


class SuggestedReviewer(mongoengine.EmbeddedDocument):
    reviewer = mongoengine.StringField()  # login of the suggested user; only user?
    reviewerType = mongoengine.StringField()
    isAuthor = mongoengine.BooleanField()
    isCommenter = mongoengine.BooleanField()