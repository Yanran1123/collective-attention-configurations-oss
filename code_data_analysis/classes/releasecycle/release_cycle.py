from typing import Any

import mongoengine

"""
Notes:
1. Carefully check whether the connected collection in MongoDB is correct
2. There are five classes
"""


class ReleaseCycleInvolvedDeveloper(mongoengine.Document):
    # ----------------------
    # BASICS
    repository = mongoengine.StringField(required=True)
    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle

    actorType = mongoengine.StringField(required=True)
    login = mongoengine.StringField(required=True)
    actorType_login = mongoengine.StringField(required=True)  # user_login or org_login

    # tenure
    firstCommitTime = mongoengine.DateTimeField()  # DateTime when the developer made the first commit for the repository
    tenure = mongoengine.IntField()  # 0 if firstCommitTime >= startTime; otherwise, days between the two time points
    code_exp = mongoengine.FloatField()  # number of commits the developer made before the release cycle

    # CODE Summary
    contribution_code = mongoengine.IntField()  # How many lines the developer changed in the focal release cycle
    contribution_codeAdded = mongoengine.IntField()  # How many lines the developer added in the release cycle
    # observation of attention focus on existing modules [status--added, modified, removed, renamed--in changedFile of a commit]
    pro_addedFiles = mongoengine.FloatField()  # files added by the developer / all files worked on by the developer
    pro_removedFiles = mongoengine.FloatField()  # files removed by the developer / all files worked on by the developer
    addedFiles = mongoengine.ListField()
    removedFiles = mongoengine.ListField()
    modifiedFiles = mongoengine.ListField()
    renamedFiles = mongoengine.ListField()

    #COMMENT Summary
    contribution_comment = mongoengine.IntField()  # Num of comments the developer made in the release cycle   
    # observation of attention focus on issues
    contribution_comment_issues = mongoengine.IntField()  # Num of comments the developer made for issues
    contribution_IssueComment = mongoengine.IntField()  # Num of issueComments that the developer made

    # ----------------------
    # ATTENTION DISTRIBUTION
    # Comment-based; in sample3_issueCodeComment, attention to an issue is the sum of comments and commits
    num_issues = mongoengine.IntField()  # The number of issues on which this developer has commented
        # issue here means: issues + prs with no issue connection in the focal release cycle
    primaryIssues = mongoengine.ListField()  # Issues (['issue_ or pr_number', numComments]) with most comments from the dev 
    num_primaryIssues = mongoengine.IntField()  # The number of attentive (primary) issues this developer has
    secondaryIssues = mongoengine.ListField()  # Issues (['issue_ or pr_number', linesChanged]) with comments from the dev
    num_secondaryIssues = mongoengine.IntField()  # The number of attentive (primary) issues this developer has
    pro_secondaryIssueOverlap = mongoengine.FloatField()  # The proportion of issues in thesecondary focus that overlaps others' attention
    primaryRate_issue = mongoengine.FloatField()  # The proportion of comments taken by primary issues

    pro_primaryIssueOverlap = mongoengine.FloatField()  # The proportion of issues in the primary focus that overlaps others' primary focus

    # Code-based
    num_files = mongoengine.IntField()  # The number of files on which this developer has worked
    primaryFiles = mongoengine.ListField()  # Files ([path, linesChanged]) with the developers' highest lines of change
    num_primaryFiles = mongoengine.IntField()  # The number of attentive (primary) files this developer has
    secondaryFiles = mongoengine.ListField()  # Files ([path, linesChanged]) with the developers' lines of change
    num_secondaryFiles = mongoengine.IntField()  # The number of attentive (primary) files this developer has
    pro_secondaryFileOverlap = mongoengine.FloatField()  # The proportion of files in the secondary focus that overlaps others' attention
    primaryRate_file = mongoengine.FloatField()  # The proportion of changed lines taken by attentive files

    pro_primaryFileOverlap = mongoengine.FloatField()  # The proportion of files in the primary focus that overlaps others' primary focus
   
    # Code-based
    num_modules = mongoengine.IntField()  # The number of modules on which this developer has worked
    primaryModules = mongoengine.ListField()  # Modules ([path, linesChanged]) with the developers' highest lines of change
    num_primaryModules = mongoengine.IntField()  # The number of attentive (primary) modules this developer has
    secondaryModules = mongoengine.ListField()  # Modules ([path, linesChanged]) with the developers' lines of change
    num_secondaryModules = mongoengine.IntField()  # The number of attentive (primary) modules this developer has
    pro_scondaryModuleOverlap = mongoengine.FloatField()  # The proportion of modules in the secondary focus that overlaps others' attention
    primaryRate_module = mongoengine.FloatField()  # The proportion of changed lines taken by attentive modules

    pro_primaryModuleOverlap = mongoengine.FloatField()  # The proportion of modules in the primary focus that overlaps others' primary focus

    # ----------------------
    # ORIENTATION
    orient_bugs_comment = mongoengine.FloatField()  # Orientation: Ratio of comments on bug reports of issues
    orient_features_comment = mongoengine.FloatField()  # Orientation: Ratio of comments on feature requests of issues
    orient_bugs_code = mongoengine.FloatField()  # Orientation: Ratio of code changes allocated to bug reports
    orient_features_code = mongoengine.FloatField()  # Orientation: Ratio of code changes allocated to feature requests

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0_invDevelopers',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber', 'actorType_login'], 'name': "basic_index2"}
        ]
    }


