import time

# Basic information about all issues of an repository
from Classes.issuecollection.edit import Edit
from Classes.issuecollection.issue import Issue
from setup.graphql import run_query_variable, get_remaining, sleep_in_seconds, get_reset


def add_issues(owner, name):

    first = 50  # Iterms per page; if too many requests per page, I will have 502 error

    query = """
    query ($owner: String!, $name: String!, $first: Int!){
      repository(owner: $owner, name: $name) {
        issues(first: $first, orderBy: {direction: ASC, field:CREATED_AT}){
        
          totalCount
          
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
            
            closed
            closedAt
            
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
            
            timelineItems{
              totalCount
            }
             
          }
          
        }
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name,
        "first": first
    }
    if get_remaining() > 5:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        print("No repository {}/{}".format(owner, name))
        return
    else:
        total_count = result["data"]["repository"]["issues"]["totalCount"]
        hasNextPage = result["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["issues"]["pageInfo"]["endCursor"]

        print("------------------------------------------------------------")
        print("There are in total {} issues for {}/{}".format(str(total_count), owner, name))

        # Data fields of issue
        for issue in result["data"]["repository"]["issues"]["nodes"]:
            save_one_issue_node(issue)

        page = 1
        print("  Page {}:".format(page))
        print("  {} issues are added".format(str(len(result["data"]["repository"]["issues"]["nodes"]))))

        after_cursor = endCursor
        while hasNextPage:
            page = page + 1
            print("  Page {}:".format(page))
            hasNextPage, after_cursor = fetch_issue_next_page(owner, name, after_cursor, first)

        print("------------------------------------------------------------")


# Fetch issue based on cursor
def fetch_issue_next_page(owner, name, after_cursor, first):
    query = """
        query ($owner: String!, $name: String!, $after_cursor: String!, $first: Int!){
          repository(owner: $owner, name: $name) {
            issues(first: $first, after: $after_cursor, orderBy: {direction: ASC, field:CREATED_AT}){

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

                closed
                closedAt

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

                timelineItems{
                  totalCount
                }

              }

            }
          }
        }
        """
    variables = {
        "owner": owner,
        "name": name,
        "after_cursor": after_cursor,
        "first": first
    }
    if get_remaining() > 5:
        result = run_query_variable(query, variables)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query, variables)

    hasNextPage = result["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"]
    endCursor = result["data"]["repository"]["issues"]["pageInfo"]["endCursor"]

    # Data fields of issue
    for issue in result["data"]["repository"]["issues"]["nodes"]:
        save_one_issue_node(issue)

    print("  {} issues are added".format(str(len(result["data"]["repository"]["issues"]["nodes"]))))

    return hasNextPage, endCursor


# From issue node in GitHub API to issue object
def save_one_issue_node(issue):
    repository = issue["repository"]["nameWithOwner"]
    number = issue["number"]
    # Some issues have no author, e.g., issue #62, tensorflow/tensorflow
    author = issue["author"]
    if not author:
        author = ""
        authorType = ""
    else:
        author = issue["author"]["login"]
        authorType = issue["author"]["__typename"]
    authorAssociation = issue["authorAssociation"]

    createdAt = issue["createdAt"]
    createdViaEmail = issue["createdViaEmail"]
    publishedAt = issue["publishedAt"]
    updatedAt = issue["updatedAt"]

    databaseId = issue["databaseId"]
    resourcePath = issue["resourcePath"]
    url = issue["url"]

    closed = issue["closed"]
    closedAt = issue["closedAt"]

    title = issue["title"]
    body = issue["body"]
    bodyHTML = issue["bodyHTML"]
    bodyText = issue["bodyText"]

    editor = issue["editor"]
    if not editor:
        editor = ""
        editorType = ""
    else:
        editor = issue["editor"]["login"]
        editorType = issue["editor"]["__typename"]
    includesCreatedEdit = issue["includesCreatedEdit"]
    lastEditedAt = issue["lastEditedAt"]
    editCount = issue["userContentEdits"]["totalCount"]

    issue_obj = Issue(repository=repository, number=number, author=author, authorType=authorType,
                      authorAssociation=authorAssociation, createdAt=createdAt, createdViaEmail=createdViaEmail,
                      publishedAt=publishedAt, updatedAt=updatedAt,
                      databaseId=databaseId, resourcePath=resourcePath, url=url,
                      closed=closed, closedAt=closedAt,
                      title=title, body=body, bodyHTML=bodyHTML, bodyText=bodyText,
                      editor=editor, editorType=editorType, includesCreatedEdit=includesCreatedEdit,
                      lastEditedAt=lastEditedAt, editCount=editCount)

    issue_obj.save()


# Update Edit objects of an issue
def update_issue_edits(owner, name, number):
    first = 50

    # ------------------------------------
    # Get total count
    query_total_count = """
        query($owner: String!, $name: String!, $number: Int!) {

          repository(owner: $owner, name: $name){
            issue(number: $number){
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

    total_count = result["data"]["repository"]["issue"]["userContentEdits"]["totalCount"]
    print("------------------------------------------------------------")
    print("There are in total {} edits for issue #{} of repo {}/{}".
          format(str(total_count), str(number), owner, name))

    if total_count == 0:
        return

    # ------------------------------------
    # Get the first page

    page = 1

    query_first_page = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!) {

      repository(owner: $owner, name: $name){
        issue(number: $number){
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
        fetch_edit_nodes(query=query_first_page, variables=variables_first_page, cost=1)

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
        num_updated = Issue.objects(repository=repository, number=number). \
            update_one(push__edits=edit_obj)
        if num_updated != 1:
            raise Exception("No issue with number {} in repo {} -- MongoDB database".
                            format(str(number), repository))

    print("Page {}".format(str(page)))
    print("{} edits are added into issue #{} of repo {}/{} -- MongoDB database".
          format(str(len(edits)), str(number), owner, name))

    # ----------------------------
    # Get the following pages
    after_cursor = endCursor
    while hasNextPage:
        page = page + 1

        query_next_page = """
            query($owner: String!, $name: String!, $number: Int!, $first: Int!, $after_cursor: String!) {

              repository(owner: $owner, name: $name){
                issue(number: $number){
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
                                                            cost=1)

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
            num_updated = Issue.objects(repository=repository, number=number). \
                update_one(push__edits=edit_obj)
            if num_updated != 1:
                raise Exception("No pull request with number {} in repo {} -- MongoDB database".
                                format(str(number), repository))

        print("Page {}".format(str(page)))
        print("{} edits are added into issue #{} of repo {}/{} -- MongoDB database".
              format(str(len(edits)), str(number), owner, name))
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
        hasNextPage = result["data"]["repository"]["issue"]["userContentEdits"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["issue"]["userContentEdits"]["pageInfo"]["endCursor"]
        nodes = result["data"]["repository"]["issue"]["userContentEdits"]["nodes"]

        return hasNextPage, endCursor, nodes



