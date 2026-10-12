import os
import datetime
import json
import time

import requests

from Classes.actorcollection.actor_alien import ActorAlien
from Classes.actorcollection.actor_bot import ActorBot
from Classes.actorcollection.actor_enterprise import ActorEnterprise
from Classes.actorcollection.actor_mannequin import ActorMannequin
from Classes.actorcollection.actor_org import ActorOrganization
from Classes.actorcollection.actor_user import ActorUser
from Classes.commit.commit import Commit
from Classes.commit.parent import Parent
from Classes.issuecollection.changedfile import ChangedFile
from setup.graphql import get_remaining, sleep_in_seconds, get_reset

# GitHub personal access tokens: supply your own via environment variables (see README.md).
# GITHUB_TOKEN is used by default. update_changed_info() rotates among up to three tokens
# (GITHUB_TOKEN_1, GITHUB_TOKEN_2, GITHUB_TOKEN_3) to spread the REST API rate limit; any that are
# not set fall back to GITHUB_TOKEN. Never hard-code tokens in this file.
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_TOKEN_1 = os.environ.get("GITHUB_TOKEN_1", GITHUB_TOKEN)
GITHUB_TOKEN_2 = os.environ.get("GITHUB_TOKEN_2", GITHUB_TOKEN)
GITHUB_TOKEN_3 = os.environ.get("GITHUB_TOKEN_3", GITHUB_TOKEN)

headers = {
    "Authorization": "token " + GITHUB_TOKEN,
    "User-Agent": "research-data-collection",
    "Accept": "application/vnd.github.v3+json"
}


per_page = 100
sleep_more = 1200


def save_repo_commits(repository, remaining, reset, page):
    """
    Save basic commit information into MongoDB database, and returning the remaining score
    :param page: the start page we search
    :param reset: timestamp for reset the 5000 scores
    :param remaining: remaining scores
    :param repository: owner/name
    :return:
    """
    remaining = int(remaining)
    reset = int(reset)

    print("Working on fetching commits of repo {}".format(repository))

    url = "https://api.github.com/repos/" + repository + "/commits"
    params = {
        "until": "2020-07-14T00:00:00Z",
        "page": page,
        "per_page": per_page
    }

    print("Page {}:".format(str(page)))
    if remaining < 1:
        sleep = reset - datetime.datetime.now().timestamp() + sleep_more
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    response = requests.get(url, headers=headers, params=params)

    result = response.json()
    # Save the commits in MongoDB
    if not result:
        print("This repository has no commits!")
        return
    for node in result:
        save_commit_basic_info(node=node, repository=repository)
    print("  --> {} commits are saved in MongoDB".format(len(result)))

    remaining = int(response.headers["x-ratelimit-remaining"])
    reset = int(response.headers["x-ratelimit-reset"])

    # Detect whether there is a page link
    # If the result has multiple pages, there should be "link" information
    hasNextPage = False
    if "link" in response.headers:
        link = decode_link_info(response.headers["link"])
        if "nextPage" in link:
            hasNextPage = True

    while hasNextPage:
        if remaining < 1:
            sleep = reset - datetime.datetime.now().timestamp() + sleep_more
            print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
            time.sleep(sleep)
            print("Restart! :-)")

        page = page + 1
        print("Page {}: ".format(page) + link["nextPage"])
        response = requests.get(link["nextPage"], headers=headers)

        remaining = int(response.headers["x-ratelimit-remaining"])
        reset = int(response.headers["x-ratelimit-reset"])
        result = response.json()
        # Detect whether there is a next page
        # If this is the last page, there should be no information about "nextPage"
        hasNextPage = False
        if "link" in response.headers:
            link = decode_link_info(response.headers["link"])
            if "nextPage" in link:
                hasNextPage = True
        # Save the commits in MongoDB
        for node in result:
            save_commit_basic_info(node=node, repository=repository)
        print("  --> {} commits are saved in MongoDB".format(len(result)))

    print("------------------------------------------")
    return remaining, reset


