"""
Helper functions for Steps 4-5: distributions of actions over developers/PRs/files/modules,
primary/secondary foci, and Blau's index.
"""

from classes.analysis.innovativeaction import InnovativeAction
from classes.github.issuecollection.issue import Issue
from classes.github.issuecollection.pullrequest import PullRequest
from datetime import datetime
from itertools import groupby
from mongoengine.queryset.visitor import Q


def distribution_of_actions_over_developers(actions):
    user_dict = {}
    org_dict = {}
    for a in actions:
        mongoId = a["id"]
        additions = a["additions"]
        deletions = a["deletions"]
        lines = additions + deletions
        authorType = a["authorType"]
        login = a["authorLogin"]
        if authorType == "User":
            # add the lines to a user's basket
            if login not in user_dict:
                user_dict[login] = lines
            else:
                user_dict[login] = user_dict[login] + lines
        elif authorType == "Organization":
            # add the lines to an organization's basket
            if login not in org_dict:
                org_dict[login] = lines
            else:
                org_dict[login] = org_dict[login] + lines
        else:
            raise Exception("{} is not a valid developer type".format(authorType))

    return user_dict, org_dict


def distribution_of_actions_over_prs(actions, repository, startTime, endTime):
    """
    Distribution of actions over prs that have been open in the focal release cycle
        child function: return_open_prs_of_an_action(action, repository, startTime, endTime)
    :param actions: commits
    :param repository: the focal repository
    :param startTime: the start time of the focal release cycle
    :param endTime: the end time of the focal release cycle
    :return: a dictionary with 'number' as the key and with the lines of code change as the value
    """
    pr_dict = {}  # A dictionary that has pr numbers as keys and lines of changes allocated to the pr as values
    for a in actions:
        lines = a["additions"] + a["deletions"]
        # Collect its connected prs that are in this repository
        conn_prs = return_open_prs_of_an_action(
            action=a, repository=repository, startTime=startTime, endTime=endTime)
        # divide the total lines by the number of involved open prs
        n = len(conn_prs)
        lines_perPR = lines / n
        # add the lines per pull request to the corresponding pull-request record in pr_dict
        for number in conn_prs:
            key = str(number)
            if key not in pr_dict:
                pr_dict[key] = lines_perPR
            else:
                pr_dict[key] = pr_dict[key] + lines_perPR
    return pr_dict


def return_open_prs_of_an_action(action, repository, startTime, endTime):
    """
    Find prs that
    1. are associated with the action and
    2. have been open during the focal release cycle
    :param action: The action of interest
    :param repository: The owner/name of the focal repository
    :param startTime: The start time of the focal release cycle
    :param endTime: The end time of the focal release cycle
    :return: an array of associated open prs' numbers
    """
    open_prs = []
    for p in action['prConnections']:
        # Check whether an associated pr is for the focal repository
        if p["repository"] == repository:
            number = p['number']
            pr = PullRequest.objects(repository=repository, number=number).only(
                'createdAt', 'timeline').first()
            # if the associated pr is created after the release cycle, skip the pr
            if pr['createdAt'] >= endTime:
                continue
            # otherwise,
            # 1) check whether the pr has been open during the release cycle
            isOpen = True  # initiated isOpen as True
            closedTime = pr['createdAt']  # record the latest closed time that is before the startTime of release cycle
            for event in pr['timeline']:
                eventType = event['eventType']
                eventTime = event['createdAt']
                if eventType == 'Merged':
                    # if the pr is merged before the release cycle starts,
                    # refresh the isOpen as False
                    # Note that this should never happen logically on GitHub
                    if eventTime <= startTime:
                        isOpen = False
                        break
                elif eventType == 'ClosedEvent':
                    # if the pr is closed before the release cycle starts,
                    # refresh the closedTime with the event time but continue the timeline check
                    if closedTime <= eventTime <= startTime:
                        closedTime = eventTime
                        isOpen = False
                elif eventType == 'ReopenedEvent':
                    # if the pr is reopened during the release cycle,
                    # refresh the closeTime with the end time of the focal release cycle
                    if startTime <= eventTime < endTime:
                        isOpen = True
                        break
                else:
                    continue
            # 2) if the pr is closed/terminated before the release cycle, skip the pr
            if isOpen:
                open_prs.append(number)

    return open_prs


def distribution_of_actions_over_files(actions):
    file_dict = {}
    for a in actions:
        mongoId = a["id"]
        files = a["changedFiles"]
        for f in files:
            key = f["path"]
            lines = f["additions"] + f["deletions"]
            if key not in file_dict:
                file_dict[key] = lines
            else:
                file_dict[key] = file_dict[key] + lines
    return file_dict


