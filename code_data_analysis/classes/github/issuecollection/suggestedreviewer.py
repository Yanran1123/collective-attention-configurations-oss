import mongoengine


class SuggestedReviewer(mongoengine.EmbeddedDocument):
    reviewer = mongoengine.StringField(required=True)  # login of the suggested user; only user?
    reviewerType = mongoengine.StringField()
    isAuthor = mongoengine.BooleanField(required=True)
    isCommenter = mongoengine.BooleanField(required=True)
