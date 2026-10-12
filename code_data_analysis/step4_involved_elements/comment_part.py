"""
Step 4b. Discursive work: scope comments (incl. IssueCreated and PullRequestCreated) by the cycle's
developers, create involved issues/PRs, and each developer's primary/secondary issues.
"""

from classes.analysis.inputissue import InputIssue
from classes.analysis.supportiveactioninfo import SupportiveAction
from classes.github.event.connection.connected import ConnectedEvent
from classes.github.event.connection.crossreferenced import CrossReferencedEvent
from classes.github.event.connection.referenced import ReferencedEvent
from classes.github.issuecollection.issue import Issue
from classes.github.issuecollection.pullrequest import PullRequest
from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedIssue
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest
from itertools import groupby
from mongoengine.queryset.visitor import Q
from step4_involved_elements.basics import check_issue_or_pr_openness
from step4_involved_elements.basics import distribution_of_comments_overDevelopers
from step4_involved_elements.basics import get_primary_secondary_items_highest


# -----------------------------------------------
# Part 1 (of 2): Update the COMMENT PART of involved Issues, PRs, and developers
def scope_focal_comments_r4(repository, cycleNumber, startTime, endTime):
    """
    :return: focal comments (comments made by focal developers),
        MongoDB: update comment summary for the focal release cycle
    """
    # 1. Get all comments made during the release cycle
    #   * associated with the focal repository's pull requests or issues
    #   * made within the focal release cycle --> Use created time of the comment event
    #   * conducted by GitHub users (i.e., not bots or aliens)
    #   * actionType are IssueComment, CommitComment, PullRequestReview, PullRequestReviewComment,
    #   IssueCreated, PullRequestCreated
    comments_user0 = SupportiveAction.objects().filter(
        (Q(repository=repository)) &  # for the focal repository
        (Q(createdAt__gte=startTime) & Q(createdAt__lt=endTime)) &  # made within the release cycle
        (Q(actorType="User")) &  # made by GitHub human participants
        (
            Q(actionType="IssueComment") | Q(actionType="CommitComment")
            | Q(actionType="PullRequestReview") | Q(actionType="PullRequestReviewComment")
            # !!!!!!!!!!!!!!!!!!!!!!! IssueCreated and PullRequestCreated should also be epistemic work
            | Q(actionType="IssueCreated") | Q(actionType="PullRequestCreated")
        )  # are comments
    )
    comments_org0 = SupportiveAction.objects().filter(
        (Q(repository=repository)) &  # for the focal repository
        (Q(createdAt__gte=startTime) & Q(createdAt__lt=endTime)) &  # made within the release cycle
        (Q(actorType="Organization")) &  # made by GitHub human participants
        (
            Q(actionType="IssueComment") | Q(actionType="CommitComment")
            | Q(actionType="PullRequestReview") | Q(actionType="PullRequestReviewComment")
            # !!!!!!!!!!!!!!!!!!!!!!! IssueCreated and PullRequestCreated should also be epistemic work
            | Q(actionType="IssueCreated") | Q(actionType="PullRequestCreated")
        )  # are comments
    )
    # 2. Exclude comments that are made for issues or pull requests that have not been open in the focal release cycle
    comments_user = []
    for comment in comments_user0:
        issueType = comment['subjectType']
        number = comment['number']
        isOpen = check_issue_or_pr_openness(
            issueType=issueType, number=number, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen:
            comments_user.append(comment)
    comments_org = []
    for comment in comments_org0:
        issueType = comment['subjectType']
        number = comment['number']
        isOpen = check_issue_or_pr_openness(
            issueType=issueType, number=number, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen:
            comments_org.append(comment)

    total_comments = len(comments_user) + len(comments_org)

    # 3. Differentiate comments made by developers (people who made lines of change) and comments made by others
    # get a list of focal developers in User account
    user_devs = []
    cases = ReleaseCycleInvolvedDeveloper.objects(
        repository=repository, cycleNumber=cycleNumber, actorType='User').only('login')
    for dev in cases:
        login = dev['login']
        user_devs.append(login)
    # get a list of focal developers in Organization account
    org_devs = []
    cases = ReleaseCycleInvolvedDeveloper.objects(
        repository=repository, cycleNumber=cycleNumber, actorType='Organization').only('login')
    for dev in cases:
        login = dev['login']
        org_devs.append(login)
    # check whether the comment is made by focal developers
    focal_comments = []  # Store comments made by (focal) developers
    other_comments = []  # Store comments made by other people (user or organization account)
    for comment in comments_user:
        login = comment['actorLogin']
        if login in user_devs:
            focal_comments.append(comment)
        else:
            other_comments.append(comment)
    for comment in comments_org:
        login = comment['actorLogin']
        if login in org_devs:
            focal_comments.append(comment)
        else:
            other_comments.append(comment)
    total_comments_dev = len(focal_comments)

    # 3.1 Calculate issue-related comments made by focal developers
    focal_comments_issue = []  # Comments made by (focal) developers for issues
    focal_comments_pr = []  # Comments made by (focal) developers for pull requests
    if len(focal_comments) > 0:
        sorted_comments = sorted(focal_comments, key=lambda x: x.subjectType)
        grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.subjectType)]
        count = len(grouped_comments)
        if count == 2:
            issueType0 = grouped_comments[0][0]['subjectType']
            issueType1 = grouped_comments[1][0]['subjectType']
            if issueType0 == 'Issue' and issueType1 == 'PullRequest':
                focal_comments_issue.extend(grouped_comments[0])
                focal_comments_pr.extend(grouped_comments[1])
            else:
                raise Exception('Debug: 3.1 Calculate issue-related comments made by focal developers')
        elif count == 1:
            issueType = grouped_comments[0][0]['subjectType']
            if issueType == 'Issue':
                focal_comments_issue.extend(grouped_comments[0])
            elif issueType == 'PullRequest':
                focal_comments_pr.extend(grouped_comments[0])
            else:
                raise Exception("{} is an unexpected issueType".format(issueType))
        else:
            raise Exception("The length of grouped_comments is {}".format(str(count)))

    total_comments_dev_forIssues = len(focal_comments_issue)

    # 3.2 Calculate issue-related comments made by others, i.e., users
    total_comments_user = len(other_comments)
    total_comments_user_forIssues = 0
    # calculate focal comments made by users for issues
    sorted_comments = sorted(other_comments, key=lambda x: x.subjectType)
    grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.subjectType)]
    for comments in grouped_comments:
        issueType = comments[0]['subjectType']
        if issueType == 'Issue':
            total_comments_user_forIssues = len(comments)
            break
    # 4. update release cycle summary information
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        total_comments=total_comments, total_comments_dev=total_comments_dev,
        total_comments_dev_forIssues=total_comments_dev_forIssues,
        total_comments_user=total_comments_user, total_comments_user_forIssues=total_comments_user_forIssues
    )
    if num_updated != 1:
        raise Exception("The number of case repo: {}, cycle {} is incorrect!".format(repository, str(cycleNumber)))

    return focal_comments, focal_comments_issue, focal_comments_pr


