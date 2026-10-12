import mongoengine

from classes.github.issuecollection.changedfile import ChangedFile


class RepoByReleaseCycle(mongoengine.Document):
    # Information about the release cycle
    # The release should not be a draft; it may be a pre-release (not ready for production and may be unstable)
    repository = mongoengine.StringField(required=True)
    isPrerelease = mongoengine.BooleanField(required=True)
    tagName = mongoengine.StringField(required=True)
    name = mongoengine.StringField()
    tagCommitOid = mongoengine.StringField()
    author = mongoengine.StringField()
    description = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    updatedAt = mongoengine.DateTimeField()

    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle
    startTime = mongoengine.DateTimeField(required=True)  # The time when last release is published
    endTime = mongoengine.DateTimeField(required=True)  # The time when the focal release is published
    days = mongoengine.IntField(required=True)  # How many days are there in the release cycle

    startCommitOid = mongoengine.StringField()  # The most recent defaultBranch commit before startTime; can be None
    endCommitOid = mongoengine.StringField(required=True)  # The most recent defaultBranch commit before endCommitOid

    # -----------------------------------------------
    # Information about innovation productivity
    novelty_changedFiles = mongoengine.EmbeddedDocumentListField(ChangedFile)  # Not sure whether it is easy to get
    novelty_changedFilesCount = mongoengine.IntField()  # Compare the startCommit and endCommit in the default branch
    novelty_changedLines = mongoengine.IntField()
    novelty_additions = mongoengine.IntField()
    novelty_deletions = mongoengine.IntField()

    speed_mergedEventCount = mongoengine.IntField()  # How many merge events happen during the release cycle
    speed_mergeCommitCount = mongoengine.IntField()  # How many merged commits there are
    mergeCommitAllowed_Jun2020 = mongoengine.BooleanField()  # The status of whether mergeCommits are allowed when collecting repoInfo

    novelty_aveChangedFiles = mongoengine.FloatField()  # Average the changed files of each Merged event
    novelty_aveChangedLines = mongoengine.FloatField()  # Average the changed lines of each Merged event

    # ----------------------------------------------
    # Information about contingencies: availability of developers
    num_developers = mongoengine.IntField()  # The number of developers who have conducted innovative actions during the release cycle
    # The following values are -999, if no developers are involved
    tenure_disparity_releaseCycle = mongoengine.FloatField()  # The tenure disparity of involved developers by joining releaseCycle
    tenure_disparity_month = mongoengine.FloatField()  # The tenuer disparity of involved developers by joining month

    # ----------------------------------------------
    # Information about contingencies: input issues
    num_issues = mongoengine.IntField()  # The number of issues that have been open during the release cycle
    num_newIssues = mongoengine.IntField()  # The number of issues that are created during the release cycle
    
    num_bugs = mongoengine.IntField()  # The number of input issues that are bugs
    num_features = mongoengine.IntField()  # The number of input issues that are feature requests
    num_newBugs = mongoengine.IntField()  # The number of new input issues that are bugs
    num_newFeatures = mongoengine.IntField()  # The number of new input issues that are feature requests

    # ----------------------------------------------
    # Information about contingencies: initial shared codebase (files)
    num_files = mongoengine.IntField()  # The number of files
    linesPerFile = mongoengine.FloatField()  # The number of lines per file
    total_lines = mongoengine.IntField()  # The total lines of all files
    count_negativeLines = mongoengine.IntField()  # How many files have negative lines

    # Information about project stage, how many months elapsed
    # between when the repo is created and when the cycle starts
    project_stage = mongoengine.IntField()

    # ----------------------------------------------
    # !! Information about collective attention
    attentionPrioritization_issues = mongoengine.FloatField()
    attentionPrioritization_files = mongoengine.FloatField()

    attentionPartition_issues = mongoengine.FloatField()  # base_threshold = 100 lines of code change
    attentionPartition_files = mongoengine.FloatField()  # base_threshold = 100
    num_engagedDevelopers = mongoengine.IntField()  # base_threshold = 100

    attentionPartition_issues1 = mongoengine.FloatField()  # base_threshold = 50 lines of code change
    attentionPartition_files1 = mongoengine.FloatField()  # base_threshold = 50
    num_engagedDevelopers1 = mongoengine.IntField()  # base_threshold = 50

    attentionPartition_issues2 = mongoengine.FloatField()  # base_threshold = 1 lines of code change
    attentionPartition_files2 = mongoengine.FloatField()  # base_threshold = 1
    num_engagedDevelopers2 = mongoengine.IntField()  # base_threshold = 1

    # *********************************************************************************
    # From here: Second Round Analysis

    num_actions = mongoengine.IntField()  # The total number of innovative actions for prs in the cycle

    # -----------------------------------
    # Innovation productivity
    total_outputs = mongoengine.IntField()  # The total number of innovation outputs produced
    total_features = mongoengine.IntField()  # The total number of features produced
    total_changedLines = mongoengine.IntField()  # The total number of lines changed from base to merged commit
    total_featureChangedLines = mongoengine.IntField()  # The total number of lines changed for features

    speed1 = mongoengine.FloatField()  # total_outputs / days
    speed2 = mongoengine.FloatField()  # total_features / days

    novelty1 = mongoengine.FloatField()  # total_changedLines / total_outputs
    novelty2 = mongoengine.FloatField()  # total_featureChangedLines / total_features
    novelty3 = mongoengine.FloatField()  # total_features / total_outputs

    # -----------------------------------
    # developers contingencies: 
    #   num_developers
    tenure_disparity_month1 = mongoengine.FloatField()  # Identify the time of the first commit as the start

    # -----------------------------------
    # input-issue contingencies: 
    #   num_issues  # Number of issues (including prs) that have been open during the release cycle
    num_involvedIssues = mongoengine.IntField()  # The number of issues that developers have worked on
    proportion_featureRequests = mongoengine.FloatField()  # Number of feature requests / num_issues
  
    # -----------------------------------
    # involved-file contingencies:
    num_involvedFiles = mongoengine.IntField()  # The number of files developers have changed during the period

    # -----------------------------------
    # project_stage

    # -----------------------------------
    # collective attention: 
    #   attentionPrioritization_issues, 
    #   attentionPrioritization_files, 
    #   attentionPartition_issues2, 
    #   attentionPartition_files2
 
    meta = {
        'db_alias': 'analysis',
        'collection': 'repoByReleaseCycle_2539',
        'indexes': [
            {'fields': ['repository'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber'], 'name': "basic1_index"}
        ]
    }