def save_repo_commit(repository, commitOid):
    """
    Get the commit information by repo --> commits --> commitOid;
    note that I need to check whether remaining is bigger than 1 because the cost is 1.
    :param repository: owner/name
    :param commitOid: GitObject ID of the commit
    :return: No return, the commit is saved
    """
    print("Working on commit {} in repo {}".format(commitOid, repository))
    # Get a commit, see documentation: https://developer.github.com/v3/repos/commits/#get-a-commit
    url = "https://api.github.com/repos/" + repository + "/commits/" + commitOid

    if get_remaining() < 1:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    response = requests.get(url, headers=headers)

    result = response.json()
    if not result:
        raise Exception("Cannot find commit with oid: {} in repo {}".format(commitOid, repository))

    save_commit_basic_info(node=result, repository=repository)
    print("  --> Basic info of the commit is saved in MongoDB")

    # Save the addition, deleting, and changed-files information
    additions = result["stats"]["additions"]
    deletions = result["stats"]["deletions"]
    num_updated = Commit.objects(repository=repository, oid=commitOid). \
        update(set__additions=additions, set__deletions=deletions)
    if num_updated != 1:
        raise Exception("An error for updating the additions and deletions info of oid: {}".format(commitOid))

    print("  --> additions and deletions information are updated for commit: {} in repo {}".
          format(commitOid, repository))

    # Save the changed files information
    files = result["files"]
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
        num_updated = Commit.objects(repository=repository, oid=commitOid).update(push__changedFiles=changedFile)
        if num_updated != 1:
            raise Exception("An error for updating the changedFiles info of oid: {} in repo {}".
                            format(commitOid, repository))

    print("  --> {} changedFiles are added to commit: {} in repo {}".
          format(str(len(result["files"])), commitOid, repository))
    print("------------------------------------------")


# Using multiple tokens: GITHUB_TOKEN_1 (server), GITHUB_TOKEN_2 (office), GITHUB_TOKEN_3 (mac)
def update_changed_info(repository, commitOid, remaining_server, remaining_office, remaining_mac,
                        reset_server, reset_office, reset_mac):
    """
    Get the additions and deletions information as well as the changedFiles information of a commit
    :param repository: owner/name
    :param commitOid: GitObjectId of a commit
    :param remaining: How many scores are remained
    :param reset: Timestamp for the score that will be reset
    :return:
    """
    print("Working on commit {} in repo {}".format(commitOid, repository))

    remaining_server = int(remaining_server)
    remaining_office = int(remaining_office)
    remaining_mac = int(remaining_mac)
    reset_server = int(reset_server)
    reset_office = int(reset_office)
    reset_mac = int(reset_mac)

    # Get a commit, see documentation: https://developer.github.com/v3/repos/commits/#get-a-commit
    url = "https://api.github.com/repos/" + repository + "/commits/" + commitOid
    if remaining_server > 0:
        headers["Authorization"] = "token " + GITHUB_TOKEN_1
        print("(Using server score):")
        response = requests.get(url, headers=headers)
        remaining_server = response.headers["x-ratelimit-remaining"]
        reset_server = response.headers["x-ratelimit-reset"]
    else:
        if remaining_office > 0:
            print("(Using office score):")
            headers["Authorization"] = "token " + GITHUB_TOKEN_2  # office token
            response = requests.get(url, headers=headers)
            remaining_office = response.headers["x-ratelimit-remaining"]
            reset_office = response.headers["x-ratelimit-reset"]
        else:
            if remaining_mac > 0:
                print("(Using mac score):")
                headers["Authorization"] = "token " + GITHUB_TOKEN_3  # mac token
                response = requests.get(url, headers=headers)
                remaining_mac = response.headers["x-ratelimit-remaining"]
                reset_mac = response.headers["x-ratelimit-reset"]
            else:
                sleep_server = reset_server - datetime.datetime.now().timestamp() + sleep_more
                sleep_office = reset_office - datetime.datetime.now().timestamp() + sleep_more - 1200
                sleep_mac = reset_mac - datetime.datetime.now().timestamp() + sleep_more - 2400
                sleep = max(sleep_server, sleep_office, sleep_mac)
                if sleep > 0:
                    print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
                    time.sleep(sleep)
                    print("Restart! :-)")
                    remaining_office = 5000
                    remaining_mac = 5000
                headers["Authorization"] = "token " + GITHUB_TOKEN_1
                print("(Using server score:")
                response = requests.get(url, headers=headers)
                remaining_server = response.headers["x-ratelimit-remaining"]
                reset_server = response.headers["x-ratelimit-reset"]

    # response = requests.get(url, headers=headers)
    #
    # remaining = response.headers["x-ratelimit-remaining"]
    # reset = response.headers["x-ratelimit-reset"]

    result = response.json()
    if not result:
        raise Exception("Cannot find commit with oid: {} in repo {}".format(commitOid, repository))

    # Save the addition, deleting, and changed-files information
    additions = result["stats"]["additions"]
    deletions = result["stats"]["deletions"]
    num_updated = Commit.objects(repository=repository, oid=commitOid).\
        update(set__additions=additions, set__deletions=deletions)
    if num_updated != 1:
        raise Exception("An error for updating the additions and deletions info of oid: {}".format(commitOid))

    print("  --> additions and deletions information are updated for commit: {} in repo {}".
          format(commitOid, repository))

    # Save the changed files information
    for file in result["files"]:
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
        num_updated = Commit.objects(repository=repository, oid=commitOid).update(push__changedFiles=changedFile)
        if num_updated != 1:
            raise Exception("An error for updating the changedFiles info of oid: {} in repo {}".
                            format(commitOid, repository))

    print("  --> {} changedFiles are added to commit: {} in repo {}".
          format(str(len(result["files"])), commitOid, repository))
    print("------------------------------------------")
    return remaining_server, remaining_office, remaining_mac, reset_server, reset_office, reset_mac


