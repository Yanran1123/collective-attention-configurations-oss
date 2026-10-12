import time

# Basic information about all issues of an repository
from Classes.issuecollection.associatedPR import AssociatedPR
from Classes.issuecollection.changedfile import ChangedFile
from Classes.issuecollection.edit import Edit
from Classes.issuecollection.issue import Issue
from Classes.issuecollection.suggestedreviewer import SuggestedReviewer
from setup.graphql import run_query_variable, get_remaining, sleep_in_seconds, get_reset
from Classes.issuecollection.pullrequest import PullRequest


# *************************************
# Get basic info of pull requests of a repository

def add_prs_part1(owner, name):

    first = 50

    query_total_count = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name){
        pullRequests(first:1){

          totalCount
          
        }
      }
    }
    """
    variables_total_count = {
        "owner": owner,
        "name": name
    }
    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    total_count = result["data"]["repository"]["pullRequests"]["totalCount"]
    print("There are in total {} pullRequests for {}/{}".format(str(total_count), owner, name))

    if total_count == 0:
        return

    query_part1_firstPage = """
    query($owner: String!, $name: String!, $first: Int!) {
      repository(owner: $owner, name: $name){
        pullRequests(first:$first, orderBy: {direction: ASC, field:CREATED_AT}){

          pageInfo{
            hasNextPage
            endCursor
          }

          nodes{

            repository{
              nameWithOwner
            }
            number
            author{
              login
              __typename
            }
            authorAssociation

            createdAt
            createdViaEmail
            publishedAt
            updatedAt

            databaseId
            resourcePath
            url
            
            title
            body
            bodyHTML
            bodyText

            editor{
              login
              __typename
            }
            includesCreatedEdit
            lastEditedAt
            userContentEdits{
              totalCount
            }

          }
        }
      } 
    }
    """
    variables_part1_firstPage = {
        "owner": owner,
        "name": name,
        "first": first
    }
    hasNextPage, endCursor, prs = fetch_pr_nodes(query=query_part1_firstPage, variables=variables_part1_firstPage,
                                                 cost=5)

    page = 1
    for pr in prs:
        save_one_pr_node_part1(pr)
    print("  Page {}:".format(page))
    print("  {} pullRequests are added".format(str(len(prs))))

    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
        query($owner: String!, $name: String!, $after_cursor: String!, $first: Int!) {
          repository(owner: $owner, name: $name){
            pullRequests(first:$first, after: $after_cursor, orderBy: {direction: ASC, field:CREATED_AT}){
    
              pageInfo{
                hasNextPage
                endCursor
              }
    
              nodes{
    
                repository{
                  nameWithOwner
                }
                number
                author{
                  login
                  __typename
                }
                authorAssociation
    
                createdAt
                createdViaEmail
                publishedAt
                updatedAt
    
                databaseId
                resourcePath
                url
    
                title
                body
                bodyHTML
                bodyText
    
                editor{
                  login
                  __typename
                }
                includesCreatedEdit
                lastEditedAt
                userContentEdits{
                  totalCount
                }
    
              }
            }
          } 
        }
        """
        variables_next_page = {
            "owner": owner,
            "name": name,
            "after_cursor": after_cursor,
            "first": first
        }
        hasNextPage, after_cursor, prs = fetch_pr_nodes(query=query_next_page,
                                                        variables=variables_next_page,
                                                        cost=5)
        for pr in prs:
            save_one_pr_node_part1(pr)
        print("  Page {}:".format(page))
        print("  {} pullRequests are added".format(str(len(prs))))

    print("------------------------------------------------------------")


def add_pr_part1(owner, name, number):
    cost = 1

    query_part1 = """
    query($owner: String!, $name: String!, $number: Int!){
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          
            repository{
              nameWithOwner
            }
            number
            author{
              login
              __typename
            }
            authorAssociation
    
            createdAt
            createdViaEmail
            publishedAt
            updatedAt
    
            databaseId
            resourcePath
            url
            
            title
            body
            bodyHTML
            bodyText
    
            editor{
              login
              __typename
            }
            includesCreatedEdit
            lastEditedAt
            userContentEdits{
              totalCount
            }
        }
      }
    }
    """
    variables_part1 = {
        "owner": owner,
        "name": name,
        "number": number
    }
    pr = fetch_pr_node(query=query_part1, variables=variables_part1, cost=cost)
    save_one_pr_node_part1(pr)
    

