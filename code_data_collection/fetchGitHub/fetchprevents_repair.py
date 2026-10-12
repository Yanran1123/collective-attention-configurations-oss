import time

from Classes.event.basehead.headrefdeleted import HeadRefDeleted

from Classes.issuecollection.pullrequest import PullRequest
from Classes.issuecollection.timelineitem import TimelineItem

from fetchGitHub.fetchissueevents import get_issue_or_pr_id

from fetchGitHub.fetchprevents import fetch_event_nodes, save_assigned_event, save_unassigned_event, save_issue_comment, \
    save_comment_deleted_event, save_connected_event, save_disconnected_event, save_cross_referenced_event, \
    save_referenced_event, save_transferred_event, save_labeled_event, save_unlabeled_event, save_mentioned_event, \
    save_milestoned_event, save_demilestoned_event, save_closed_event, save_reopened_event, save_locked_event, \
    save_unlocked_event, save_pinned_event, save_unpinned_event, save_marked_as_duplicate_event, \
    save_unmarked_as_duplicate_event, save_added_to_project_event, save_removed_from_project_event, \
    save_moved_columns_in_project_event, save_converted_note_to_issue_event, save_subscribed_event, \
    save_unsubscribed_event, save_renamed_title_event, save_user_blocked_event, save_automatic_base_change_failed_event, \
    save_automatic_base_change_succeeded_event, save_baseRef_changed_event, save_baseRef_force_pushed_event, \
    save_headRef_force_pushed_event, save_headRef_restored_event, save_pr_commit, save_pr_commit_comment_thread, \
    save_convert_to_draft_event, save_deployed_event, save_deployment_environment_changed_event, save_merged_event, \
    save_pr_review, save_pr_review_thread, save_ready_for_review_event, save_review_dismissed_event, \
    save_review_requested_event, save_review_request_removed_event

from setup.graphql import get_remaining, run_query_variable, sleep_in_seconds, get_reset

first = 30
cost = 30


def update_pr_timeline_items_repair(owner, name, number):
    """
    Update the timelineItems of a pullRequest
    :param owner: Owner of the associated repository
    :param name: Name of the associated repository
    :param number: Number of the pullRequest
    :return: No return; the event objects are saved and the timeline of the pullRequest is updated in MongoDB
    """
    print("Working on pullRequest #{} of repo {}/{}".format(str(number), owner, name))

    variables_total_count = {
        "owner": owner,
        "name": name,
        "number": number
    }

    fetch_with_skip_repair(variables_total_count=variables_total_count)


def fetch_with_skip_repair(variables_total_count):
    events = []

    # Get nodes of timelineItems associated with the specific issue
    query_total_count = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          timelineItems(first: 1){
            totalCount
          }
        }
      }
    }
    """

    query_skip_repair = """
    query($owner: String!, $name: String!, $number: Int!, $first: Int!, $skip: Int!) {
      rateLimit{
        cost
        remaining
      }
      repository(owner: $owner, name: $name){
        pullRequest(number: $number){
          timelineItems(first: $first, skip: $skip){
            totalCount
            pageInfo{
              hasNextPage
              endCursor
            }
            edges{
              cursor
              node{

                ... on AssignedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt

                  assignee{
                    ... on User{
                      login
                      __typename
                    }
                    ... on Bot{
                      login
                      __typename
                    }
                    ... on Organization{
                      login
                      __typename
                    }
                    ... on Mannequin{
                      login
                      __typename
                    }
                  }

                  assignable{
                    __typename
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnassignedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt

                  assignee{
                    ... on User{
                      login
                      __typename
                    }
                    ... on Bot{
                      login
                      __typename
                    }
                    ... on Organization{
                      login
                      __typename
                    }
                    ... on Mannequin{
                      login
                      __typename
                    }
                  }

                  assignable{
                    __typename
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  } 
                }

                ... on IssueComment{
                  __typename
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
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  isMinimized
                  minimizedReason
                  body
                  bodyHTML
                  bodyText
                  editor{
                    login
                    __typename
                  }
                  includesCreatedEdit
                  lastEditedAt
                  userContentEdits(first:50){
                    totalCount
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
                  reactionGroups{
                    content
                    createdAt
                    users{
                      totalCount
                    }
                  }
                }

                ... on CommentDeletedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on ConnectedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  isCrossRepository
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on DisconnectedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  isCrossRepository
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on CrossReferencedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  referencedAt
                  resourcePath
                  url
                  isCrossRepository
                  willCloseTarget
                  source{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  target{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ReferencedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  commit{
                    oid
                  }
                  commitRepository{
                    nameWithOwner
                  }
                  isCrossRepository
                  isDirectReference
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on TransferredEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  fromRepository{
                    nameWithOwner
                  }
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on LabeledEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  label{
                    name
                    createdAt
                    color
                    isDefault
                    description
                    repository{
                      nameWithOwner
                    }
                    resourcePath
                    url
                    updatedAt
                  }
                  labelable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnlabeledEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  label{
                    name
                    createdAt
                    color
                    isDefault
                    description
                    repository{
                      nameWithOwner
                    }
                    resourcePath
                    url
                    updatedAt
                  }
                  labelable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MentionedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on DemilestonedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  milestoneTitle
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MilestonedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  milestoneTitle
                  subject{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ClosedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  closable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                  closer{
                    __typename
                    ... on Commit{
                      repository{
                        nameWithOwner
                      }
                      oid
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on ReopenedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  closable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on LockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  lockReason
                  lockable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnlockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  lockable{
                    __typename
                    ... on Issue{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on MarkedAsDuplicateEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                }

                ... on UnmarkedAsDuplicateEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                }

                ... on PinnedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on UnpinnedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  issue{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on AddedToProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on RemovedFromProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on ConvertedNoteToIssueEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on MovedColumnsInProjectEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on SubscribedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  subscribable{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UnsubscribedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  subscribable{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on RenamedTitleEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  currentTitle
                  previousTitle
                  subject{
                    ... on Issue{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                    ... on PullRequest{
                      __typename
                      repository{
                        nameWithOwner
                      }
                      number
                    }
                  }
                }

                ... on UserBlockedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  blockDuration
                  subject{
                    login
                    __typename
                  }

                }

                ... on AutomaticBaseChangeFailedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  newBase
                  oldBase
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on AutomaticBaseChangeSucceededEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  newBase
                  oldBase
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on BaseRefChangedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                }

                ... on BaseRefForcePushedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  ref{
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  beforeCommit{
                    oid
                  }
                  afterCommit{
                    oid
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }

                }

                ... on HeadRefDeletedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  headRefName
                  
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on HeadRefForcePushedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  ref{
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  beforeCommit{
                    oid
                  }
                  afterCommit{
                    oid
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on HeadRefRestoredEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestCommit{
                  __typename
                  commit{
                    repository{
                      nameWithOwner
                    }
                    oid
                  }
                  pullRequest{
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestCommitCommentThread{
                  __typename
                  commit{
                    oid
                  }
                  path
                  position
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  comments(first: 1){
                    totalCount
                  }
                }

                ... on ConvertToDraftEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on DeployedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                  ref{
                    __typename
                    name
                    prefix
                    target{
                      oid
                    }
                  }
                  deployment{
                    creator{
                      login
                      __typename
                    }
                    createdAt
                    updatedAt
                    commitOid
                    task
                    databaseId
                    description
                    payload
                    environment
                    originalEnvironment
                    state
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on DeploymentEnvironmentChangedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  deploymentStatus{
                    state
                    deployment{
                      creator{
                      login
                      __typename
                      }
                      createdAt
                      updatedAt
                      commitOid
                      task
                      databaseId
                      description
                      payload
                      environment
                      originalEnvironment
                      state
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on MergedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  commit{
                    oid
                  }
                  resourcePath
                  url
                  mergeRefName
                  mergeRef{
                    __typename
                    prefix
                    target{
                      oid
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestReview{
                  __typename
                  author{
                    login
                    __typename
                  }
                  authorAssociation
                  state
                  commit{
                    oid
                  }
                  createdAt
                  createdViaEmail
                  publishedAt
                  updatedAt
                  submittedAt
                  databaseId
                  resourcePath
                  url
                  body
                  bodyHTML
                  bodyText
                  editor{
                    login
                    __typename
                  }
                  includesCreatedEdit
                  lastEditedAt
                  userContentEdits(first: 50){
                    totalCount
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
                  reactionGroups{
                    content
                    createdAt
                    users{
                      totalCount
                    }
                  }
                  onBehalfOf(first:50){
                    totalCount
                    pageInfo{
                      hasNextPage
                      endCursor
                    }
                    nodes{
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                  }
                  comments(first:1){
                    totalCount
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on PullRequestReviewThread{
                  __typename
                  isResolved
                  line
                  startLine
                  originalLine
                  originalStartLine
                  resolvedBy{
                    login
                    __typename
                  }
                  diffSide
                  startDiffSide
                  comments(first: 1){
                    totalCount
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReadyForReviewEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  resourcePath
                  url
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReviewDismissedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  databaseId
                  resourcePath
                  url
                  dismissalMessage
                  dismissalMessageHTML
                  previousReviewState
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                  pullRequestCommit{
                    commit{
                      oid
                    }
                  }
                  review{
                    author{
                      login
                    }
                    createdAt
                    body
                  }
                }

                ... on ReviewRequestedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  requestedReviewer{
                    __typename
                    ... on Mannequin{
                      login
                    }
                    ... on Team{
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                    ... on User{
                      login
                    }
                  }
                  pullRequest{
                    __typename
                    repository{
                      nameWithOwner
                    }
                    number
                  }
                }

                ... on ReviewRequestRemovedEvent{
                  __typename
                  actor{
                    login
                    __typename
                  }
                  createdAt
                  requestedReviewer{
                    ... on Mannequin{
                      login
                      __typename
                    }
                    ... on Team{
                      __typename
                      organization{
                        login
                      }
                      slug
                      combinedSlug
                      createdAt
                      updatedAt
                      databaseId
                      avatarUrl
                      resourcePath
                      url
                      name
                    }
                    ... on User{
                      login
                      __typename
                    }
                  }
                  pullRequest{
                    __typename
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
      }
    }
    """

    # ------------------------------------
    # Get the total count

    if get_remaining() > 1:
        result = run_query_variable(query_total_count, variables_total_count)
    else:
        sleep = sleep_in_seconds(get_reset())
        print("Need to sleep about {} minutes to reset the 5000 scores".format(str(sleep / 60)))
        time.sleep(sleep)
        print("Restart! :-)")
        result = run_query_variable(query_total_count, variables_total_count)

    # An exception: Cannot find repo "quantum9Innovation/Neural-Network-Frameworks" anymore
    if not result["data"]["repository"]:
        raise Exception("Cannot find repo {}/{} anymore!".
                        format(variables_total_count["owner"], variables_total_count["name"]))

    total_count = result["data"]["repository"]["pullRequest"]["timelineItems"]["totalCount"]
    print("There are in total {} timeline items.".format(str(total_count)))

    if total_count == 0:
        print("------------------------------------------------------------")
        return

    # ------------------------------------
    # Traverse the list by skip function

    skip = 0

    variables_skip = {
        "owner": variables_total_count["owner"],
        "name": variables_total_count["name"],
        "number": variables_total_count["number"],
        "first": first,
        "skip": skip
    }

    while skip < total_count:
        hasNextPage, endCursor, edges = fetch_event_nodes(query=query_skip_repair, variables=variables_skip)

        # # If the query has an error, I set the edges as None;
        # # Information about the errors is saved in the files at path_message and path_var
        if not edges:
            raise Exception("The something-went-wrong error for this pull request is not repaired!")

        events.extend(edges)
        skip = skip + first
        variables_skip["skip"] = skip

    # Note that there is no PullRequestRevisionMarker
    count = {
        "AssignedEvent": 0,
        "UnassignedEvent": 0,
        "IssueComment": 0,
        "CommentDeletedEvent": 0,
        "ConnectedEvent": 0,
        "DisconnectedEvent": 0,
        "CrossReferencedEvent": 0,
        "ReferencedEvent": 0,
        "TransferredEvent": 0,
        "LabeledEvent": 0,
        "UnlabeledEvent": 0,
        "MentionedEvent": 0,
        "MilestonedEvent": 0,
        "DemilestonedEvent": 0,
        "ClosedEvent": 0,
        "ReopenedEvent": 0,
        "LockedEvent": 0,
        "UnlockedEvent": 0,
        "PinnedEvent": 0,
        "UnpinnedEvent": 0,
        "MarkedAsDuplicateEvent": 0,
        "UnmarkedAsDuplicateEvent": 0,
        "AddedToProjectEvent": 0,
        "RemovedFromProjectEvent": 0,
        "MovedColumnsInProjectEvent": 0,
        "ConvertedNoteToIssueEvent": 0,
        "SubscribedEvent": 0,
        "UnsubscribedEvent": 0,
        "RenamedTitleEvent": 0,
        "UserBlockedEvent": 0,
        # From here, PR only events
        "AutomaticBaseChangeFailedEvent": 0,
        "AutomaticBaseChangeSucceededEvent": 0,
        "BaseRefChangedEvent": 0,
        "BaseRefForcePushedEvent": 0,
        "HeadRefDeletedEvent": 0,
        "HeadRefForcePushedEvent": 0,
        "HeadRefRestoredEvent": 0,
        "PullRequestCommit": 0,
        "PullRequestCommitCommentThread": 0,
        "ConvertToDraftEvent": 0,
        "DeployedEvent": 0,
        "DeploymentEnvironmentChangedEvent": 0,
        "MergedEvent": 0,
        "PullRequestReview": 0,
        "PullRequestReviewThread": 0,
        "ReadyForReviewEvent": 0,
        "ReviewDismissedEvent": 0,
        "ReviewRequestedEvent": 0,
        "ReviewRequestRemovedEvent": 0
    }

    # We use skip instead of beforeEventCursor to reach a specific timelineItem in the list
    # because skip seems much more stable.
    skip = 0

    repository = variables_total_count["owner"] + "/" + variables_total_count["name"]
    number = variables_total_count["number"]

    for i in range(0, len(events)):
        eventType = events[i]["node"]["__typename"]
        event = events[i]["node"]
        # Save a document of the event in MongoDB
        if eventType == "AssignedEvent":
            timelineItem = save_assigned_event(event)
        elif eventType == "UnassignedEvent":
            timelineItem = save_unassigned_event(event)
        elif eventType == "IssueComment":
            timelineItem = save_issue_comment(event)
        elif eventType == "CommentDeletedEvent":
            timelineItem = save_comment_deleted_event(event, variables_total_count)
        elif eventType == "ConnectedEvent":
            timelineItem = save_connected_event(event)
        elif eventType == "DisconnectedEvent":
            timelineItem = save_disconnected_event(event)
        elif eventType == "CrossReferencedEvent":
            timelineItem = save_cross_referenced_event(event)
        elif eventType == "ReferencedEvent":
            timelineItem = save_referenced_event(event)
        elif eventType == "TransferredEvent":
            timelineItem = save_transferred_event(event)
        elif eventType == "LabeledEvent":
            timelineItem = save_labeled_event(event)
        elif eventType == "UnlabeledEvent":
            timelineItem = save_unlabeled_event(event)
        elif eventType == "MentionedEvent":
            timelineItem = save_mentioned_event(event, variables_total_count)
        elif eventType == "MilestonedEvent":
            timelineItem = save_milestoned_event(event)
        elif eventType == "DemilestonedEvent":
            timelineItem = save_demilestoned_event(event)
        elif eventType == "ClosedEvent":
            timelineItem = save_closed_event(event)
        elif eventType == "ReopenedEvent":
            timelineItem = save_reopened_event(event)
        elif eventType == "LockedEvent":
            timelineItem = save_locked_event(event)
        elif eventType == "UnlockedEvent":
            timelineItem = save_unlocked_event(event)
        elif eventType == "PinnedEvent":
            timelineItem = save_pinned_event(event)
        elif eventType == "UnpinnedEvent":
            timelineItem = save_unpinned_event(event)
        elif eventType == "MarkedAsDuplicateEvent":
            timelineItem = save_marked_as_duplicate_event(event, variables_total_count)
        elif eventType == "UnmarkedAsDuplicateEvent":
            timelineItem = save_unmarked_as_duplicate_event(event, variables_total_count)
        elif eventType == "AddedToProjectEvent":
            timelineItem = save_added_to_project_event(event, variables_total_count)
        elif eventType == "RemovedFromProjectEvent":
            timelineItem = save_removed_from_project_event(event, variables_total_count)
        elif eventType == "MovedColumnsInProjectEvent":
            timelineItem = save_moved_columns_in_project_event(event, variables_total_count)
        elif eventType == "ConvertedNoteToIssueEvent":
            timelineItem = save_converted_note_to_issue_event(event, variables_total_count)
        elif eventType == "SubscribedEvent":
            timelineItem = save_subscribed_event(event)
        elif eventType == "UnsubscribedEvent":
            timelineItem = save_unsubscribed_event(event)
        elif eventType == "RenamedTitleEvent":
            timelineItem = save_renamed_title_event(event)
        elif eventType == "UserBlockedEvent":
            timelineItem = save_user_blocked_event(event, variables_total_count)
        # From here: PR-only events
        elif eventType == "AutomaticBaseChangeFailedEvent":
            timelineItem = save_automatic_base_change_failed_event(event)
        elif eventType == "AutomaticBaseChangeSucceededEvent":
            timelineItem = save_automatic_base_change_succeeded_event(event)
        elif eventType == "BaseRefChangedEvent":
            timelineItem = save_baseRef_changed_event(event, variables_total_count)
        elif eventType == "BaseRefForcePushedEvent":
            timelineItem = save_baseRef_force_pushed_event(event)
        elif eventType == "HeadRefDeletedEvent":
            timelineItem = save_headRef_deleted_event_repair(event)
        elif eventType == "HeadRefForcePushedEvent":
            timelineItem = save_headRef_force_pushed_event(event)
        elif eventType == "HeadRefRestoredEvent":
            timelineItem = save_headRef_restored_event(event)
        elif eventType == "PullRequestCommit":
            timelineItem = save_pr_commit(event)
        elif eventType == "PullRequestCommitCommentThread":
            timelineItem = save_pr_commit_comment_thread(event, variables_total_count, skip)
        elif eventType == "ConvertToDraftEvent":
            timelineItem = save_convert_to_draft_event(event)
        elif eventType == "DeployedEvent":
            timelineItem = save_deployed_event(event)
        elif eventType == "DeploymentEnvironmentChangedEvent":
            timelineItem = save_deployment_environment_changed_event(event)
        elif eventType == "MergedEvent":
            timelineItem = save_merged_event(event)
        elif eventType == "PullRequestReview":
            timelineItem = save_pr_review(event, variables_total_count, skip)
        elif eventType == "PullRequestReviewThread":
            timelineItem = save_pr_review_thread(event, variables_total_count, skip)
        elif eventType == "ReadyForReviewEvent":
            timelineItem = save_ready_for_review_event(event)
        elif eventType == "ReviewDismissedEvent":
            timelineItem = save_review_dismissed_event(event)
        elif eventType == "ReviewRequestedEvent":
            timelineItem = save_review_requested_event(event)
        elif eventType == "ReviewRequestRemovedEvent":
            timelineItem = save_review_request_removed_event(event)
        else:
            raise Exception("{} is an unexpected event type of pullRequest timeline items".format(eventType))

        # Save the timelineItem in the focal pullRequest
        num_updated = PullRequest.objects(repository=repository, number=number).update(push__timeline=timelineItem)
        if num_updated != 1:
            raise Exception(
                "No pullRequest with number {} in repo {} -- MongoDB database".format(str(number), repository))

        count[eventType] = count[eventType] + 1
        skip = skip + 1

    print("------------------------------------------------------------")
    print("{} events are added to the timeline of pullRequest #{} in repo {}/{} -- MongoDB database".
          format(str(len(events)), variables_total_count["number"],
                 variables_total_count["owner"], variables_total_count["name"]))
    for key in count:
        if count[key] != 0:
            print("  --> {}: {} added".format(key, count[key]))
    print("------------------------------------------------------------")
    # ------------------------------


def save_headRef_deleted_event_repair(node):
    """
    Save the event object/document and save the timeline items of the event
    :param node: Node of the event
    :return: timelineItem to be pushed to the focal pullRequest; save the event in MongoDB as a document
    """
    actor = node["actor"]
    if not actor:
        actor = None
        actorType = None
    else:
        actor = node["actor"]["login"]
        actorType = node["actor"]["__typename"]
    createdAt = node["createdAt"]

    headRefName = node["headRefName"]

    # headRef = node["headRef"]
    # if not headRef:
    #     headRefPrefix = None
    #     headRefOid = None
    # else:
    #     headRefPrefix = node["headRef"]["prefix"]
    #     if node["headRef"]["target"]:
    #         headRefOid = node["headRef"]["target"]["oid"]
    #     else:
    #         headRefOid = None

    subjectType = node["pullRequest"]["__typename"]
    repository = node["pullRequest"]["repository"]["nameWithOwner"]
    number = node["pullRequest"]["number"]
    subjectId = get_issue_or_pr_id(type_issue_or_pr=subjectType, repository=repository, number=number)

    # event = HeadRefDeleted(actor=actor, actorType=actorType, createdAt=createdAt,
    #                        headRefName=headRefName, headRefPrefix=headRefPrefix, headRefOid=headRefOid,
    #                        subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event = HeadRefDeleted(actor=actor, actorType=actorType, createdAt=createdAt,
                           headRefName=headRefName,
                           subjectType=subjectType, repository=repository, number=number, subjectId=subjectId)
    event.save()

    # Save the corresponding timeline item
    timelineItem = TimelineItem(actor=actor, actorType=actorType, createdAt=createdAt,
                                eventType=node["__typename"], eventId=event["id"])

    return timelineItem