class ReleaseCycleInvolvedIssue(mongoengine.Document):
    repository = mongoengine.StringField(required=True)
    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle

    number = mongoengine.IntField(required=True)  # The number of this involved issue
    url = mongoengine.StringField()  # url of the issue (actually pull request)
    author = mongoengine.StringField()  # login of the actor who propose the issues
    authorType = mongoengine.StringField()  # type of the actor Who propose the issue
    authorAssociation = mongoengine.StringField()
    """
    Values
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

    inputIssue_label = mongoengine.StringField()  # BugReport, FeatureRequest, Documentation, or Question
    num_comments = mongoengine.IntField()  # Value can be null if it is a PR in prior database but no comments in the focal release cycle

    developers = mongoengine.ListField()  # developers ([user_login or org_login, comments]) commented for it during the focal release cycle
    num_developers = mongoengine.IntField()

    ledToPR = mongoengine.BooleanField()  # Whether the issue leads to at least one pull request; the pr may not be involved in the focal release cycle
    con_prs = mongoengine.ListField()  # Pull Requests ([number)] referred to this issue
    num_conPRs = mongoengine.IntField()

    con_issues = mongoengine.ListField()  # issues ([number]) connected to this focal issue
    num_conIssues = mongoengine.IntField()

    con_commits = mongoengine.ListField()  # commits ([commitOid]) to which this issue referenced in the repository
    num_conCommits = mongoengine.IntField()

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    # ********************************
    # R3: Deeper Inspectation
    # Number of individuals regarding it as primary regarding comments on the issue and its connected PR; 
    #   number of individuals regarding it as secondary
    primary_individual = mongoengine.IntField()
    secondary_individual = mongoengine.IntField()

    # Sentiment in this issue
    comments_issue = mongoengine.ListField()  # object IDs of comments (SupportiveActions) involved in the issue; empty comments ignored!
    comments_pr = mongoengine.ListField()  # object IDs of comments (SupportiveActions) involved in the connected pull request(s); empty ignored!
    num_comments_issue = mongoengine.IntField()  # number of comments involved in the issue; empty comments ignored!
    num_comments_pr = mongoengine.IntField()  # numner of comments involved in the leadTo pr(s); empty comments ignored!
    total_comments = mongoengine.IntField()  # Sum of the numbers of comments involved in the issue and the leadTo pr(s); empty comments ignored!
    
    ave_polarity = mongoengine.FloatField()  # Average the polarity of all involved comments 
        # Polarity: Indicates how positive or negative the text is. 
        # -1 indicates a very negative sentiment.
        # 0 indicates a neutral sentiment.
        # 1 indicates a very positive sentiment.
    ave_subjectivity = mongoengine.FloatField()  # Average the subjectivity of all involved comments
        # Subjectivity: Indicates how subjective or objective the text i
        # 0 indicates that the text is very objective, containing mostly factual information.
        # 1 indicates that the text is very subjective, containing mostly personal opinions, feelings, and beliefs.
    ave_neg = mongoengine.FloatField()  # average the negativity of all involved comments
    ave_neu = mongoengine.FloatField()  # average the neutrality of all involved comments
    ave_pos = mongoengine.FloatField()  # average the positivity of all involved comments
    ave_compound = mongoengine.FloatField() # average the compound scores of comments made by developers in the release cycle
    
    count_toxicComments = mongoengine.IntField()  # The number of possible toxic comments; threshold possibility is 0.6 for any
        # one of the labels: 'Hate', 'Insult', 'Obscene', 'Severe Toxic', 'Threat', 'Toxic'

    # Inspection of speed for processing this issue
    # Stage 1: taking into account the issue only
    createdAt = mongoengine.DateTimeField()  # When this issue is created
    closed = mongoengine.BooleanField()  # whether the issue is closed when we collect the data
    closedAt = mongoengine.DateTimeField()  # when this issue is closed
    spanEntireReleaseCycle = mongoengine.BooleanField()  # True if the issue span the whole release cycle
    time_span = mongoengine.FloatField()  # num of days this issue spans in the focal release cycle
        # Beginning time: (1) when the issue is created or (2) when the release cycle starts, whichever goes later
        # Ending time: (1) when the issue is closed or (2) when the release cycle ends, whichever goes first
    invPRs_ledTo = mongoengine.ListField()  # Information [number, ...] about PRs it led to during the release cycle
    num_prs_ledTo = mongoengine.IntField()  # The number of pull requests this issue leads to in the release cycle
    num_outputs_ledTo = mongoengine.IntField()  # The number of outputs it leads to
    concluded = mongoengine.BooleanField()  # True if the issue is closed or leads to a PR during the release cycle
    # Stage2: taking into account the issues and its leadTo PRs

    # Files involved in each issue that led to at least one pull request during the release cycle
    invFiles = mongoengine.ListField()  # Information [path, ...] about code files that involved in each issue
    num_invFiles = mongoengine.IntField()  # number of file modifications it led to
        
    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0_invIssues',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber', 'number'], 'name': "basic_index2"},
            {'fields': ['repository', 'cycleNumber', 'num_developers'], 'name': "num_dIndex"}
        ]
    }


class ReleaseCycleInvolvedPullRequest(mongoengine.Document):
    repository = mongoengine.StringField(required=True)
    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle
    number = mongoengine.IntField(required=True)  # The number of this involved pull request

    url = mongoengine.StringField()  # url of the issue (actually pull request)
    author = mongoengine.StringField()  # login of the actor who propose the issues
    authorType = mongoengine.StringField()  # type of the actor Who propose the issue

    inputIssue_label = mongoengine.StringField()  # BugReport, FeatureRequest, Documentation, or Question

    # ------------------------------
    # COMMIT-RELATED ATTRIBUTES
    isResolved = mongoengine.BooleanField()  # Whether a valid solution of it is merged within the release cycle
    noChangeInfo_GitHubRestriction = mongoengine.BooleanField()  # Cannot compare with the base commit due to data fetch restriction
    mergedLines = mongoengine.IntField()  # None if not resolved; otherwise, lines changed
    mergedAdditions = mongoengine.IntField()   # None if not resolved; otherwise, lines added
    changedFilesCount = mongoengine.IntField()  # The number of files that are changed after the Merged event
    outputId = mongoengine.ObjectIdField()  # Object ID of its output in the innovation_outputs collection (MongoDB)
    output_type = mongoengine.StringField()  # if "", no related InnovationOutput object; otherwise, BugFixing, NewFeature, or Documentation

    # files and modules involved by commits in this pull request
    linesChanged = mongoengine.IntField()  # Total number of code changes made to this PR in the focal release cycle
    linesAdded = mongoengine.IntField()  # Total additions of code change made to this PR in the focal release cycle

    files = mongoengine.ListField()  # Files ([path, linesChanged]) changed by commits for solving it within the focal cycle
    modules = mongoengine.ListField()  # Modules ([path, linesChanged]) changed by commits for solving it within the focal cycle
    developers_code = mongoengine.ListField()  # developers ([user_login or org_login, linesChanged]) committed for it during the focal cycle
    num_files = mongoengine.IntField()
    num_modules = mongoengine.IntField()
    num_developers_code = mongoengine.IntField()

    # ------------------------------
    # COMMENT-RELATED ATTRIBUTES
    # developers involved by commits and by comments in this pull request
    num_comments = mongoengine.IntField()  # Value can be null if it is a PR in prior database but no comments in the focal release cycle

    developers_comment = mongoengine.ListField()  # developers ([user_login or org_login, comments]) committed for it during the focal cycle
    num_developers_comment = mongoengine.IntField()

    # issues that this pull request has referenced
    connectedToIssue = mongoengine.BooleanField()  # Whether this pull request has referenced to an issue
    con_issues = mongoengine.ListField()  # Issues([number]) connected to the pull request
    num_conIssues = mongoengine.IntField()  # the number of issues connected to this pull request

    con_prs = mongoengine.ListField()  # issues ([number]) connected to this focal PR
    num_conPRs = mongoengine.IntField()

    con_commits = mongoengine.ListField()  # commits ([commitOid]) to which this PR referenced in the repository
    num_conCommits = mongoengine.IntField()

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    # ********************************
    # R3: Deeper Inspectation
    # Number of individuals regarding it as primary regarding comments; number of individuals regarding it as secondary
    notComeFromIssue = mongoengine.BooleanField()  # True if 
    #   (1) the pr does NOT comes from an involved issue of the release cycle, and
    #   (2) the developers made comments for the pr
    primary_individual = mongoengine.IntField()  # !! Only for pull requests that do not come from issues
        # Number of individuals who regard this pull request as primary based on commenting actions
    secondary_individual = mongoengine.IntField()  # !! Only for pull requests that do not come from issues
        # Number of individuals who regard this pull request as secondary based on commenting actions

    # Sentiment analysis
    # !!! Only for notComeFromIssue is True !!!
    comments = mongoengine.ListField()  # object IDs of comments (SupportiveActions) involved in the pr；empty comments ignored!!
    total_comments = mongoengine.IntField()  # the number of involved comments whose text is not empty
    ave_polarity = mongoengine.FloatField()  # Average the polarity of all involved comments 
        # Polarity: Indicates how positive or negative the text is. 
        # -1 indicates a very negative sentiment.
        # 0 indicates a neutral sentiment.
        # 1 indicates a very positive sentiment.
    ave_subjectivity = mongoengine.FloatField()  # Average the subjectivity of all involved comments
        # Subjectivity: Indicates how subjective or objective the text i
        # 0 indicates that the text is very objective, containing mostly factual information.
        # 1 indicates that the text is very subjective, containing mostly personal opinions, feelings, and beliefs.
    ave_neg = mongoengine.FloatField()  # average the negativity of all involved comments
    ave_neu = mongoengine.FloatField()  # average the neutrality of all involved comments
    ave_pos = mongoengine.FloatField()  # average the positivity of all involved comments
    ave_compound = mongoengine.FloatField() # average the compound scores of comments made by developers in the release cycle
    
    count_toxicComments = mongoengine.IntField()  # The number of possible toxic comments; threshold possibility is 0.6 for any
        # one of the labels: 'Hate', 'Insult', 'Obscene', 'Severe Toxic', 'Threat', 'Toxic'

    # Inspection of speed for processing this issue
    createdAt = mongoengine.DateTimeField()  # when the pr is opened
        # isResolved indicates whether a pr is merged during the release cycle
    mergedAt = mongoengine.DateTimeField()  # when the pr is merged
    closed = mongoengine.BooleanField()  # whether the issue is closed when we collect the data
    closedAt = mongoengine.DateTimeField()  # when the pr is closed
    concluded = mongoengine.BooleanField()  # whether the pr is closed or is merged during the release cycle
    
    time_span = mongoengine.FloatField()  # num of days this pr spans in the focal release cycle
        # Beginning time: (1) when the pr is created or (2) when the release cycle starts, whichever goes later
        # Ending time: (1) when the pr is closed, (2) when the pr is closed, or (3) when the release cycle ends, whichever goes first
    spanEntireReleaseCycle = mongoengine.BooleanField()  # True if the pr span the whole release cycle

    # Connection with involved/focal issues within the same release cycle
    invIssues_cameFrom = mongoengine.ListField()  # [number, ...] numbers of involved issues it came from
    num_issues_cameFrom = mongoengine.IntField()

    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0_invPRs',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber', 'number'], 'name': "basic_index2"}
        ]
    }


class ReleaseCycleInvolvedFile(mongoengine.Document):
    repository = mongoengine.StringField(required=True)
    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle

    path = mongoengine.StringField(required=True)
    linesChanged = mongoengine.IntField()  # attempts to make line changes for this file in the release cycle
    linesAdded = mongoengine.IntField()  # attempts to make line additions for this file in the release cycle

    # Pull requests and developers involved in modifying the code of this file
    prs = mongoengine.ListField()  # PullRequests (['number', linesChanged_focalFile]) that had commits for changing this file within the focal cycle
    developers = mongoengine.ListField()  # developers ([user_login or org_login, linesChanged_focalFile]) committed for changing it in the cycle
    num_prs = mongoengine.IntField()
    num_developers = mongoengine.IntField()

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    # ********************************
    # R3: Deeper Inspectation
    # Number of individuals regarding it as primary regarding comments; number of individuals regarding it as secondary
    primary_individual = mongoengine.IntField()
    secondary_individual = mongoengine.IntField()

    # Average time span of each involved pr
    avg_pr_time = mongoengine.FloatField()  # The average time span of involved prs
    time_span = mongoengine.FloatField()  # Number of days a file spans in a release cycle
    # Beginning time: (1) when a involved pr is created or (2) when the release cycle starts, whichever goes later
    # Ending time: (1) when all involved prs are closed, or (2) when the release cycle ends, whichever goes first
    spanEntireReleaseCycle = mongoengine.BooleanField()  # whether the work on this file span the whole release cycle

    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0_invFiles',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber', 'path'], 'name': "basic_index1"}
        ]
    }


class ReleaseCycleInvolvedModule(mongoengine.Document):
    repository = mongoengine.StringField(required=True)
    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle

    path = mongoengine.StringField(required=True)
    linesChanged = mongoengine.IntField()  # attempts to make line changes for this module in the release cycle
    linesAdded = mongoengine.IntField()  # attempts to make line additions for this module in the release cycle

    # Pull requests and developers involved in modifying the code of this module
    prs = mongoengine.ListField()  # PullRequests (['number', linesChanged_focalModule]) that had commits for changing this module within the focal cycle
    developers = mongoengine.ListField()  # developers ([user_login or org_login, linesChanged_focalModule]) committed for changing it in the cycle
    num_prs = mongoengine.IntField()
    num_developers = mongoengine.IntField()

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0_invModules',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic_index"},
            {'fields': ['repository', 'cycleNumber', 'path'], 'name': "basic_index1"}
        ]
    }


class ReleaseCycle(mongoengine.Document):
    """
    The unit of analysis is a release cycle.
    This version considers comments and code changes on all types of issue (bug, feature request, and documentation).
    """
    # ********************************************
    # Part 1 (of 4): properties of a release cycle, i.e., unit of analysis

    # Information about the release cycle
    # The release should not be a draft; it may be a pre-release (not ready for production and may be unstable)
    repository = mongoengine.StringField(required=True)
    isPrerelease = mongoengine.BooleanField(required=True)
    tagName = mongoengine.StringField(required=True)  # e.g., v0.7.7
    name = mongoengine.StringField()  # often same as the tagName
    tagCommitOid = mongoengine.StringField()
    author = mongoengine.StringField()  # who created this release
    description = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)
    updatedAt = mongoengine.DateTimeField()

    cycleNumber = mongoengine.IntField(required=True)  # The 1st, 2nd, 3rd, and so on number of release cycle
    startTime = mongoengine.DateTimeField(required=True)  # The time when last release is published
    endTime = mongoengine.DateTimeField(required=True)  # The time when the focal release is published

    startCommitOid = mongoengine.StringField()  # The most recent defaultBranch commit before startTime; can be None
    endCommitOid = mongoengine.StringField(required=True)  # The most recent defaultBranch commit before endCommitOid

    # Summary of actions occurred in the release cycle

    # -- Commit records a snapshot of the codebase and code changes
    total_commits = mongoengine.IntField()  # The total number of focal innovative actions
    total_additions = mongoengine.IntField()  # Total additions in the commits
    total_deletions = mongoengine.IntField()  # Total deletions in the commits

    # -- Comment refers to 4 types of GitHub activities
    #       IssueComment, CommitComment, PullRequestReview, PullRequestReviewComment
    total_comments = mongoengine.IntField()
    total_comments_dev = mongoengine.IntField()
    total_comments_dev_forIssues = mongoengine.IntField()
    total_comments_user = mongoengine.IntField()
    total_comments_user_forIssues = mongoengine.IntField()  # Comments made by other participants for issues

    # Summary of output-production process
    # -- wiring between issues, pull requests, commits
    proPRs_hasIssueConnect = mongoengine.FloatField()  # The proportion of PRs that have issue connections
    proIssues_hasPRConnect = mongoengine.FloatField()  # The proportion of issues that have pr connections
    proPRs_hasCommitConnect = mongoengine.FloatField()  # The proportion of PRs that have commit connections
    proIssues_hasCommitConnect = mongoengine.FloatField()  # The proportion of issues that have commit connections
    # -- open issues and pull requests
    num_openIssues = mongoengine.IntField()  # Number of issues that have been open during the release cycle
    num_openBugs = mongoengine.IntField()  # Number of issues that have been open and that are bug reports
    num_openFeatures = mongoengine.IntField()  # Number of issues that have been open and that are feature requests
    num_openPRs = mongoengine.IntField()  # Number of prs that have been open during the release cycle
    # -- types of comments
    total_issueComments_dev = mongoengine.IntField()  # Number of issue comments by developers during the release cycle
    total_codeComments_dev = mongoengine.IntField()  # of commitComments, PullRequestReviews, and PullRequestComments by dev
    # -- file work
    num_addedFiles = mongoengine.IntField()  # of new code files that developers added in the release cycle

    # ********************************************
    # Part 2 (of 4): Outcome and collective attention variables
    hasNoChangeInfo = mongoengine.BooleanField()  # True if it has output whose merged and base commits can't be compared
    # variables for innovation productivity
    #   Outputs can be in three categories BugFixing, NewFeature, or Documentation
    num_outputs = mongoengine.IntField()  # Check involved prs to see how many are solved/merged;
    # None if it has outputs whose mergedLine is None due to GitHub restrictions
    speed = mongoengine.FloatField()  # num_outputs / days
    novelty = mongoengine.FloatField()  # The number of outputs that are new features
    quality = mongoengine.FloatField()  # The number of outputs that are bug fixes
    speed_NewFeature = mongoengine.FloatField()  # Number of features created per day
    speed_BugFixing = mongoengine.FloatField()  # Number of bugs fixed per day

    # variables for collective attention
    pdi = mongoengine.FloatField()  # primary division by issues, calculated by comments for issues and connected prs
    pdf = mongoengine.FloatField()  # primary division by files, calculated by code changes
    pdm = mongoengine.FloatField()  # primary division by modules, calculated by code changes

    sii = mongoengine.FloatField()  # secondary integration by issues, calculated by comments for issues and connected prs
    sif = mongoengine.FloatField()  # secondary integration by files, calculated by code changes
    sim = mongoengine.FloatField()  # secondary integration by modules, calculated by code changes

    pai = mongoengine.FloatField()  # code-based primary division by issues
    aui = mongoengine.FloatField()  # code-based secondary integration by issues

    # ********************************************
    # Part 3 (of 4): Information about contingencies, i.e., involved developers, issues, pull requests, files, modules
    # 1. threshold constraint
    #       Note that we may consider only developers who made more than X lines of change
    # 2. feature-only constraint
    #       Note that we may focus on solving feature requests only

    # variables on developer composition
    num_developers = mongoengine.IntField()  # len(involvedDevelopers), people who have coded for the release cycle

    ave_tenure = mongoengine.FloatField()  # average tenure of the involved developers
    sd_tenure = mongoengine.FloatField()  # standard deviation of tenures of the involved developers
    tenure_disparity = mongoengine.FloatField()  # sd_tenure / ave_tenure

    task_interdependence = mongoengine.FloatField()  # network density of pull requests
    # the portion of the potential connections in a pull-request network that are actual connections (has shared file)

    star = mongoengine.FloatField()  # HHI of changed lines over individuals

    # propensity_featureReqeust_code = mongoengine.FloatField()  # Proportion of devs tending to code for feature requests
    # propensity_featureReqeust_comment = mongoengine.FloatField()  # Proportion of devs tending to comment for feature requests

    # scope of work
    num_files = mongoengine.IntField()  # Number of files developers have worked on
    num_modules = mongoengine.IntField()  # Number of modules developers have worked on
    num_prs = mongoengine.IntField()  # Number of pull requests developers have worked on
    num_issues = mongoengine.IntField()  # Number of GitHub issues developers have commented on

    # temporal variable
    project_stage = mongoengine.IntField()  # days elapsed between the startTime of a case and when the repo is created
    days = mongoengine.IntField(required=True)  # How many days are there in the release cycle

    # project ownership
    org = mongoengine.IntField()  # 1 if the owner of the focal repo is an organization; 0 if an user

    # dominance of user voice
    user_commentProp = mongoengine.FloatField()  # (total_comments - total_comments_dev) / total_comments

    # collective code experience
    ave_codeExp = mongoengine.FloatField()  # codeExp of each developer / num_developers

    # orientation to bug fixes or new features
    # orient_features = mongoengine.FloatField()  # Ratio of actions (code or comments) for feature requests
    # orient_bugs = mongoengine.FloatField()  # Ratio of actions (code or comments) for bug reports
    orient_bugs_code = mongoengine.FloatField()  # Orientation: Ratio of code changes allocated to feature requests
    orient_features_code = mongoengine.FloatField()  # Orientation: Ratio of code changes allocated to bug reports
    orient_bugs_comment = mongoengine.FloatField()  # Orientation: Ratio of comments on feature requests of issues
    orient_features_comment = mongoengine.FloatField()  # Orientation: Ratio of comments on bug reports of issues

    # ********************************************
    # Part 4 (of 4): Other important information
    botNum_code = mongoengine.IntField()  # How many bots are involved in the cycle's coding work
    botCommits = mongoengine.IntField()  # How many commits the involved bots have contributed
    botAdditions = mongoengine.IntField()  # How many lines the involved bots have added
    botDeletions = mongoengine.IntField()  # How many lines the involved bots have deleted

    botNum_comment = mongoengine.IntField()  # How many bots have commented in the release cycle
    botComments = mongoengine.IntField()  # Number of comments bots have contributed during the release cycle

    botIntervention_issue = mongoengine.FloatField()  # The proportion of involved issues that have bot intervention
    botIntervention_pr = mongoengine.FloatField()  # The proportion of involved pull requests that have bot intervention
    botIntervention_module = mongoengine.FloatField()  # The proportion of involved modules that have bot intervention
    botIntervention_file = mongoengine.FloatField()  # The proportion of involved files that have bot intervention

    bots_code = mongoengine.DictField()  # Dictionary of bots with login and lines of code change
    bots_prs_code = mongoengine.DictField()  # All pull requests that have bot intervention in coding
    bots_commnet = mongoengine.DictField()  # Dictionary of bots with login and number of comments
    bots_issues_comment = mongoengine.DictField()  # All issues that have bot intervention in commenting
    bots_prs_comment = mongoengine.DictField()  # All pull requests that have bot intervention in commneting

    total_hiddenCommits = mongoengine.IntField()  # The number of hidden commits
    total_hiddenAdditions = mongoengine.IntField()  # Total lines of addition for the hidden commits
    total_hiddenDeletions = mongoengine.IntField()  # Total lines of deletion for the hidden commits

    inSample = mongoengine.IntField()  # 1 if the corresponding release cycle is selected in sample; otherwise, 0

    # Comment sentiment analysis
    ave_polarity = mongoengine.FloatField()  # Average the polarity of comments made by developers in the release cycle
        # Polarity: Indicates how positive or negative the text is. 
        # -1 indicates a very negative sentiment.
        # 0 indicates a neutral sentiment.
        # 1 indicates a very positive sentiment.
    ave_subjectivity = mongoengine.FloatField()  # Average the subjectivity of comments made by developers in the release cycle
        # Subjectivity: Indicates how subjective or objective the text i
        # 0 indicates that the text is very objective, containing mostly factual information.
        # 1 indicates that the text is very subjective, containing mostly personal opinions, feelings, and beliefs.
    ave_neg = mongoengine.FloatField()  # average the negativity of comments made by developers in the release cycle
    ave_neu = mongoengine.FloatField()  # average the neutrality of comments made by developers in the release cycle
    ave_pos = mongoengine.FloatField()  # average the positivity of comments made by developers in the release cycle
    ave_compound = mongoengine.FloatField() # average the compound scores of comments made by developers in the release cycle
    
    count_toxicComments = mongoengine.IntField()  # The number of possible toxic comments; threshold possibility is 0.6 for any
        # one of the labels: 'Hate', 'Insult', 'Obscene', 'Severe Toxic', 'Threat', 'Toxic'
    count_deleted_comments = mongoengine.IntField()  # The number of comments deleted in the focal involved issues or prs

    # ************************************
    # R4: 4th round revision
    # Proportion overlap for primary foci
    # Average proportion of primary foci that overlap with others' primary foci
    num_devWithPrimary_comment = mongoengine.IntField()  # number of developers who have primary foci (epistemic)
    num_devWithPrimary_code = mongoengine.IntField()  # number of developers who have primary foci (technical)
    poi = mongoengine.FloatField()  # primary overlap by issues, calculated by comments for issues and connected prs
    pof = mongoengine.FloatField()  # primary overlap by files, calculated by code changes
    pom = mongoengine.FloatField()  # primary overlap by modules, calculated by code changes
    # Blau's index of developers' secondary foci
    num_devWithSecondary_comment = mongoengine.IntField()  # number of developers who have secondary foci (epistemic)
    num_devWithSecondary_code = mongoengine.IntField()  # number of developers who have secondary foci (technical)
    ssi = mongoengine.FloatField()  # secondary separation by issues, calculated by comments for issues and connected prs
    ssf = mongoengine.FloatField()  # secondary separation by files, calculated by code changes
    ssm = mongoengine.FloatField()  # secondary separation by modules, calculated by code changes
    # Calculate task interdependence based on bipartite network projection
    issue_interdependence_r4 = mongoengine.FloatField()  # Jaccard index for unique pairs, then the sum of pairs/possible pairs
    file_interdependence_r4 = mongoengine.FloatField()  # same as issue interdependence
    task_interdependence_r4 = mongoengine.FloatField()  # 1/2(issue_interdependence_r4 + module_interdependence_r4
    # Calculate the number of epistemic tasks
    num_epistemicTasks = mongoengine.IntField()  # num of involved issues + number of prs that have no connected invoved issues

    meta = {
        'db_alias': 'paper_r2',
        'collection': 'sample0',
        'indexes': [
            {'fields': ['repository', 'cycleNumber'], 'name': "basic1_index"}
        ]
    }