# Fetch pullRequest nodes
def fetch_pr_nodes(query, variables, cost):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :param cost: Estimated cost of this call
    :return: hasNextPage, endCursor, nodes
    """
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequests"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequests"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["pullRequests"]["nodes"]

        return hasNextPage, endCursor, nodes


# Child function of add_prs_part1
def save_one_pr_node_part1(pr):
    """
    This function get a pr node and save information in the node into MongoDB
    :param pr: A pr node with data fields in both Issue and PullRequest objects
    :return: No return -- Check MongoDB to see the results
    """
    repository = pr["repository"]["nameWithOwner"]
    number = pr["number"]
    # Some issues have no author, e.g., issue #62, tensorflow/tensorflow
    author = pr["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = pr["author"]["login"]
        authorType = pr["author"]["__typename"]
    authorAssociation = pr["authorAssociation"]

    createdAt = pr["createdAt"]
    createdViaEmail = pr["createdViaEmail"]
    publishedAt = pr["publishedAt"]
    updatedAt = pr["updatedAt"]

    databaseId = pr["databaseId"]
    resourcePath = pr["resourcePath"]
    url = pr["url"]

    title = pr["title"]
    body = pr["body"]
    bodyHTML = pr["bodyHTML"]
    bodyText = pr["bodyText"]

    editor = pr["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = pr["editor"]["login"]
        editorType = pr["editor"]["__typename"]
    includesCreatedEdit = pr["includesCreatedEdit"]
    lastEditedAt = pr["lastEditedAt"]
    editCount = pr["userContentEdits"]["totalCount"]

    pr_obj = PullRequest(repository=repository, number=number, author=author, authorType=authorType,
                         authorAssociation=authorAssociation, createdAt=createdAt, createdViaEmail=createdViaEmail,
                         publishedAt=publishedAt, updatedAt=updatedAt,
                         databaseId=databaseId, resourcePath=resourcePath, url=url,
                         title=title, body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                         editor=editor, editorType=editorType, includesCreatedEdit=includesCreatedEdit,
                         lastEditedAt=lastEditedAt, editCount=editCount)

    pr_obj.save()


# Update the data-field Part2 into MongoDB: only prs have those fields
def update_pr_part2(owner, name, number):
    cost = 1

    query_part2 = """
    query($owner: String!, $name: String!, $number: Int!){
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          permalink
          revertResourcePath
          revertUrl
          
          maintainerCanModify
          
          baseRefName
          baseRefOid
          baseRepository{
            nameWithOwner
          }
    
          headRefName
          headRefOid
          headRepository{
            nameWithOwner
          }
    
          additions
          deletions
          files{
            totalCount
          }
    
          checksResourcePath
          checksUrl
          
          closed
          closedAt
    
          mergeCommit{
            oid
          }
          mergeable
          merged
          mergedAt
          mergedBy{
            login
            __typename
          }
        }
      }
    }
    """
    variables_part2 = {
        "owner": owner,
        "name": name,
        "number": number
    }
    pr = fetch_pr_node(query=query_part2, variables=variables_part2, cost=cost)

    repository = owner + "/" + name

    # Information in the pullRequest node
    permalink = pr["permalink"]
    revertResourcePath = pr["revertResourcePath"]
    revertUrl = pr["revertUrl"]
    maintainerCanModify = pr["maintainerCanModify"]

    baseRefName = pr["baseRefName"]
    baseRefOid = pr["baseRefOid"]
    baseRepository = pr["baseRepository"]["nameWithOwner"]

    headRefName = pr["headRefName"]
    headRefOid = pr["headRefOid"]
    headRepository = pr["headRepository"]
    if not headRepository:
        headRepository = ""
    else:
        headRepository = pr["headRepository"]["nameWithOwner"]

    additions = pr["additions"]
    deletions = pr["deletions"]
    changedFiles = pr["files"]
    if not changedFiles:
        changedFilesCount = 0
    else:
        changedFilesCount = pr["files"]["totalCount"]

    checksResourcePath = pr["checksResourcePath"]
    checksUrl = pr["checksUrl"]

    closed = pr["closed"]
    closedAt = pr["closedAt"]

    mergeCommit = pr["mergeCommit"]
    if not mergeCommit:
        mergeCommit = ""
    else:
        mergeCommit = pr["mergeCommit"]["oid"]
    mergeable = pr["mergeable"]
    merged = pr["merged"]
    mergedAt = pr["mergedAt"]
    mergedBy = pr["mergedBy"]
    if not mergedBy:
        mergedBy = mergedBy
        mergedByType = ""
    else:
        mergedBy = pr["mergedBy"]["login"]
        mergedByType = pr["mergedBy"]["__typename"]

    # num_updated = PullRequest.objects(repository=repository, number=number).\
    #     update_one(push__permalink=permalink, push__revertResourcePath=revertResourcePath, push__revertUrl=revertUrl,
    #                push__maintainerCanModify=maintainerCanModify,
    #                push__baseRefName=baseRefName, push__baseRefOid=baseRefOid, push__baseRepository=baseRepository,
    #                push__headRefName=headRefName, push__headRefOid=headRefOid, push__headRepository=headRepository,
    #                push__additions=additions, push__deletions=deletions, push__changedFilesCount=changedFilesCount,
    #                push__checksResourcePath=checksResourcePath, push__checksUrl=checksUrl,
    #                push__mergeCommit=mergeCommit, push__mergeable=mergeable,
    #                push__merged=merged, push__mergedAt=mergedAt,
    #                push__mergedBy=mergedBy, push__mergedByType=mergedByType,
    #                )

    # The set operator sets the value of a field, but push adds elements to the end of an array if the array exists
    # and creates a new array if it does not.
    num_updated = PullRequest.objects(repository=repository, number=number). \
        update_one(set__permalink=permalink, set__revertResourcePath=revertResourcePath, set__revertUrl=revertUrl,
                   set__maintainerCanModify=maintainerCanModify,
                   set__baseRefName=baseRefName, set__baseRefOid=baseRefOid, set__baseRepository=baseRepository,
                   set__headRefName=headRefName, set__headRefOid=headRefOid, set__headRepository=headRepository,
                   set__additions=additions, set__deletions=deletions, set__changedFilesCount=changedFilesCount,
                   set__checksResourcePath=checksResourcePath, set__checksUrl=checksUrl,
                   set__closed=closed, set__closedAt=closedAt,
                   set__mergeCommit=mergeCommit, set__mergeable=mergeable,
                   set__merged=merged, set__mergedAt=mergedAt,
                   set__mergedBy=mergedBy, set__mergedByType=mergedByType,
                   )
    if num_updated != 1:
        raise Exception("No pull request with number {} in repo {}".format(str(number), repository))

    print("Part2 of pullRequest #{} in repo {}/{} is updated".format(str(number), owner, name))
    print("------------------------------------------------------------")


# Fetch pullRequest node
def fetch_pr_node(query, variables, cost):
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    # Check whether the repository exists
    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        node = result["data"]["repository"]["pullRequest"]

    return node


# The end of getting basic information of pull requests of a repository
# ***********************************


# Update base AssociationPR objects of a pullRequest
def update_pr_base_associationPRs(owner, name, number):
    first = 50
    cost = 5

    # ------------------------------------
    # Get total count
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          baseRef{
            associatedPullRequests(first: 1, orderBy: {direction: ASC, field:CREATED_AT}){
            
              totalCount
              
            }
          }
        }
      }
    }
    """
    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }
    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    if not result["data"]["repository"]["pullRequest"]["baseRef"]:
        print("PullRequest #{} of repo {}/{} has no baseRef".format(str(number), owner, name))
        return

    total_count = result["data"]["repository"]["pullRequest"]["baseRef"]["associatedPullRequests"]["totalCount"]
    print("There are in total {} pullRequests associated with the baseRef of pullRequest # {} in repo {}/{}".
          format(str(total_count), str(number), owner, name))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Get the first page

    page = 1

    query_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!) {

      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          baseRef{
            associatedPullRequests(first: $first, orderBy: {direction: ASC, field:CREATED_AT}){
              
              pageInfo{
                hasNextPage
                endCursor
              }
              
              nodes{
                repository{
                  nameWithOwner
                }
                number
              }
              
            }
          }
        }
      }
    }
    """
    variables_first_page = {
        "owner": owner,
        "name": name,
        "number": number,
        "first": first
    }
    hasNextPage, endCursor, associatedPRs = \
        fetch_base_associatedPR_nodes(query=query_first_page, variables=variables_first_page, cost=cost)

    repository = owner + "/" + name

    for associatedPR in associatedPRs:
        """
        Deal with an EXCEPTION that the baseRef PullRequest #1 of nearai/program_synthesis has one associated PR based on
        the information of total count. However, the node is null! 
        SOLUTION. Ignore the inconsistent total count, push info based on the actual nodes that we can access.
        """
        if not associatedPR:
            print("This node of baseAssociatedPR is null. No associatedPR is added")
        else:
            a_repo = associatedPR["repository"]["nameWithOwner"]
            a_number = associatedPR["number"]
            associatedPR_obj = AssociatedPR(number=a_number, repository=a_repo)
            num_updated = PullRequest.objects(repository=repository, number=number). \
                update_one(push__baseAssociatedPRs=associatedPR_obj)
            if num_updated != 1:
                raise Exception("No pull request with number {} in repo {} -- MongoDB database".format(str(number), repository))

    print("Page {}".format(str(page)))
    print("{} base associatedPRs are added to pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(associatedPRs)), str(number), owner, name))

    # ----------------------------
    # Get the following pages
    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {
        
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              baseRef{
                associatedPullRequests(first: $first, after: $after_cursor, orderBy: {direction: ASC, field:CREATED_AT}){
                  
                  pageInfo{
                    hasNextPage
                    endCursor
                  }
                  
                  nodes{
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  
                }
              }
            }
          }
        }
        """
        variables_next_page = {
            "owner": owner,
            "name": name,
            "number": number,
            "first": first,
            "after_cursor":after_cursor
        }
        hasNextPage, after_cursor, associatedPRs = fetch_base_associatedPR_nodes(query=query_next_page,
                                                                                 variables=variables_next_page,
                                                                                 cost=cost)
        for associatedPR in associatedPRs:
            if not associatedPR:
                print("This node of baseAssociatedPR is null. No associatedPR is added")
            else:
                a_repo = associatedPR["repository"]["nameWithOwner"]
                a_number = associatedPR["number"]
                associatedPR_obj = AssociatedPR(number=a_number, repository=a_repo)
                num_updated = PullRequest.objects(repository=repository, number=number). \
                    update_one(push__baseAssociatedPRs=associatedPR_obj)
                if num_updated != 1:
                    raise Exception("No pull request with number {} in repo {} -- MongoDB database".format(str(number), repository))

        print("Page {}".format(str(page)))
        print("{} base associatedPRs are added to pullRequest #{} in repo {}/{} -- MongoDB database".
              format(str(len(associatedPRs)), str(number), owner, name))

    print("------------------------------------------------------------")
    # ------------------------------