def create_invIssues_invPRsComment_r4(focal_comments_issue, focal_comments_pr,
                                      repository, cycleNumber):
    # 1. Create involved issues based on focal_comments_issue
    sorted_comments = sorted(focal_comments_issue, key=lambda x: x.number)
    grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.number)]
    for comments in grouped_comments:
        number = comments[0]['number']
        count = ReleaseCycleInvolvedIssue.objects(repository=repository, cycleNumber=cycleNumber, number=number).count()
        if count == 0:
            invIssue = ReleaseCycleInvolvedIssue(repository=repository, cycleNumber=cycleNumber, number=number)
            invIssue.save()
    # 2. Create involved prs which has comments but not commits based on focal_comments_pr
    sorted_comments = sorted(focal_comments_pr, key=lambda x: x.number)
    grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.number)]
    for comments in grouped_comments:
        number = comments[0]['number']
        count = ReleaseCycleInvolvedPullRequest.objects(
            repository=repository, cycleNumber=cycleNumber, number=number).count()
        if count == 0:
            pull = PullRequest.objects(repository=repository, number=number).only('url', 'author', 'authorType').first()
            if pull is not None:
                url = pull['url']
                author = pull['author']
                authorType = pull['authorType']
            else:
                raise Exception("PR #{} in {} does not exist in PullRequest objects.".format(str(number), repository))
            # Get corresponding inputIssue_label
            inputIssue = InputIssue.objects(repository=repository, number=number).only('label').first()
            if inputIssue is not None:
                inputIssue_label = inputIssue['label']
            else:
                raise Exception("PR #{} in {} does not exist in InputIssue objects.".format(str(number), repository))
            invPR = ReleaseCycleInvolvedPullRequest(
                repository=repository, cycleNumber=cycleNumber, number=number,
                url=url, author=author, authorType=authorType, inputIssue_label=inputIssue_label
            )
            invPR.save()
        elif count == 1:
            continue
        else:
            raise Exception("There are {} prs whose repo is {}, cycleNumber is {}, and number is #{}".format(
                str(count), repository, str(cycleNumber), str(number)
            ))

    return


def update_focal_issues_r4(focal_comments_issue, repository, cycleNumber, startTime, endTime):
    if not focal_comments_issue:
        return
    if focal_comments_issue[0]["subjectType"] != 'Issue':
        raise Exception("Comments are not for issues in update_focal_issues")
    # 1. Group the comments by issue number
    sorted_comments = sorted(focal_comments_issue, key=lambda x: x.number)
    grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.number)]
    for comments in grouped_comments:
        number = comments[0]['number']
        # 2. Get url, author, authorType information
        issue = Issue.objects(repository=repository, number=number).only(
            'url', 'author', 'authorType', 'authorAssociation').first()
        if issue is not None:
            url = issue['url']
            author = issue['author']
            authorType = issue['authorType']
            authorAssociation = issue['authorAssociation']
        else:
            raise Exception("Issue #{} in {} does not exist in Issue objects.".format(str(number), repository))
        # 3. Get inputIssue_label information
        inputIssue = InputIssue.objects(repository=repository, number=number).only('label').first()
        if inputIssue is not None:
            inputIssue_label = inputIssue['label']
        else:
            raise Exception("Issue #{} in {} does not exist in InputIssue objects.".format(str(number), repository))
        # 4. Get num_comments information
        num_comments = len(comments)
        # 5. Group the comments for each issue by developer
        developers = distribution_of_comments_overDevelopers(comments)
        num_developers = len(developers)
        # 6. Get its connection to pull requests, other issues, and commits
        con_prs, con_issues, con_commits = get_connections(
            itemType='Issue', repository=repository, number=number, startTime=startTime, endTime=endTime)
        num_conPRs = len(con_prs)
        num_conIssues = len(con_issues)
        num_conCommits = len(con_commits)
        if num_conPRs > 0:
            ledToPR = True
        else:
            ledToPR = False
        # 7. Save this involved issue
        num_updated = ReleaseCycleInvolvedIssue.objects(
            repository=repository, cycleNumber=cycleNumber, number=number
        ).update(
            url=url, author=author, authorType=authorType, authorAssociation=authorAssociation,
            inputIssue_label=inputIssue_label,
            num_comments=num_comments, developers=developers, num_developers=num_developers,
            ledToPR=ledToPR, con_prs=con_prs, num_conPRs=num_conPRs, con_issues=con_issues, num_conIssues=num_conIssues,
            con_commits=con_commits, num_conCommits=num_conCommits
        )
        if num_updated != 1:
            raise Exception("There are {} issues whose repo is {}, cycleNumber is {}, and number is #{}".format(
                str(num_updated), repository, str(cycleNumber), str(number)
            ))

    return


