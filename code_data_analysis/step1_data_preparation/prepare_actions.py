"""
Step 1a. Build the analysis collections from the raw GitHub database (core):
repos_info_2539 (RepoDescription), supportive_actions (SupportiveAction: discursive actions),
and innovative_actions (InnovativeAction: commits).
"""

import datetime
from classes.analysis.innovativeaction import InnovativeAction
from classes.analysis.innovativeaction import PrConnection
from classes.analysis.repoinfo import RepoDescription
from classes.analysis.supportiveactioninfo import SupportiveAction
from classes.github.commit.commit import Commit
from classes.github.event.comment.commitcomment import CommitComment
from classes.github.event.comment.commitcommentthread import CommitCommentThread
from classes.github.event.comment.issuecomment import IssueComment
from classes.github.event.comment.pullrequestreviewcomment import PullRequestReviewComment
from classes.github.event.review.pullrequestreview import PullRequestReview
from classes.github.issuecollection.issue import Issue
from classes.github.issuecollection.pullrequest import PullRequest
from classes.github.repocollection.repo import Repo


def repo_info_db2():
    repos = Repo.objects().only("dataCollectionTime",
                                "id", "nameWithOwner", "owner", "ownerType", "name", "createdAt", "description",
                                "diskUsage", "primaryLanguage", "languageSize",
                                "forkCount", "stargazerCount", "watcherCount",
                                "releaseCount", "topicCount", "languageCount", "license")
    for repo in repos:
        dataCollectionTime = repo["dataCollectionTime"]
        db1Id = repo["id"]
        nameWithOwner = repo["nameWithOwner"]
        owner = repo["owner"]
        ownerType = repo["ownerType"]
        name = repo["name"]
        createdAt = repo["createdAt"]
        description = repo["description"]

        diskUsage = repo["diskUsage"]
        primaryLanguage = repo["primaryLanguage"]
        languageSize = repo["languageSize"]

        forkCount = repo["forkCount"]
        stargazerCount = repo["stargazerCount"]
        watcherCount = repo["watcherCount"]

        releaseCount = repo["releaseCount"]
        topicCount = repo["topicCount"]
        languageCount = repo["languageCount"]
        if not repo["license"]:
            licenseKey = None
            licenseName = None
            licensePseudo = None
        else:
            licenseKey = repo["license"]["key"]
            licenseName = repo["license"]["name"]
            licensePseudo = repo["license"]["pseudoLicense"]

        repoinfo = RepoDescription(dataCollectionTime=dataCollectionTime, db1Id=db1Id, nameWithOwner=nameWithOwner,
                                   owner=owner, ownerType=ownerType, name=name,
                                   createdAt=createdAt, description=description,
                                   diskUsage=diskUsage, primaryLanguage=primaryLanguage, languageSize=languageSize,
                                   forkCount=forkCount, stargazerCount=stargazerCount, watcherCount=watcherCount,
                                   releaseCount=releaseCount, topicCount=topicCount, languageCount=languageCount,
                                   licenseKey=licenseKey, licenseName=licenseName, licensePseudo=licensePseudo)
        repoinfo.save()
    return


def action_info_db2():
    # Discursive actions; commits are saved as innovative actions below
    supportiveActionTypes = [
        "IssueCreated",
        "PullRequestCreated",
        "CommitComment",
        "IssueComment",
        "PullRequestReviewComment",
        "PullRequestReview"
    ]
    for actionType in supportiveActionTypes:
        save_supportive_action_db2(actionType)

    # Save commit information
    startIndex = 0
    delta = 10000
    endIndex = Commit.objects().count()
    while startIndex < endIndex:
        save_innovative_action_db2(startIndex, delta)
        startIndex = startIndex+delta
    return