def distribution_of_actions_over_modules(actions):
    module_dict = {}
    for a in actions:
        files = a["changedFiles"]
        for f in files:
            # set key as the path to the file that is changed
            path = f["path"]
            rfind = path.rfind("/")  # return -1 if the substring is not found; otherwise return the last position of /
            if rfind < 0:
                key = path
            else:
                key = path[0:(rfind + 1):]
            lines = f["additions"] + f["deletions"]
            if key not in module_dict:
                module_dict[key] = lines
            else:
                module_dict[key] = module_dict[key] + lines
    return module_dict


def calculate_average(nums):
    if not nums:
        return None
    total = 0
    for num in nums:
        total = total + num
    ave = total / len(nums)
    return ave


def calculate_blau_index(d):
    if not d:
        return None
    blau_index = 0
    total = 0
    for key in d:
        total = total + d[key]
    for key in d:
        blau_index = blau_index + (d[key] / total) * (d[key] / total)
    blau_index = 1 - blau_index
    return blau_index


def return_firstCommitTime(login, actorType, repository):
    action = InnovativeAction.objects(
        (Q(prConnections__repository=repository) | Q(commitRepository=repository)) &
        Q(authorLogin=login) & Q(authorType=actorType)
    ).only("committedDate").order_by("+committedDate").first()
    if not action:
        raise Exception("!!Debug!!")
    firstCommitTime = action["committedDate"]
    return firstCommitTime


def check_issue_or_pr_openness(issueType, number, repository, startTime, endTime):
    """
    Check whether an issue is open
    :return: isOpen, True if the issue or pull request has been open during the release cycle
    """
    isOpen = False
    # Get the timeline information of the issue or pull request
    if issueType == "Issue":
        item = Issue.objects(repository=repository, number=number).only(
            'createdAt', 'closed', 'closedAt').first()
    elif issueType == "PullRequest":
        item = PullRequest.objects(repository=repository, number=number).only(
            'createdAt', 'closed', 'closedAt', 'merged', 'mergedAt').first()
    else:
        raise Exception("{} is unexpected issue type".format(issueType))

    if item is None:
        raise Exception("{} #{} in repo: {} cannot be found".format(issueType, str(number), repository))

    # Situations in which the item is open in the release cycle
    # For an issue
    #   the item is created before the endTime, and the item is not closed or closed after the startTime
    # For a pull request
    #   the item is not merged and not closed
    #   the item is not merged, but closed after the startTime
    #   the item is merged, but merged after the startTime
    if item['createdAt'] < endTime:
        closed = item['closed']
        closedAt = item['closedAt']
        if issueType == 'Issue':
            # Not closed or closed after the release cycle starts
            if closed is False:
                isOpen = True
            if closed is True and (closedAt is not None and closedAt > startTime):
                isOpen = True
        elif issueType == "PullRequest":
            # see merged situation and closed situation
            merged = item['merged']
            mergedAt_string = item['mergedAt']
            if merged is True:  # Merged
                # Convert mergedAt to DateTime type
                mergedAt = datetime.fromisoformat(mergedAt_string.rstrip('Z'))
                if mergedAt > startTime:  # merged after the release cycle starts
                    isOpen = True
            else:
                if closed is False:  # not merged, and not closed
                    isOpen = True
                if closed is True and closedAt > startTime:  # not merged, but closed, however closed after startTime
                    isOpen = True
        else:
            raise Exception("{} is unexpected issueType in check_issue_or_pr_openness".format(issueType))

    return isOpen


def distribution_of_comments_overDevelopers(comments):
    """
    Return a list recording the distribution of comments over developers (user_ or org_login)
    :param comments: supportiveActions in IssueComment, PullRequestReview, PullRequestReviewComment, or CommitComment
    :return: developers, a list of [user_ or org_login, number of comments]
    """
    sorted_comments = sorted(comments, key=lambda x: (x.actorType, x.actorLogin))
    grouped_comments = [list(group) for _, group in groupby(
        sorted_comments, key=lambda x: (x.actorType, x.actorLogin))]
    developers = []
    for dev_comments in grouped_comments:
        count = len(dev_comments)
        actorType = dev_comments[0]['actorType']
        login = dev_comments[0]['actorLogin']
        if actorType == 'User':
            actorType_login = 'user_' + login
        elif actorType == 'Organization':
            actorType_login = 'org_' + login
        else:
            raise Exception("{} is unexpected type of user".format(actorType))
        developers.append([actorType_login, count])

    return developers


def get_primary_secondary_items_highest(focal_dict):
    primaryItems = []
    secondaryItems = []
    maxValue = max(focal_dict.values())
    primary = 0
    contribution = 0
    for key in focal_dict:
        value = focal_dict[key]
        contribution += value
        if value == maxValue:
            primaryItems.append([key, value])
            primary = primary + value
        else:
            secondaryItems.append([key, value])
    primaryRate = primary / contribution

    return primaryItems, secondaryItems, primaryRate
