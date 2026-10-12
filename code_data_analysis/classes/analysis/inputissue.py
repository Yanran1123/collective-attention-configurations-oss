import mongoengine


class InputIssue(mongoengine.Document):

    # Basic information
    issueType = mongoengine.StringField(required=True)  # Issue or PullRequest
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)  # number of the associated pull request
    createdAt = mongoengine.DateTimeField(required=True)    

    # Final Categories: BugReport, FeatureRequest, Documentation, or Question
    category = mongoengine.StringField()  # Labeled by developers; discarded; it includes enhancement as NewFeature

    # enhancement label is too ambiguous, can be documentation improvement also
    category1 = mongoengine.StringField()  # Remove checking the enhancement label
    label = mongoengine.StringField()  # With category1 and predictions info included
    isFeature = mongoengine.IntField()  # 1 if it's a new feature (category1 and predictions); otherwise 0

    # Issue or PullRequest event information
    eventId = mongoengine.ObjectIdField(required=True)
    eventUrl = mongoengine.StringField(required=True)

    # Text
    title = mongoengine.StringField()
    body = mongoengine.StringField()
    clean_title = mongoengine.StringField()
    clean_body = mongoengine.StringField()

    meta = {
        'db_alias': 'analysis',
        'collection': 'input_issues',
        'indexes': [
            {'fields': ['repository', 'number', 'issueType'], 'name': "basic_index"},
            {'fields': ['repository', 'createdAt'], 'name': "repoTime_index"},
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }