"""
Helper for Step 1b: fetch a commit that is missing from innovative_actions via the GitHub REST API v3.
"""

import datetime
import os
import requests
import time
from classes.analysis.innovativeaction import InnovativeAction
from classes.github.commit.parent import Parent
from classes.github.issuecollection.changedfile import ChangedFile
from setup.restv3 import get_remaining_rest_RESTV3


headers = {
    "Authorization": "token " + os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN"),
    "User-Agent": "research-data-collection",
    "Accept": "application/vnd.github.v3+json"
}


sleep_more = 1200


# Get full information of a commit and save it in MongoDB
def fetch_repo_commit(repository, commitOid):
    """
    Get the full information of a specific commit and save the information in MongoDB
    1. Set the url of fetching a commit by repo --> commits --> commitOid
        see documentation of "Get a commit": https://developer.github.com/v3/repos/commits/#get-a-commit
    2. Call information of the commit by GitHub REST API v3
    3. Collect the commit information and save full information (basicInfo, additions, deletions, and
        changedFiles) of the commit in MongoDB

    :param repository: The owner/name of the repository that owns this commit
    :param commitOid: GitObject ID of the commit
    :return: Return the message of this commit
    """
    print("Working on commit {} in repo {}".format(commitOid, repository))

    # 1. Set the url of fetching a commit by repo --> commits --> commitOid
    url = "https://api.github.com/repos/" + repository + "/commits/" + commitOid

    # 2. Call information of the commit by GitHub REST API v3
    remaining, reset = get_remaining_rest_RESTV3(headers=headers)
    if remaining < 2:
        sleep = int(reset - datetime.datetime.now().timestamp()) + sleep_more
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    response = requests.get(url, headers=headers)

    # 3. Collect the commit information and save full information (basicInfo, additions, deletions, and
    #     changedFiles) of the commit in MongoDB
    result = response.json()
    # deal with the situation that the commit cannot be found or fetched
    if not result:
        raise Exception("Cannot find commit with oid: {} in repo {}".format(commitOid, repository))
    if "sha" not in result:
        print("Cannot fetch information of this commit!")
        print("------------------------------------------")
        return None
    # save the commit information if the information can be fetched
    save_commitBasicInfo(node=result, repository=repository)
    print("    --> Basic info of the commit is saved in MongoDB")
    save_commitChangedInfo(result=result, repository=repository, commitOid=commitOid)
    print("    --> additions and deletions information are updated for commit: {} in repo {}".
          format(commitOid, repository))
    print("    --> {} changedFiles are added to commit: {} in repo {}".
          format(str(len(result["files"])), commitOid, repository))
    print("------------------------------------------")

    return result["commit"]["message"]