# Fetch base AssociatedPR nodes
def fetch_base_associatedPR_nodes(query, variables, cost):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :param cost: Estimated cost of this call
    :return: hasNextPage, endCursor, nodes
    """
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequest"]["baseRef"]["associatedPullRequests"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequest"]["baseRef"]["associatedPullRequests"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["pullRequest"]["baseRef"]["associatedPullRequests"]["nodes"]

        return hasNextPage, endCursor, nodes


# Update head AssociationPR objects of a pullRequest
def update_pr_head_associationPRs(owner, name, number):
    first = 50
    cost = 5

    # ------------------------------------
    # Get total count
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          headRef{
            associatedPullRequests(first: 1, orderBy: {direction: ASC, field:CREATED_AT}){

              totalCount

            }
          }
        }
      }
    }
    """
    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }
    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    """
    The headRef can be null even the headName and headOid is not null. The reason may be that the headRef is unavailable.
    """
    if not result["data"]["repository"]["pullRequest"]["headRef"]:
        print("PullRequest #{} of repo {}/{} has no headRef".format(str(number), owner, name))
        print("------------------------------------------------------------")
        return

    total_count = result["data"]["repository"]["pullRequest"]["headRef"]["associatedPullRequests"]["totalCount"]
    print("There are in total {} pullRequests associated with the headRef of pullRequest #{} repo {}/{}".
          format(str(total_count), str(number), owner, name))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Get the first page

    page = 1

    query_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!) {

      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          headRef{
            associatedPullRequests(first: $first, orderBy: {direction: ASC, field:CREATED_AT}){

              pageInfo{
                hasNextPage
                endCursor
              }

              nodes{
                repository{
                  nameWithOwner
                }
                number
              }

            }
          }
        }
      }
    }
    """
    variables_first_page = {
        "owner": owner,
        "name": name,
        "number": number,
        "first": first
    }
    hasNextPage, endCursor, associatedPRs = \
        fetch_head_associatedPR_nodes(query=query_first_page, variables=variables_first_page, cost=cost)

    repository = owner + "/" + name

    for associatedPR in associatedPRs:
        if not associatedPR:
            print("This node of headAssociatedPR is null. No associatedPR is added")
        else:
            a_repo = associatedPR["repository"]["nameWithOwner"]
            a_number = associatedPR["number"]
            associatedPR_obj = AssociatedPR(number=a_number, repository=a_repo)
            num_updated = PullRequest.objects(repository=repository, number=number). \
                update_one(push__headAssociatedPRs=associatedPR_obj)
            if num_updated != 1:
                raise Exception(
                    "No pull request with number {} in repo {} -- MongoDB database".format(str(number), repository))

    print("Page {}".format(str(page)))
    print("{} head associatedPRs are added to pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(associatedPRs)), str(number), owner, name))

    # ----------------------------
    # Get the following pages
    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {

          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              headRef{
                associatedPullRequests(first: $first, after: $after_cursor, orderBy: {direction: ASC, field:CREATED_AT}){

                  pageInfo{
                    hasNextPage
                    endCursor
                  }

                  nodes{
                    repository{
                      nameWithOwner
                    }
                    number
                  }

                }
              }
            }
          }
        }
        """
        variables_next_page = {
            "owner": owner,
            "name": name,
            "number": number,
            "first": first,
            "after_cursor": after_cursor
        }
        hasNextPage, after_cursor, associatedPRs = fetch_head_associatedPR_nodes(query=query_next_page,
                                                                                 variables=variables_next_page,
                                                                                 cost=cost)
        for associatedPR in associatedPRs:
            if not associatedPR:
                print("This node of headAssociatedPR is null. No associatedPR is added")
            else:
                a_repo = associatedPR["repository"]["nameWithOwner"]
                a_number = associatedPR["number"]
                associatedPR_obj = AssociatedPR(number=a_number, repository=a_repo)
                num_updated = PullRequest.objects(repository=repository, number=number). \
                    update_one(push__headAssociatedPRs=associatedPR_obj)
                if num_updated != 1:
                    raise Exception(
                        "No pull request with number {} in repo {} -- MongoDB database".format(str(number), repository))

        print("Page {}".format(str(page)))
        print("{} head associatedPRs are added to pullRequest #{} in repo {}/{} -- MongoDB database".
              format(str(len(associatedPRs)), str(number), owner, name))

    print("------------------------------------------------------------")
    # ------------------------------