def save_commit_basic_info(node, repository):
    """
    Save a node of commit fetched from GitHub API v3 into MongoDB database
    :param node: A node of commit from repos-->commits or a document of commit from repos --> commit
    :param repository: owner/name
    :return: No return; the basic information of commit is saved
    """
    oid = node["sha"]

    # In the commit, the author and committer exist, but they do no exist in the node.

    # Save author
    author = node["author"]
    if not author:
        author = node["commit"]["author"]["email"]  # For aliens, we use emails to identify them
        authorType = "Alien"
    else:
        author = node["author"]["login"]
        authorType = node["author"]["type"]
    authorId = get_actor_id(actorType=authorType, identification=author)
    if not authorId:
        authorId = save_author(actorType=authorType, node=node)

    # Save committer
    committer = node["committer"]
    if not committer:
        committer = node["commit"]["committer"]["email"]  # For aliens, we use emails to identify them
        committerType = "Alien"
    else:
        committer = node["committer"]["login"]
        committerType = node["committer"]["type"]
    committerId = get_actor_id(actorType=committerType, identification=committer)
    if not committerId:
        committerId = save_committer(actorType=committerType, node=node)

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

    repository = repository

    commitUrl = node["html_url"]
    message = node["commit"]["message"]

    treeOid = node["commit"]["tree"]["sha"]

    commentCount = node["commit"]["comment_count"]

    commit = Commit(oid=oid, author=author, authorType=authorType, authorId=authorId,
                    committer=committer, committerType=committerType, committerId=committerId,
                    authoredByCommitter=authoredByCommitter, authoredDate=authoredDate, committedDate=committedDate,
                    repository=repository,
                    commitUrl=commitUrl, message=message, treeOid=treeOid, commentCount=commentCount)
    # Append parent information
    for i in node["parents"]:
        parent_oid = i["sha"]
        parent_restUrl = i["url"]
        parent_url = i["html_url"]
        parent = Parent(oid=parent_oid, restUrl=parent_restUrl, url=parent_url)
        commit.parents.append(parent)

    commit.save()


def get_actor_id(actorType, identification):
    """
    Get the object ID of an actor; note that the actor can be an alien with no GitHub login
    :param actorType: User, Bot, Organization, EnterpriseUserAccount, Mannequin or Alien
    :param identification: The login of a GitHub account or the email of an alien
    :return: actor_obj: The object ID
    """
    if actorType == "User":
        actors = ActorUser.objects(login=identification).only("id")
    elif actorType == "Bot":
        actors = ActorBot.objects(login=identification).only("id")
    elif actorType == "Organization":
        actors = ActorOrganization.objects(login=identification).only("id")
    elif actorType == "EnterpriseUserAccount":
        actors = ActorEnterprise.objects(login=identification).only("id")
    elif actorType == "Mannequin":
        actors = ActorMannequin.objects(login=identification).only("id")
    elif actorType == "Alien":
        actors = ActorAlien.objects(email=identification).only("id")
    else:
        raise Exception("{} is an unexpected actor type. Accepted actorTypes are: User, Bot, Organization, "
                        + "EnterpriseUserAccount, Mannequin, and Alien.".format(actorType))

    if len(actors) == 1:
        actor_obj = actors[0]["id"]
    elif len(actors) == 0:
        actor_obj = None
    else:
        raise Exception("There are no {}s or multiple {}s with identification {}, which should be the primary key.".
                        format(actorType, actorType, identification))

    return actor_obj