def update_focal_prs_commentPart_r4(focal_comments_pr, repository, cycleNumber, startTime, endTime):
    if not focal_comments_pr:
        return
    if focal_comments_pr[0]["subjectType"] != 'PullRequest':
        raise Exception("Comments are not for pull requests in update_focal_prs_commentPart")
    # 1. Group the comments by PR number
    sorted_comments = sorted(focal_comments_pr, key=lambda x: x.number)
    grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.number)]
    for comments in grouped_comments:
        number = comments[0]['number']
        # 2. Get num_comments information
        num_comments = len(comments)
        # 3. Group the comments for each issue by developer
        developers_comment = distribution_of_comments_overDevelopers(comments)
        num_developers_comment = len(developers_comment)
        # 4. Get its connection to issues, other pull requests, and commits
        con_prs, con_issues, con_commits = get_connections(
            itemType='PullRequest', repository=repository, number=number, startTime=startTime, endTime=endTime)
        num_conPRs = len(con_prs)
        num_conIssues = len(con_issues)
        num_conCommits = len(con_commits)
        if num_conIssues > 0:
            connectedToIssue = True
        else:
            connectedToIssue = False
        # 5. Save the information
        num_updated = ReleaseCycleInvolvedPullRequest.objects(
            repository=repository, cycleNumber=cycleNumber, number=number
        ).update(
            num_comments=num_comments, developers_comment=developers_comment,
            num_developers_comment=num_developers_comment, connectedToIssue=connectedToIssue,
            con_issues=con_issues, num_conIssues=num_conIssues, con_prs=con_prs, num_conPRs=num_conPRs,
            con_commits=con_commits, num_conCommits=num_conCommits
        )
        if num_updated != 1:
            raise Exception("More than one case with repo: {}, cycleNumber: {}, pullRequest Number: {} UPDATED".format(
                repository, str(cycleNumber), str(number)
            ))

    return


def update_focal_developers_comments_r4(focal_comments, repository, cycleNumber):
    sorted_comments = sorted(focal_comments, key=lambda x: (x.actorType, x.actorLogin))
    groupedComments_byDev = [
        list(group) for _, group in groupby(sorted_comments, key=lambda x: (x.actorType, x.actorLogin))
    ]
    # Go for each developer
    for comments in groupedComments_byDev:
        # Identifier of the developer
        actorType = comments[0]['actorType']
        login = comments[0]['actorLogin']
        # 1. Differentiate comments for issues and for pull requests
        sorted_comments = sorted(comments, key=lambda x: x.subjectType)
        grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.subjectType)]
        comments_forPRs = []
        comments_forIssues = []
        if grouped_comments[0][0]['subjectType'] == 'Issue':
            comments_forIssues.extend(grouped_comments[0])
            if len(grouped_comments) == 2:
                comments_forPRs.extend(grouped_comments[1])
        elif grouped_comments[0][0]['subjectType'] == 'PullRequest':
            comments_forPRs.extend(grouped_comments[0])
            if len(grouped_comments) == 2:
                comments_forIssues.extend(grouped_comments[1])
        else:
            raise Exception("{} is unexpected subject type".format(grouped_comments[0][0]['subjectType']))
        # 2. Calculate contribution_comment, contribution_comment_issues, contribution_IssueComment
        contribution_comment = len(comments)
        contribution_comment_issues = len(comments_forIssues)
        contribution_IssueComment = 0
        sorted_comments = sorted(comments, key=lambda x: x.actionType)
        grouped_comments = [list(group) for _, group in groupby(sorted_comments, key=lambda x: x.actionType)]
        for type_comments in grouped_comments:
            actionType = type_comments[0]['actionType']
            if actionType == 'IssueComment':
                contribution_IssueComment = len(type_comments)
        # 3. Get attention distribution over issues (with connected prs) and PRs and get primary/secondary issues
        # if login == 'jon-morra-zefr' and repository == "VowpalWabbit/vowpal_wabbit" and cycleNumber == 7:
        #     print("got it!")
        issue_dict_unsorted = distribution_of_commentsBy_aFocalDeveloper_overIssuePRs_r4(
            comments=comments, repository=repository, cycleNumber=cycleNumber)
        issue_dict = dict(sorted(issue_dict_unsorted.items(), reverse=False))  # sorted by key instead of value
        num_issues = len(issue_dict)
        primaryIssues, secondaryIssues, primaryRate_issue = get_primary_secondary_items_highest(
            focal_dict=issue_dict
        )
        num_primaryIssues = len(primaryIssues)
        num_secondaryIssues = len(secondaryIssues)

        # 4. Calculate orientation regarding comments
        num_comments_bug = 0
        num_comments_feature = 0
        for key in issue_dict:
            splitted_list = key.split('_')
            issueType = splitted_list[0]
            number_string = splitted_list[1]
            number = int(number_string)
            count = issue_dict[key]
            if issueType == 'issue':
                invItem = ReleaseCycleInvolvedIssue.objects(
                    repository=repository, cycleNumber=cycleNumber, number=number
                ).only('inputIssue_label').first()
            elif issueType == 'pr':
                invItem = ReleaseCycleInvolvedPullRequest.objects(
                    repository=repository, cycleNumber=cycleNumber, number=number
                ).only('inputIssue_label').first()
            else:
                raise Exception("{} #{} does not exist in repo:{}, cycleNumber: {}".format(
                    issueType, str(number), repository, str(cycleNumber)
                ))
            inputIssue_label = invItem['inputIssue_label']
            if inputIssue_label == 'BugReport':
                num_comments_bug += count
            elif inputIssue_label == 'FeatureRequest':
                num_comments_feature += count
            elif inputIssue_label == 'Documentation' or inputIssue_label == 'Question':
                continue
            else:
                raise Exception('{} is an unexpected InputIssue label'.format(inputIssue_label))

        orient_bugs_comment = num_comments_bug / contribution_comment
        orient_features_comment = num_comments_feature / contribution_comment

        # 5. Update the information
        num_updated = ReleaseCycleInvolvedDeveloper.objects(
            repository=repository, cycleNumber=cycleNumber, actorType=actorType, login=login
        ).update(
            contribution_comment=contribution_comment, contribution_comment_issues=contribution_comment_issues,
            contribution_IssueComment=contribution_IssueComment,
            num_issues=num_issues,
            primaryIssues=primaryIssues, num_primaryIssues=num_primaryIssues, secondaryIssues=secondaryIssues,
            num_secondaryIssues=num_secondaryIssues, primaryRate_issue=primaryRate_issue,
            orient_bugs_comment=orient_bugs_comment, orient_features_comment=orient_features_comment
        )
        if num_updated != 1:
            raise Exception("{} involved developers in repo: {}, cycle: {}, actorType: {}, login: {}".format(
                str(num_updated), repository, str(cycleNumber), actorType, login
            ))

    return