# Fetch head AssociatedPR nodes
def fetch_head_associatedPR_nodes(query, variables, cost):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :param cost: Estimated cost of this call
    :return: hasNextPage, endCursor, nodes
    """
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequest"]["headRef"]["associatedPullRequests"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequest"]["headRef"]["associatedPullRequests"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["pullRequest"]["headRef"]["associatedPullRequests"]["nodes"]

        return hasNextPage, endCursor, nodes


# Update ChangedFile objects of a pullRequest
def update_pr_changed_files(owner, name, number):
    first = 50
    cost = 5  # the cost of fetching nodes

    # ------------------------------------
    # Get total count
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
    
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          files(first:1){
          
            totalCount

          }
        }
      }
    }
    """
    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }
    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)
    """
    When the diff is not available, the files connection is none. It may be not because that it actually has no
    commits. The files changed in the web is infinity.
    Example: pullRequest #19 of awslabs/gluon-ts
    """
    if not result["data"]["repository"]["pullRequest"]["files"]:
        print("Exception: The files connection is none. The diff is unavailable.")
        print("------------------------------------------------------------")
        return

    total_count = result["data"]["repository"]["pullRequest"]["files"]["totalCount"]
    print("There are in total {} files changed by pullRequest #{} of repo {}/{}".
          format(str(total_count), str(number), owner, name))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Get the first page

    page = 1

    query_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!) {
    
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          files(first: $first){
            
            pageInfo{
                hasNextPage
                endCursor
              }
              
            nodes{
              additions
              deletions
              path
            }
          
          }
        }
      }
    }
    """
    variables_first_page = {
        "owner": owner,
        "name": name,
        "number": number,
        "first": first
    }
    hasNextPage, endCursor, changed_files = \
        fetch_changed_files_nodes(query=query_first_page, variables=variables_first_page, cost=cost)

    repository = owner + "/" + name

    for file in changed_files:
        additions = file["additions"]
        deletions = file["deletions"]
        path = file["path"]
        changed_file_obj = ChangedFile(additions=additions, deletions=deletions, path=path)
        num_updated = PullRequest.objects(repository=repository, number=number). \
            update_one(push__changedFiles=changed_file_obj)
        if num_updated != 1:
            raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                            format(str(number), repository))

    print("Page {}".format(str(page)))
    print("{} files are changed by pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(changed_files)), str(number), owner, name))

    # ----------------------------
    # Get the following pages
    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
        query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {
    
          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              files(first: $first, after: $after_cursor){
                
                pageInfo{
                  hasNextPage
                  endCursor
                }
              
                nodes{
                  additions
                  deletions
                  path
                }
              
              }
            }
          }
        }
        """
        variables_next_page = {
            "owner": owner,
            "name": name,
            "number": number,
            "first": first,
            "after_cursor": after_cursor
        }
        hasNextPage, after_cursor, associatedPRs = fetch_changed_files_nodes(query=query_next_page,
                                                                             variables=variables_next_page,
                                                                             cost=cost)
        for file in changed_files:
            additions = file["additions"]
            deletions = file["deletions"]
            path = file["path"]
            changed_file_obj = ChangedFile(additions=additions, deletions=deletions, path=path)
            num_updated = PullRequest.objects(repository=repository, number=number). \
                update_one(push__changedFiles=changed_file_obj)
            if num_updated != 1:
                raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                                format(str(number), repository))

        print("Page {}".format(str(page)))
        print("{} files are changed by pullRequest #{} in repo {}/{} -- MongoDB database".
              format(str(len(changed_files)), str(number), owner, name))

    print("------------------------------------------------------------")
    # ------------------------------