def save_author(actorType, node):
    """
    Save information of the author of a commit into the MongoDB database; note that the author is the agent
    who made code changes while the committer is the agent who applied the changes into the repository.
    :param actorType: User, Bot, Organization, EnterpriseUserAccount, Mannequin, or Alien
    :param node: The node of a commit fetched from GitHub REST API v3
    :return: object ID of the saved actor; A document for the actor is also saved in MongoDB.
    """
    # Check whether the actor is an alien of GitHub, with not GitHub login
    if actorType != "Alien":
        login = node["author"]["login"]
        actorType = node["author"]["type"]
        email = node["commit"]["author"]["email"]
        name = node["commit"]["author"]["name"]
        avatarUrl = node["author"]["avatar_url"]
        if actorType == "User":
            actor = ActorUser(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Bot":
            actor = ActorBot(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Organization":
            actor = ActorOrganization(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "EnterpriseUserAccount":
            actor = ActorEnterprise(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Mannequin":
            actor = ActorMannequin(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        else:
            raise Exception("{} is an unexpected actor type. Accepted actorTypes are: User, Bot, Organization, "
                            + "EnterpriseUserAccount, Mannequin, or Alien.".format(actorType))
    else:  # if actorType == "Alien"
        email = node["commit"]["author"]["email"]
        name = node["commit"]["author"]["name"]
        actor = ActorAlien(email=email, name=name)

    actor.save()
    return actor["id"]


def save_committer(actorType, node):
    """
    Save information of the committer of a commit into the MongoDB database; note that the author is the agent
    who made code changes while the committer is the agent who applied the changes into the repository.
    :param actorType: User, Bot, Organization, EnterpriseUserAccount, Mannequin, or Alien
    :param node: The node of a commit fetched from GitHub REST API v3
    :return: object ID of the saved actor; A document for the actor is also saved in MongoDB.
    """
    # Check whether the actor is an alien of GitHub, with not GitHub login
    if actorType != "Alien":
        login = node["committer"]["login"]
        actorType = node["committer"]["type"]
        email = node["commit"]["committer"]["email"]
        name = node["commit"]["committer"]["name"]
        avatarUrl = node["committer"]["avatar_url"]
        if actorType == "User":
            actor = ActorUser(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Bot":
            actor = ActorBot(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Organization":
            actor = ActorOrganization(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "EnterpriseUserAccount":
            actor = ActorEnterprise(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        elif actorType == "Mannequin":
            actor = ActorMannequin(login=login, actorType=actorType, email=email, name=name, avatarUrl=avatarUrl)
        else:
            raise Exception("{} is an unexpected actor type. Accepted actorTypes are: User, Bot, Organization, "
                            + "EnterpriseUserAccount, Mannequin, or Alien.".format(actorType))
    else:  # if actorType == "Alien"
        email = node["commit"]["committer"]["email"]
        name = node["commit"]["committer"]["name"]
        actor = ActorAlien(email=email, name=name)

    actor.save()
    return actor["id"]


def decode_link_info(link):
    """
    Convert the string of link in the header of a GitHub-REST-API-v3 response to a dictionary for link information
    :param link: The string of link information about next, last, first, or prev (i.e.,previous) page
    :return: link_dic: a dictionary of urls for the page linkages
    """
    link_dic = {}
    for element in link.split(',', 3):
        urlPart = element.split(';')[0]
        relPart = element.split(';')[1]
        rel = relPart.split('rel="')[1].split('"')[0]
        # Translate VALUES of rel into easy-to-understand KEYS
        if rel == "next":
            link_dic["nextPage"] = urlPart.split('<')[1].split('>')[0]
        elif rel == "last":
            link_dic["lastPage"] = urlPart.split('<')[1].split('>')[0]
        elif rel == "first":
            link_dic["firstPage"] = urlPart.split('<')[1].split('>')[0]
        elif rel == "prev":
            link_dic["previousPage"] = urlPart.split('<')[1].split('>')[0]
        else:
            raise Exception("the link '{}' has an unexpected structure!".format(link))

    return link_dic


def save_text_file(path, response):
    """
    Save the response as a text file of JSON type
    :param path: The full path of the JSON file
    :param response: What is returned by a call toward GitHub REST API v3
    :return: No returns. The information is saved in the file with path=path
    """
    result_text = json.dumps(response.json(), indent=4)
    file = open(path, "w")
    file.write(result_text)
    file.close()