def distribution_of_commentsBy_aFocalDeveloper_overIssuePRs_r4(comments, repository, cycleNumber):
    """
    Get a dictionary of issues and prs, with values of comments connected to them
    :param comments:
    :param repository:
    :param cycleNumber:
    :return: focal_dict {issue_ or pr_number: the number of comments}
    """
    # 1. Create an issue dict and a pr dict with {'number': Number of Comments}
    dict_issue = {}
    dict_pr = {}
    for c in comments:
        issueType = c['subjectType']
        key = str(c['number'])
        if issueType == 'Issue':
            if key not in dict_issue:
                dict_issue[key] = 1
            else:
                dict_issue[key] += 1
        elif issueType == 'PullRequest':
            if key not in dict_pr:
                dict_pr[key] = 1
            else:
                dict_pr[key] += 1
        else:
            raise Exception("{} is unexpected type".format(issueType))
    # 2. Add the connected PRs' comments to the corresponding issues and remove the PRs included in issues to
    # get updated 'dict_issue' with connected PRs' comments added and 'dict_pr' with connected to issues removed
    prKeys_shouldRemove = []  # A list of prNumbers (String type) that should be removed
    original_totalComments = sum(dict_issue.values()) + sum(dict_pr.values())
    # 2.1 Update the issues
    for key in dict_issue:
        number = int(key)
        # Get the issue's connected PRs,
        #     add the connected PRs' comments to this issue,
        #     if the connected PR links to two focal issues, add 1/count total comments of this PR to the issue, and
        invIssue = ReleaseCycleInvolvedIssue.objects(
            repository=repository, cycleNumber=cycleNumber, number=number
        ).only('con_prs', 'number').first()
        if invIssue is not None:
            con_prs = invIssue['con_prs']
            for pr in con_prs:
                prKey = str(pr)
                if prKey in dict_pr:
                    # Mark that this pr should be removed
                    if prKey not in prKeys_shouldRemove:
                        prKeys_shouldRemove.append(prKey)
                    # Count the number of focal issues that connect to this PR
                    invPR = ReleaseCycleInvolvedPullRequest.objects(
                        repository=repository, cycleNumber=cycleNumber, number=pr
                    ).only('con_issues').first()
                    pr_issuesConnected = invPR['con_issues']
                    if pr_issuesConnected is None:
                        raise Exception("repo: {}, cycleNumber: {}, pr: {} cannot be found".format(
                            repository, str(cycleNumber), prKey))
                    count = 0
                    for issueConnected in pr_issuesConnected:
                        issueKey = str(issueConnected)
                        if issueKey in dict_issue:
                            count += 1
                    if count == 0:
                        raise Exception("Debug")
                    elif count > 1:
                        print("carefully double check!")
                    # Add a portion (1/count) of the PR's comment to the issue
                    dict_issue[key] += dict_pr[prKey] / count
                else:
                    continue
        else:
            raise Exception("Issue #{} does not exist in repo:{}, cycleNumber: {}".format(
                str(number), repository, str(cycleNumber)
            ))
    # 2.2 Remove the prs that are counted in the updated issues
    for prKey in prKeys_shouldRemove:
        del dict_pr[prKey]
    # 2.3 Double-check the number of total comments made by the developer
    final_totalComments = sum(dict_issue.values()) + sum(dict_pr.values())
    if abs(final_totalComments - original_totalComments) > 0.5:
        raise Exception("The number of comments are changed!")

    # 3. Convert the issue_dict and pr_dict to a list of Issues (['issue_number or pr_number', numComments])
    focal_dict = {}
    for key in dict_issue:
        keyElement = 'issue_' + key
        valueElement = dict_issue[key]
        focal_dict[keyElement] = valueElement
    for key in dict_pr:
        keyElement = 'pr_' + key
        valueElement = dict_pr[key]
        focal_dict[keyElement] = valueElement

    return focal_dict


