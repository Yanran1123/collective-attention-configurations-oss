import time

from Classes.repocollection.language import Language
from Classes.repocollection.license import License
from Classes.repocollection.release import Release
from Classes.repocollection.repo import Repo
from Classes.repocollection.topic import Topic
from setup.graphql import run_query_variable


# Estimated maximum total resource consumption for getting complete information for a repository:
# 13.36 =
# (2 for viewerInfo and for repo + 1111 for releases + 111 for topics + 111 for languages + 1 for license) / 100
def add_repo(owner, name):
    query = """
    query RepoInfo ($owner:String!, $name:String!){
      rateLimit{
        cost
        remaining
        resetAt
      }
      repository(owner: $owner, name: $name) {
        owner{
          login
          __typename
        }
        name
        nameWithOwner
        createdAt
        description
        homepageUrl
       
        defaultBranchRef{
          name
        }
        primaryLanguage{
          name
        }
        diskUsage
        databaseId
       
        
        forkCount
        stargazers{
          totalCount
        }
        watchers{
          totalCount
        }
        
        isArchived
        isLocked
        isMirror
        isTemplate
        mergeCommitAllowed
        
        releases(first:1){
          totalCount
        }
        
        repositoryTopics(first:1){
          totalCount
        }
        languages(first:1){
          totalCount
          totalSize
        }
    
        licenseInfo{
          key
          name
          nickname
          pseudoLicense
          spdxId
          url
        }
        
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }

    result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        print("No repository {}/{}".format(owner, name))
        return
    else:
        # owner = result["data"]["repository"]["owner"]["login"]
        ownerType = result["data"]["repository"]["owner"]["__typename"]
        # name = result["data"]["repository"]["name"]
        nameWithOwner = result["data"]["repository"]["nameWithOwner"]
        createdAt = result["data"]["repository"]["createdAt"]
        description = result["data"]["repository"]["description"]
        homepageUrl = result["data"]["repository"]["homepageUrl"]

        if not result["data"]["repository"]["defaultBranchRef"]:
            defaultBranch = ""
        else:
            defaultBranch = result["data"]["repository"]["defaultBranchRef"]["name"]
        if not result["data"]["repository"]["primaryLanguage"]:
            primaryLanguage = ""
        else:
            primaryLanguage = result["data"]["repository"]["primaryLanguage"]["name"]
        diskUsage = result["data"]["repository"]["diskUsage"]
        databaseId = result["data"]["repository"]["databaseId"]

        forkCount = result["data"]["repository"]["forkCount"]
        stargazerCount = result["data"]["repository"]["stargazers"]["totalCount"]
        watcherCount = result["data"]["repository"]["watchers"]["totalCount"]

        isArchived = result["data"]["repository"]["isArchived"]
        isLocked = result["data"]["repository"]["isLocked"]
        isMirror = result["data"]["repository"]["isMirror"]
        isTemplate = result["data"]["repository"]["isTemplate"]
        mergeCommitAllowed = result["data"]["repository"]["mergeCommitAllowed"]

        releaseCount = result["data"]["repository"]["releases"]["totalCount"]

        topicCount = result["data"]["repository"]["repositoryTopics"]["totalCount"]

        languageCount = result["data"]["repository"]["languages"]["totalCount"]
        languageSize = result["data"]["repository"]["languages"]["totalSize"]

        # Insert all information except the lists of releases, topics, and languages
        repo = Repo(owner=owner, ownerType=ownerType, name=name, nameWithOwner=nameWithOwner,
                    createdAt=createdAt, description=description,
                    homepageUrl=homepageUrl, defaultBranch=defaultBranch, primaryLanguage=primaryLanguage,
                    diskUsage=diskUsage, databaseId=databaseId,
                    forkCount=forkCount, stargazerCount=stargazerCount, watcherCount=watcherCount,
                    isArchived=isArchived, isLocked=isLocked, isMirror=isMirror, isTemplate=isTemplate,
                    mergeCommitAllowed=mergeCommitAllowed,
                    releaseCount=releaseCount,
                    topicCount=topicCount,
                    languageCount=languageCount, languageSize=languageSize)
        if not result["data"]["repository"]["licenseInfo"]:
            print("Repo {}/{} has no license".format(owner, name))
        else:
            # license info
            key = result["data"]["repository"]["licenseInfo"]["key"]
            license_name = result["data"]["repository"]["licenseInfo"]["name"]
            nickname = result["data"]["repository"]["licenseInfo"]["nickname"]
            pseudoLicense = result["data"]["repository"]["licenseInfo"]["pseudoLicense"]
            spdxID = result["data"]["repository"]["licenseInfo"]["spdxId"]
            url = result["data"]["repository"]["licenseInfo"]["url"]
            license = License(key=key, name=license_name, nickname=nickname,
                              pseudoLicense=pseudoLicense, spdxID=spdxID, url=url)
            repo.license = license
        repo.save()


def update_release(owner, name):
    # todo need to also update releaseCount
    query = """
    query RepoInfo ($owner:String!, $name:String!){
      rateLimit{
        cost
        remaining
      }
      repository(owner: $owner, name: $name) {
        releases(orderBy:{direction:DESC, field:CREATED_AT}, first:100){
          totalCount
          pageInfo{
            endCursor
            hasNextPage
          }
          nodes{
            tagName
            author{
              login
            }
            tag{
              target{
                oid
              }
            }
            name
            description
            url
            
            createdAt
            publishedAt
            updatedAt
    
            isDraft
            isPrerelease
            
          }
        }
        
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }
    result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        print("No repository {}/{}".format(owner, name))
        return
    else:
        release_count = result["data"]["repository"]["releases"]["totalCount"]
        remaining = result["data"]["rateLimit"]["remaining"]
        if release_count == 0:
            return
        else:
            if release_count > 1000:
                print("Repository {}/{} has more than 1000 releases")

            hasNextPage = result["data"]["repository"]["releases"]["pageInfo"]["hasNextPage"]
            after_cursor = result["data"]["repository"]["releases"]["pageInfo"]["endCursor"]

            # Append the 100 release info into releases
            for r in result["data"]["repository"]["releases"]["nodes"]:
                tagName = r["tagName"]
                if not r["author"]:
                    print("Repo: {}/{}, Release tagName: {} has no author".format(owner, name, tagName))
                    author = ""
                else:
                    author = r["author"]["login"]
                if not r["tag"]:
                    print("Repo: {}/{}, Release tagName: {} has no tagCommit".format(owner, name, tagName))
                    tagCommit = ""
                else:
                    tagCommit = r["tag"]["target"]["oid"]
                release_name = r["name"]
                description = r["description"]
                url = r["url"]

                createdAt = r["createdAt"]
                publishedAt = r["publishedAt"]
                updatedAt = r["updatedAt"]

                isDraft = r["isDraft"]
                isPrerelease = r["isPrerelease"]

                release = Release(tagName=tagName, author=author, tagCommit=tagCommit, name=release_name,
                                  description=description, url=url,
                                  createdAt=createdAt, publishedAt=publishedAt, updatedAt=updatedAt,
                                  isDraft=isDraft, isPrerelease=isPrerelease)
                num_updated = Repo.objects(owner=owner, name=name).update_one(add_to_set__releases=release)
                if num_updated != 1:
                    raise Exception("No repository {}/{}".format(owner, name))
                    return
                # releases.append(release)

            while hasNextPage:
                next_info = fetch_release_next_page(owner, name, after_cursor)
                remaining = next_info[0]
                after_cursor = next_info[1]
                hasNextPage = next_info[2]


# Each page: Cost 1
# Embedded function of "update_release"
def fetch_release_next_page(owner, name, after_cursor):
    next_info = []
    query = """
    query RepoInfo ($owner:String!, $name:String!, $after_cursor:String!){
      rateLimit{
        cost
        remaining
      }
      repository(owner: $owner, name: $name) {
        releases(orderBy:{direction:DESC, field:CREATED_AT}, first:100, after:$after_cursor){
          totalCount
          pageInfo{
            endCursor
            hasNextPage
          }
          nodes{
            tagName
            author{
              login
            }
            tag{
              target{
                oid
              }
            }
            name
            description
            url
            
            createdAt
            publishedAt
            updatedAt
    
            isDraft
            isPrerelease
            
          }
        }
        
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name,
        "after_cursor": after_cursor
    }

    result = run_query_variable(query, variables)

    # next_info[0] is the remaining of rateLimit
    next_info.append(result["data"]["rateLimit"]["remaining"])
    # next_info[1] is the endCursor
    # next_info[2] is the hasNextPage
    next_info.append(result["data"]["repository"]["releases"]["pageInfo"]["endCursor"])
    next_info.append(result["data"]["repository"]["releases"]["pageInfo"]["hasNextPage"])

    for r in result["data"]["repository"]["releases"]["nodes"]:
        tagName = r["tagName"]
        if not r["author"]:
            print("Repo: {}/{}, Release tagName: {} has no author".format(owner, name, tagName))
            author = ""
        else:
            author = r["author"]["login"]
        if not r["tag"]:
            print("Repo: {}/{}, Release tagName: {} has no tagCommit".format(owner, name, tagName))
            tagCommit = ""
        else:
            tagCommit = r["tag"]["target"]["oid"]
        release_name = r["name"]
        description = r["description"]
        url = r["url"]

        createdAt = r["createdAt"]
        publishedAt = r["publishedAt"]
        updatedAt = r["updatedAt"]

        isDraft = r["isDraft"]
        isPrerelease = r["isPrerelease"]

        release = Release(tagName=tagName, author=author, tagCommit=tagCommit, name=release_name,
                          description=description, url=url,
                          createdAt=createdAt, publishedAt=publishedAt, updatedAt=updatedAt,
                          isDraft=isDraft, isPrerelease=isPrerelease)
        num_updated = Repo.objects(owner=owner, name=name).update_one(add_to_set__releases=release)
        if num_updated != 1:
            raise Exception("No repository {}/{}".format(owner, name))
            return

    return list(next_info)


# resource cost is 1
def update_topic(owner, name):
    # todo need to also update topicCount
    query = """
    query RepoInfo ($owner:String!, $name:String!){
      rateLimit{
        cost
        remaining
        resetAt
      }
      repository(owner: $owner, name: $name) {
        
        repositoryTopics(first:100){
          totalCount
          nodes{
            topic{
              name
            }
          }
        }
        
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }
    result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        print("No repository {}/{}".format(owner, name))
        return
    else:
        if result["data"]["repository"]["repositoryTopics"]["totalCount"] == 0:
            return
        else:
            for r in result["data"]["repository"]["repositoryTopics"]["nodes"]:
                topic = Topic(name=r["topic"]["name"])
                num_updated = Repo.objects(owner=owner, name=name).update_one(add_to_set__topics=topic)
                if num_updated != 1:
                    raise Exception("No repository {}/{}".format(owner, name))


# resource cost is 1
def update_language(owner, name):
    # todo need to also update languageCount
    query = """
    query RepoInfo ($owner:String!, $name:String!){
      rateLimit{
        cost
        remaining
        resetAt
      }
      repository(owner: $owner, name: $name) {
        
        languages(first:100){
          totalCount
          totalSize
          nodes{
            name
          }
        }
        
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }
    result = run_query_variable(query, variables)

    if not result["data"]["repository"]:
        print("No repository {}/{}".format(owner, name))
        return
    else:
        if result["data"]["repository"]["languages"]["totalCount"] == 0:
            return
        else:
            for r in result["data"]["repository"]["languages"]["nodes"]:
                language = Language(name=r["name"])
                num_updated = Repo.objects(owner=owner, name=name).update_one(add_to_set__languages=language)
                if num_updated != 1:
                    raise Exception("No repository {}/{}".format(owner, name))


def repo_found(owner, name):
    query = """
    query($owner: String!, $name: String!) { 
      repository(owner: $owner, name: $name) { 
        name
      }
    }
    """
    variables = {
        "owner": owner,
        "name": name
    }
    results = run_query_variable(query, variables)

    if not results["data"]["repository"]:
        return False
    else:
        return True


# todo program for the content of the function
def update_fsw(owner, name):
    print("to update info about forkCount, stargazerCount, watcherCount")