# Child function of add_commits_by_repo_basicInfo_paginationRESTAPI(repository, remaining, reset, start_page)
# and save_repo_commit(repository, commitOid)
def save_commitBasicInfo(node, repository):
    """
    Save a node of commit fetched from GitHub API v3 into MongoDB database
    Save also the information of its author and its committer in actor collections of MongoDB
    Save also the information of its author and its committer in actor collections of MongoDB

    :param node: A node of commit from repos-->commits or a document of commit from repos --> commit
    :param repository: owner/name
    :return: No return; the basic information of commit is saved
    """
    oid = node["sha"]
    actionId = None  # This action is not in db1_small MongoDB
    actionType = "Commit"

    # Save author
    author = node["author"]
    if not author:
        author = node["commit"]["author"]["email"]  # For aliens, we use emails to identify them
        authorType = "Alien"
    else:
        author = node["author"]["login"]
        authorType = node["author"]["type"]

    # Save committer
    committer = node["committer"]
    if not committer:
        committer = node["commit"]["committer"]["email"]  # For aliens, we use emails to identify them
        committerType = "Alien"
    else:
        committer = node["committer"]["login"]
        committerType = node["committer"]["type"]

    # Diagnose whether the committer is the author, using both login and email information
    # If the author is a GitHub actor but the committer is an alien,
    # find the actor's email and see whether it matches the committer's.
    if authorType != "Alien" and committerType == "Alien":
        if node["commit"]["author"]["email"] == committer:
            authoredByCommitter = True
        else:
            authoredByCommitter = False
    elif authorType == "Alien" and committerType != "Alien":
        if author == node["commit"]["committer"]["email"]:
            authoredByCommitter = True
        else:
            authoredByCommitter = False
    elif authorType == "Alien" and committerType == "Alien":
        if author == committer:
            authoredByCommitter = True
        else:
            authoredByCommitter = False
    elif authorType != "Alien" and committerType != "Alien":
        if author == committer:
            authoredByCommitter = True
        else:
            authoredByCommitter = False
    else:
        raise Exception("Field: authoredByCommitter -- Check what happened!")

    authoredDate = node["commit"]["author"]["date"]
    committedDate = node["commit"]["committer"]["date"]

    commitUrl = node["html_url"]
    message = node["commit"]["message"]

    treeOid = node["commit"]["tree"]["sha"]

    commentCount = node["commit"]["comment_count"]

    parentCount = len(node["parents"])

    commit = InnovativeAction(
        oid=oid, actionId=actionId, actionType=actionType,
        authorLogin=author, authorType=authorType, committerLogin=committer, committerType=committerType,
        authoredByCommitter=authoredByCommitter, authoredDate=authoredDate, committedDate=committedDate,
        commitRepository=repository, prConnections=None,
        commitUrl=commitUrl, message=message, treeOid=treeOid, commentCount=commentCount, parentCount=parentCount
    )

    # Append parent information
    for i in node["parents"]:
        parent_oid = i["sha"]
        parent_restUrl = i["url"]
        parent_url = i["html_url"]
        parent = Parent(oid=parent_oid, restUrl=parent_restUrl, url=parent_url)
        commit.parents.append(parent)

    commit.save()

    return


# Child function of save_repo_commit(repository, commitOid) and update_changed_info(repository, commitOid,
#   remaining_server, remaining_office, remaining_mac, reset_server, reset_office, reset_mac)
def save_commitChangedInfo(result, repository, commitOid):
    """
    Update the additions, deletions, and changedFiles information of a commit wie identification information of
    repository and commitOid

    :param result: Result JSON file got by repo --> commits --> commitOid
    :param repository: The owner/name of the repository that owns the commit
    :param commitOid: The Git objectId of the commit
    :return: No return; the changed information of the commit is updated in MongoDB
    """
    additions = result["stats"]["additions"]
    deletions = result["stats"]["deletions"]
    files = result["files"]
    changedFilesCount = len(files)

    # Update the other fields
    num_updated = InnovativeAction.objects(commitRepository=repository, oid=commitOid). \
        update(set__additions=additions, set__deletions=deletions, set__changedFilesCount=changedFilesCount)
    if num_updated != 1:
        raise Exception("An error for updating the additions and deletions info of oid: {}".format(commitOid))

    print("    --> additions and deletions information are updated for commit: {} in repo {}".
          format(commitOid, repository))

    # Save the changed files information
    for file in files:
        path = file["filename"]

        additions = file["additions"]
        deletions = file["deletions"]

        oid = file["sha"]
        status = file["status"]
        blobUrl = file["blob_url"]
        rawUrl = file["raw_url"]
        contentsUrl = file["contents_url"]
        # GUESS: If the file is deleted, there is no oid or patch info
        if "patch" in file:
            patch = file["patch"]
        else:
            patch = None

        changedFile = ChangedFile(path=path, additions=additions, deletions=deletions,
                                  oid=oid, status=status, blobUrl=blobUrl, rawUrl=rawUrl, contentsUrl=contentsUrl,
                                  patch=patch)
        num_updated = InnovativeAction.objects(commitRepository=repository, oid=commitOid).update(
            push__changedFiles=changedFile)
        if num_updated != 1:
            raise Exception("An error for updating the changedFiles info of oid: {} in repo {}".
                            format(commitOid, repository))

    return
