import mongoengine


class InnovationOutput(mongoengine.Document): # Created based on Merged event

    # Basic information
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)  # number of the associated pull request
    createdAt = mongoengine.DateTimeField(required=True)  # when a Merged event happens
    isToDefaultBranch = mongoengine.BooleanField()

    # Categories: BugFixing, NewFeature, or Documentation
    # Note that feature should be feature enhancement or new feature
    category = mongoengine.StringField()  # Labeled by developers; discarded; it includes enhancement as NewFeature
    
    # enhancement label is too ambiguous, can be documentation improvement also
    category1 = mongoengine.StringField()  # Used as y in prediction; Remove checking the enhancement label
    label = mongoengine.StringField()  # With category1 and predicted values: BugFixing, NewFeature, Documentation
    isFeature = mongoengine.IntField()  # 1 if it's a new feature (category1 and predictions); otherwise 0

    # MergedEven information
    mergedCommitOid = mongoengine.StringField(required=True)
    mergedCommitMessage = mongoengine.StringField()  # Used for classification
    mergedEventId = mongoengine.ObjectIdField(required=True)
    mergedEventUrl = mongoengine.StringField(required=True)

    # Changed information by comparing the mergedCommit and the baseCommit of the pr
    changedFilesCount = mongoengine.IntField()
    additions = mongoengine.IntField()
    deletions = mongoengine.IntField()

    # Text
    title = mongoengine.StringField()  # Used for classification
    body = mongoengine.StringField()  # Used for classification
    clean_mergedCommitMessage = mongoengine.StringField()
    clean_title = mongoengine.StringField()
    clean_body = mongoengine.StringField()

    # Milestone
    milestoned_output = mongoengine.IntField()  
        # For release cycles that has milestone events, 1 if the output is included into a milestone; otherwise 0;
        # data for trainDF (as to release cycles with no milestone events, we included its outputs into toBePredictedDF)
    predMilestoned_output = mongoengine.IntField()  
        # 1 if an output is predicted to be included into a milestone; otherwise, 0

    meta = {
        'db_alias': 'analysis',
        'collection': 'innovation_outputs',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"},
            {'fields': ['repository', 'createdAt'], 'name': "timeline_index1"},
            {'fields': ['repository', 'createdAt', 'label'], 'name': "timeline_index2"}
        ]
    }