def save_supportive_action_db2(actionType):
    # Only the six discursive action types used to measure collective attention are kept here.
    # (The original builder also copied 44 other event types, e.g., labeling and assignment events,
    # which do not enter any variable in the paper.)
    if actionType == "IssueCreated":
        actions = Issue.objects().only("id", "author", "authorType", "authorAssociation", "repository", "number",
                                       "createdAt", "publishedAt", "updatedAt")
        for action in actions:
            supportive_action = SupportiveAction(actionId=action["id"], actionType=actionType,
                                                 actorLogin=action["author"], actorType=action["authorType"],
                                                 actorAssociation=action["authorAssociation"],
                                                 repository=action["repository"], subjectType="Issue",
                                                 number=action["number"],
                                                 createdAt=action["createdAt"], publishedAt=action["publishedAt"],
                                                 updatedAt=action["updatedAt"])
            supportive_action.save()

    elif actionType == "PullRequestCreated":
        actions = PullRequest.objects().only("id", "author", "authorType", "authorAssociation",
                                             "repository", "number",
                                             "createdAt", "publishedAt", "updatedAt")
        for action in actions:
            supportive_action = SupportiveAction(actionId=action["id"], actionType=actionType,
                                                 actorLogin=action["author"], actorType=action["authorType"],
                                                 actorAssociation=action["authorAssociation"],
                                                 repository=action["repository"], subjectType="PullRequest",
                                                 number=action["number"],
                                                 createdAt=action["createdAt"], publishedAt=action["publishedAt"],
                                                 updatedAt=action["updatedAt"])
            supportive_action.save()

    elif actionType == "CommitComment":
        threads = CommitCommentThread.objects().only("commitCommentIds", "repository", "subjectType", "number")
        for thread in threads:
            for commitCommentId in thread["commitCommentIds"]:
                action = CommitComment.objects(id=commitCommentId).only("id", "author", "authorType",
                                                                        "authorAssociation", "createdAt",
                                                                        "publishedAt", "updatedAt")
                if len(action) != 1:
                    raise Exception("Debug the actionType == CommitComment part, nor or multiple commitComments")
                supportive_action = SupportiveAction(actionId=action[0]["id"], actionType=actionType,
                                                     actorLogin=action[0]["author"],
                                                     actorType=action[0]["authorType"],
                                                     actorAssociation=action[0]["authorAssociation"],
                                                     repository=thread["repository"],
                                                     subjectType=thread["subjectType"], number=thread["number"],
                                                     createdAt=action[0]["createdAt"],
                                                     publishedAt=action[0]["publishedAt"],
                                                     updatedAt=action[0]["updatedAt"])
                supportive_action.save()

    elif actionType == "IssueComment":
        actions = IssueComment.objects().only("id", "author", "authorType", "authorAssociation",
                                              "repository", "subjectType", "number",
                                              "createdAt", "publishedAt", "updatedAt")
        for action in actions:
            supportive_action = SupportiveAction(actionId=action["id"], actionType=actionType,
                                                 actorLogin=action["author"], actorType=action["authorType"],
                                                 actorAssociation=action["authorAssociation"],
                                                 repository=action["repository"],
                                                 subjectType=action["subjectType"], number=action["number"],
                                                 createdAt=action["createdAt"],
                                                 publishedAt=action["publishedAt"], updatedAt=action["updatedAt"])
            supportive_action.save()

    elif actionType == "PullRequestReviewComment":
        actions = PullRequestReviewComment.objects().only("id", "author", "authorType", "authorAssociation",
                                                          "repository", "subjectType", "number",
                                                          "createdAt", "publishedAt", "updatedAt")
        for action in actions:
            supportive_action = SupportiveAction(actionId=action["id"], actionType=actionType,
                                                 actorLogin=action["author"], actorType=action["authorType"],
                                                 actorAssociation=action["authorAssociation"],
                                                 repository=action["repository"],
                                                 subjectType=action["subjectType"], number=action["number"],
                                                 createdAt=action["createdAt"],
                                                 publishedAt=action["publishedAt"], updatedAt=action["updatedAt"])
            supportive_action.save()

    elif actionType == "PullRequestReview":
        actions = PullRequestReview.objects().only("id", "author", "authorType", "authorAssociation",
                                                   "repository", "subjectType", "number",
                                                   "createdAt", "publishedAt", "updatedAt")
        for action in actions:
            supportive_action = SupportiveAction(actionId=action["id"], actionType=actionType,
                                                 actorLogin=action["author"], actorType=action["authorType"],
                                                 actorAssociation=action["authorAssociation"],
                                                 repository=action["repository"],
                                                 subjectType=action["subjectType"], number=action["number"],
                                                 createdAt=action["createdAt"],
                                                 publishedAt=action["publishedAt"], updatedAt=action["updatedAt"])
            supportive_action.save()

    else:
        raise Exception("Unexpected action type: {}".format(actionType))


def save_innovative_action_db2(startIndex, delta):

    endIndex = startIndex + delta
    actions = Commit.objects[startIndex:endIndex]

    for action in actions:
        committedDate = datetime.datetime.strptime(action["committedDate"], "%Y-%m-%dT%H:%M:%SZ")

        prConnections = []
        if action["associatedPRs"]:
            associatedPRs = action["associatedPRs"]
            for prId in associatedPRs:
                pr = PullRequest.objects(id=prId).only("repository", "number")
                if len(pr) != 1:
                    raise Exception("Debug: the associatedPR id refers to no or multiple pr!")
                prConnection = PrConnection(repository=pr[0]["repository"], number=pr[0]["number"])
                prConnections.append(prConnection)
        else:
            associatedPRs = None

        innovative_action = InnovativeAction(oid=action["oid"], actionId=action["id"], actionType="Commit",
                                             authorLogin=action["author"], authorType=action["authorType"],
                                             committerLogin=action["committer"], committerType=action["committerType"],
                                             authoredByCommitter=action["authoredByCommitter"],
                                             authoredDate=action["authoredDate"], committedDate=committedDate,
                                             commitRepository=action["repository"], prConnections=prConnections,
                                             additions=action["additions"], deletions=action["deletions"],
                                             changedFiles=action["changedFiles"],
                                             changedFilesCount=action["changedFilesCount"],
                                             commitUrl=action["commitUrl"], message=action["message"],
                                             treeOid=action["treeOid"], commentCount=action["commentCount"],
                                             parents=action["parents"], associatedPRs=associatedPRs)
        innovative_action.save()
    return


def update_innovative_action_parentCount():
    begin = 0
    delta = 1000
    end = 2681018
    while begin < end:
        cursor = begin + delta
        if begin + delta > end:
            cursor = end
        inn_actions = InnovativeAction.objects[begin: cursor].only("commitRepository", "oid", "parents")
        for inn_action in inn_actions:
            num_updated = InnovativeAction.objects(
                commitRepository=inn_action["commitRepository"], oid=inn_action["oid"]
            ).update(
                set__parentCount=len(inn_action["parents"])
            )
            if num_updated != 1:
                raise Exception("Debug!")
        begin = begin + delta
    return