# ----------------------------------
def get_connections(itemType, repository, number, startTime, endTime):
    """
    Get connection information of the given item (i.e., an issue or a pull request) based on three events:
    -- ConnectedEvent: connections between issues and pull requests
    -- CrossReferencedEvent: connections between issues and pull requests, issues and issues, PRs and PRs
    -- ReferencedEvent: connections between commit and issue or pull request
    :param startTime: Start time of the focal release cycle
    :param endTime: End time of the focal release cycle
    :param itemType: "Issue" or "PullRequest"
    :param repository: owner/repoName
    :param number: number of the issue or PR
    :return:
        con_prs: a list of pr numbers,
        con_issues: a list of issue numbers,
        con_commits: a list of commitOid
    """
    con_prs = []
    con_issues = []
    con_commits = []
    #   check connect event where the focal issue is a source
    connects = ConnectedEvent.objects(sourceType=itemType, sourceRepository=repository, sourceNumber=number)
    for con in connects:
        subjectType = con['subjectType']
        subjectRepository = con['subjectRepository']
        subjectNumber = con['subjectNumber']
        eventTime = con['createdAt']
        # Include if the item
        # a. is for the focal repository
        if subjectRepository != repository or eventTime > endTime:
            continue
        # b. has been open in the focal release cycle
        isOpen = check_issue_or_pr_openness(
            issueType=subjectType, number=subjectNumber, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen is False:
            continue
        # c. has not been included in the con_issues or con_prs list
        if subjectRepository == repository:
            if subjectType == 'Issue':
                if subjectNumber not in con_issues:
                    con_issues.append(subjectNumber)
            elif subjectType == 'PullRequest':
                if subjectNumber not in con_prs:
                    con_prs.append(subjectNumber)
            else:
                raise Exception("{} is unexpected subjectType in ConnectedEvent".format(subjectType))
    #   check connect event where the focal issue is a subjecte
    connects = ConnectedEvent.objects(subjectType=itemType, subjectRepository=repository, subjectNumber=number)
    for con in connects:
        sourceType = con['sourceType']
        sourceRepository = con['sourceRepository']
        sourceNumber = con['sourceNumber']
        eventTime = con['createdAt']
        # Include if the item
        # a. is for the focal repository
        if sourceRepository != repository or eventTime > endTime:
            continue
        # b. has been open in the focal release cycle
        isOpen = check_issue_or_pr_openness(
            issueType=sourceType, number=sourceNumber, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen is False:
            continue
        # c. has not been included in the con_issues or con_prs list
        if sourceRepository == repository:
            if sourceType == 'Issue':
                if sourceNumber not in con_issues:
                    con_issues.append(sourceNumber)
            elif sourceType == 'PullRequest':
                if sourceNumber not in con_prs:
                    con_prs.append(sourceNumber)
            else:
                raise Exception("{} is unexpected sourceType in ConnectedEvent".format(sourceType))
    #   check crossReferenced event where the focal issue is a source
    connects = CrossReferencedEvent.objects(sourceType=itemType, sourceRepository=repository, sourceNumber=number)
    for con in connects:
        targetType = con['targetType']
        targetRepository = con['targetRepository']
        targetNumber = con['targetNumber']
        eventTime = con['createdAt']
        # Include if the item
        # a. is for the focal repository or the connection happen after the release cycle
        if targetRepository != repository or eventTime > endTime:
            continue
        # b. has been open in the focal release cycle
        isOpen = check_issue_or_pr_openness(
            issueType=targetType, number=targetNumber, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen is False:
            continue
        # b. has not been included in the con_issues or con_prs list
        if targetRepository == repository:
            if targetType == 'Issue':
                if targetNumber not in con_issues:
                    con_issues.append(targetNumber)
            elif targetType == 'PullRequest':
                if targetNumber not in con_prs:
                    con_prs.append(targetNumber)
            else:
                raise Exception("{} is unexpected targetType in CrossReferencedEvent".format(targetType))
    #   check crossReferenced event where the focal issue is a target
    connects = CrossReferencedEvent.objects(targetType=itemType, targetRepository=repository, targetNumber=number)
    for con in connects:
        sourceType = con['sourceType']
        sourceRepository = con['sourceRepository']
        sourceNumber = con['sourceNumber']
        eventTime = con['createdAt']
        # Include if the item
        # a. is for the focal repository
        if sourceRepository != repository or eventTime > endTime:
            continue
        # b. has been open in the focal release cycle
        isOpen = check_issue_or_pr_openness(
            issueType=sourceType, number=sourceNumber, repository=repository, startTime=startTime, endTime=endTime)
        if isOpen is False:
            continue
        # c. has not been included in the con_issues or con_prs list
        if sourceRepository == repository:
            if sourceType == 'Issue':
                if sourceNumber not in con_issues:
                    con_issues.append(sourceNumber)
            elif sourceType == 'PullRequest':
                if sourceNumber not in con_prs:
                    con_prs.append(sourceNumber)
            else:
                raise Exception("{} is unexpected sourceType in CrossReferencedEvent".format(sourceType))
    #   check referenced event where the focal issue refers to a commit
    #   in the focal repository
    connects = ReferencedEvent.objects(
        subjectType=itemType, repository=repository, number=number, isCrossRepository=False)
    for con in connects:
        commitOid = con['commitOid']
        # b. is not None and has not been included in the list
        if commitOid is not None and commitOid not in con_commits:
            con_commits.append(commitOid)

    return con_prs, con_issues, con_commits