# Get the file nodes
def fetch_changed_files_nodes(query, variables, cost):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :param cost: Estimated cost of this call
    :return: hasNextPage, endCursor, nodes
    """
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequest"]["files"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequest"]["files"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["pullRequest"]["files"]["nodes"]

        return hasNextPage, endCursor, nodes


# Update Edit objects of a pullRequest
def update_pr_edits(owner, name, number):
    first = 50
    cost = 5

    # ------------------------------------
    # Get total count
    query_total_count = """
        query($owner: String!, $name: String!, $number: Int!) {

          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              userContentEdits(first:1){

                totalCount

              }
            }
          }
        }
        """
    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }
    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    total_count = result["data"]["repository"]["pullRequest"]["userContentEdits"]["totalCount"]
    print("There are in total {} edits for pullRequest #{} of repo {}/{}".
          format(str(total_count), str(number), owner, name))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Get the first page

    page = 1

    query_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!) {

      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          userContentEdits(first: $first){
          
            pageInfo{
              hasNextPage
              endCursor
            }

            nodes{
              editor{
                login
                __typename
              }
              createdAt
              editedAt
              updatedAt
              deletedAt
              deletedBy{
                login
                __typename
              }
              diff
            }

          }
        }
      }
    }
    """
    variables_first_page = {
        "owner": owner,
        "name": name,
        "number": number,
        "first": first
    }
    hasNextPage, endCursor, edits = \
        fetch_edit_nodes(query=query_first_page, variables=variables_first_page, cost=cost)

    repository = owner + "/" + name

    for edit in edits:
        editor = edit["editor"]
        if not editor:
            editor = ""
            editorType = ""
        else:
            editor = edit["editor"]["login"]
            editorType = edit["editor"]["__typename"]
        createdAt = edit["createdAt"]
        editedAt = edit["editedAt"]
        updatedAt = edit["updatedAt"]
        deletedAt = edit["deletedAt"]
        deletedBy = edit["deletedBy"]
        if not deletedBy:
            deletedBy = ""
            deletedByType = ""
        else:
            deletedBy = edit["deletedBy"]["login"]
            deletedByType = edit["deletedBy"]["__typename"]
        diff = edit["diff"]

        edit_obj = Edit(editor=editor, editorType=editorType, createdAt=createdAt, editedAt=editedAt,
                        updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy, deletedByType=deletedByType,
                        diff=diff)
        num_updated = PullRequest.objects(repository=repository, number=number). \
            update_one(push__edits=edit_obj)
        if num_updated != 1:
            raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                            format(str(number), repository))

    print("Page {}".format(str(page)))
    print("{} edits are added into pullRequest #{} of repo {}/{} -- MongoDB database".
          format(str(len(edits)), str(number), owner, name))

    # ----------------------------
    # Get the following pages
    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
            query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {

              repository(owner: $owner, name: $name){
                pullRequest(number: $number){
                  userContentEdits(first: $first, after: $after_cursor){
                  
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
        
                    nodes{
                      editor{
                        login
                        __typename
                      }
                      createdAt
                      editedAt
                      updatedAt
                      deletedAt
                      deletedBy{
                        login
                        __typename
                      }
                      diff
                    }

                  }
                }
              }
            }
            """
        variables_next_page = {
            "owner": owner,
            "name": name,
            "number": number,
            "first": first,
            "after_cursor": after_cursor
        }

        hasNextPage, after_cursor, edits = fetch_edit_nodes(query=query_next_page, variables=variables_next_page,
                                                            cost=cost)

        for edit in edits:
            editor = edit["editor"]
            if not editor:
                editor = ""
                editorType = ""
            else:
                editor = edit["editor"]["login"]
                editorType = edit["editor"]["__typename"]
            createdAt = edit["createdAt"]
            editedAt = edit["editedAt"]
            updatedAt = edit["updatedAt"]
            deletedAt = edit["deletedAt"]
            deletedBy = edit["deletedBy"]
            if not deletedBy:
                deletedBy = ""
                deletedByType = ""
            else:
                deletedBy = edit["deletedBy"]["login"]
                deletedByType = edit["deletedBy"]["__typename"]
            diff = edit["diff"]

            edit_obj = Edit(editor=editor, editorType=editorType, createdAt=createdAt, editedAt=editedAt,
                            updatedAt=updatedAt, deletedAt=deletedAt, deletedBy=deletedBy, deletedByType=deletedByType,
                            diff=diff)
            num_updated = PullRequest.objects(repository=repository, number=number). \
                update_one(push__edits=edit_obj)
            if num_updated != 1:
                raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                                format(str(number), repository))

        print("Page {}".format(str(page)))
        print("{} edits are added into pullRequest #{} of repo {}/{} -- MongoDB database".
              format(str(len(edits)), str(number), owner, name))

    print("------------------------------------------------------------")
    # ------------------------------


def fetch_edit_nodes(query, variables, cost):
    """
    Call GitHub GraphQL API to get data
    :param query: The GraphQL query
    :param variables: Variables included in the query
    :param cost: Estimated cost of this call
    :return: hasNextPage, endCursor, nodes
    """
    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        raise Exception("Repository not found")
    else:
        hasNextPage = result["data"]["repository"]["pullRequest"]["userContentEdits"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["pullRequest"]["userContentEdits"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["pullRequest"]["userContentEdits"]["nodes"]

        return hasNextPage, endCursor, nodes


# Update SuggestedReviewer objects of a pullRequest
def update_pr_suggested_reviewers(owner, name, number):

    cost = 1

    query = """
        query($owner: String!, $name: String!, $number: Int!) {

          repository(owner: $owner, name: $name){
            pullRequest(number: $number){
              suggestedReviewers{

                reviewer{
                  login
                  __typename
                }
                isAuthor
                isCommenter

              }
            }
          }
        }
        """
    variables = {
        "owner": owner,
        "name": name,
        "number": number
    }

    if get_remaining() > cost:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    suggested_reviewers = result["data"]["repository"]["pullRequest"]["suggestedReviewers"]

    if not suggested_reviewers:
        print("PullRequest # {} of repo {}/{} has no suggested reviewers.".format(str(number), owner, name))
        print("------------------------------------------------------------")
        return

    repository = owner + "/" + name
    for s_reviewer in suggested_reviewers:
        reviewer = s_reviewer["reviewer"]["login"]
        reviewerType = s_reviewer["reviewer"]["__typename"]
        isAuthor = s_reviewer["isAuthor"]
        isCommenter = s_reviewer["isCommenter"]

        s_reviewer_obj = SuggestedReviewer(reviewer=reviewer, reviewerType=reviewerType,
                                           isAuthor=isAuthor, isCommenter=isCommenter)
        num_updated = PullRequest.objects(repository=repository, number=number). \
            update_one(push__suggestedReviewers=s_reviewer_obj)
        if num_updated != 1:
            raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                            format(str(number), repository))

    print("{} suggested reviewers are added into pullRequest #{} of repo {}/{} -- MongoDB database".
          format(str(len(suggested_reviewers)), str(number), owner, name))
    print("------------------------------------------------------------")






