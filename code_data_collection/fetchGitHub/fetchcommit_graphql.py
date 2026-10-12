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
from fetchGitHub.fetchcommit import get_actor_id
from setup.graphql import get_remaining, sleep_in_seconds, get_reset, run_query_variable


# Get basic information, additions, deletions, and the number of changed files of a commit and save it in MongoDB
# Child function of PullRequestCommitEvent
def save_repo_commit_graphQL(repository, commitOid):
    """
    Get basic information, additions, deletions, and the number of changed files of a commit and save it in MongoDB
    1. Design a query for fetching data fields needed in Commit class (except changedFiles) 
    2. Call information of the commit by GitHub GraphQL API v4
    3. Save the commit information into MongoDB
    
    Notes
    1. Add a new data field: changedFilesCount

    :param repository: The owner/name of the repository that owns this commit
    :param commitOid: GitObject ID of the commit
    :return: No return, the commit is saved
    """
    cost = 1

    print("Working on commit {} in repo {} by using GitHub GraphQL API v4".format(commitOid, repository))

    # 1. Design a query for fetching data fields needed in Commit class (except changedFiles)
    delimiter = "/"
    owner = repository.split(delimiter)[0]
    name = repository.split(delimiter)[1]

    query_commit = """
    query($owner: String!, $name: String!, $commitOid: GitObjectID!) {
      rateLimit{
        cost
        remaining
        resetAt
      }
      repository(owner: $owner, name: $name) { 
        object(oid:$commitOid){
          repository{
            nameWithOwner
          }
          oid
          commitResourcePath
          commitUrl
          
          ...on Commit{
            author{
              name
              email
              date
              user{
                login
                __typename
                avatarUrl
              }
            }
            committer{
              name
              email
              date
              user{
                login
                __typename
              }
            }
            authoredByCommitter
            authoredDate
            committedDate
            repository{
              nameWithOwner
            }
            commitUrl
            message
            tree{
              oid
            }
            comments{
              totalCount
            }
            additions
            deletions
            changedFiles
            parents(first: 20){
              totalCount
              nodes{
                oid
                url
                resourcePath
              }
            }
          }
          
        }
      }
    }
    """
    variables_commit = {
        "owner": owner,
        "name": name,
        "commitOid": commitOid
    }

    # 2. Call information of the commit by GitHub GraphQL API v4
    if get_remaining() < cost:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
    result = run_query_variable(query_commit, variables_commit)

    # 3. Save the commit information into MongoDB
    if not result["data"]["repository"]["object"]:
        raise Exception("Cannot find commit with oid: {} in repo {}".format(commitOid, repository))
    node = result["data"]["repository"]["object"]

    save_commitInfo_graphQL(node=node)

    print("    --> Basic info of the commit is saved in MongoDB")
    print("    --> additions and deletions information are updated for commit: {} in repo {}".
          format(commitOid, repository))
    print("    --> The number of changedFiles are added to commit: {} in repo {}".
          format(commitOid, repository))
    print("------------------------------------------")


# Child function of save_repo_commit_graphQL(repository, commitOid)
def save_commitInfo_graphQL(node):
    """
    Save the commit information fetched from GitHub GraphQL API v4

    :param node: The node of object by repository -- GitHub GraphQL API v4
    :return: No return; the commit information is saved in MongoDB
    """
    # Basic info of a commit
    oid = node["oid"]

    # Save author
    author = node["author"]
    if "user" in author:
        author = node["author"]["user"]["login"]
        authorType = node["author"]["user"]["__typename"]
    else:
        author = node["author"]["email"]  # For aliens, we use emails to identify them
        authorType = "Alien"
    authorId = get_actor_id(actorType=authorType, identification=author)
    if not authorId:
        authorId = save_author_graphQL(actorType=authorType, node=node)

    # Save committer
    committer = node["committer"]
    if "user" in committer:
        committer = node["committer"]["user"]["login"]
        committerType = node["committer"]["user"]["__typename"]
    else:
        committer = node["committer"]["email"]  # For aliens, we use emails to identify them
        committerType = "Alien"
    committerId = get_actor_id(actorType=committerType, identification=committer)
    if not committerId:
        committerId = save_committer_graphQL(actorType=committerType, node=node)

    authoredByCommitter = node["authoredByCommitter"]

    authoredDate = node["authoredDate"]
    committedDate = node["committedDate"]

    repository = node["repository"]["nameWithOwner"]

    commitUrl = node["commitUrl"]
    message = node["message"]

    treeOid = node["tree"]["oid"]

    commentCount = node["comments"]["totalCount"]

    parents = []
    for i in node["parents"]["nodes"]:
        parent_oid = i["oid"]
        parent_restUrl = None
        parent_url = i["url"]
        parent = Parent(oid=parent_oid, restUrl=parent_restUrl, url=parent_url)
        parents.append(parent)

    # Changed info (without changedFiles but with changedFilesCount)
    additions = node["additions"]
    deletions = node["deletions"]

    changedFilesCount = node["changedFiles"]

    commit = Commit(oid=oid, author=author, authorType=authorType, authorId=authorId,
                    committer=committer, committerType=committerType, committerId=committerId,
                    authoredByCommitter=authoredByCommitter,
                    authoredDate=authoredDate, committedDate=committedDate,
                    repository=repository,
                    commitUrl=commitUrl, message=message, treeOid=treeOid, commentCount=commentCount,
                    additions=additions, deletions=deletions, changedFilesCount=changedFilesCount,
                    parents=parents)

    commit.save()


# Child function of save_commitBasicInfo(node, repository)
def save_author_graphQL(actorType, node):
    """
    Save information of the author of a commit into the MongoDB database; note that the author is the agent
    who made code changes while the committer is the agent who applied the changes into the repository.

    :param actorType: User, Bot, Organization, EnterpriseUserAccount, Mannequin, or Alien
    :param node: The node of a commit fetched from GitHub REST API v3
    :return: object ID of the saved actor; A document for the actor is also saved in MongoDB.
    """
    # Check whether the actor is an alien of GitHub, with not GitHub login
    if actorType != "Alien":
        login = node["author"]["user"]["login"]
        actorType = node["author"]["user"]["__typename"]
        avatarUrl = node["author"]["user"]["avatar_url"]
        email = node["author"]["email"]
        name = node["author"]["name"]
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
        email = node["author"]["email"]
        name = node["author"]["name"]
        actor = ActorAlien(email=email, name=name)

    actor.save()
    return actor["id"]


# Child function of save_commitBasicInfo(node, repository)
def save_committer_graphQL(actorType, node):
    """
    Save information of the committer of a commit into the MongoDB database; note that the author is the agent
    who made code changes while the committer is the agent who applied the changes into the repository.

    :param actorType: User, Bot, Organization, EnterpriseUserAccount, Mannequin, or Alien
    :param node: The node of a commit fetched from GitHub REST API v3
    :return: object ID of the saved actor; A document for the actor is also saved in MongoDB.
    """
    # Check whether the actor is an alien of GitHub, with not GitHub login
    if actorType != "Alien":
        login = node["committer"]["user"]["login"]
        actorType = node["committer"]["user"]["__typename"]
        avatarUrl = node["committer"]["user"]["avatar_url"]
        email = node["commit"]["committer"]["email"]
        name = node["commit"]["committer"]["name"]
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
        email = node["committer"]["email"]
        name = node["committer"]["name"]
        actor = ActorAlien(email=email, name=name)

    actor.save()
    return actor["id"]


