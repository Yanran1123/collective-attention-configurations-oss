"""
Step 5e (part 2). Final task interdependence for release cycles in the sample.
Discursive (issue-based) part: issue_interdependence_r4 as stored by step 5c.
Technical (file-based) part: each file is represented by the discursive tasks behind the PRs that changed it --
the issue(s) a PR came from, or the PR itself if it is not linked to an issue.
task_interdependence_r4 = 1/2 * (issue_interdependence_r4 + file_interdependence_r4).
"""

from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedFile
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest


def calculate_task_interdependence_r4(repository, cycleNumber):
    # # 1. Calculate epistemic interdependence;
    # # 1.1 Calculate the count of possible connections between epistemic tasks
    # # Get all epistemic tasks: issues whose num_prs_ledTo > 0, and pull requests whose num_issues_cameFrom = 0
    # num_invIssues = ReleaseCycleInvolvedIssue.objects(repository=repository, cycleNumber=cycleNumber).count()
    # num_invPRs = ReleaseCycleInvolvedPullRequest.objects(
    #     repository=repository, cycleNumber=cycleNumber, num_issues_cameFrom=0).count()
    # n = num_invIssues + num_invPRs
    # # Compute the possible connections
    # count_possibleConnection = n * (n - 1) / 2

    # # 1.2 Calculate the count of actual connections between epistemic tasks
    # # Get all epistemic tasks that have involved files
    # issues = ReleaseCycleInvolvedIssue.objects(
    #     repository=repository, cycleNumber=cycleNumber, num_prs_ledTo__gt=0  # prs led to is greater than 0
    # ).only('number', 'invPRs_ledTo')
    # prs = ReleaseCycleInvolvedPullRequest.objects(
    #     repository=repository, cycleNumber=cycleNumber, num_issues_cameFrom=0, num_files__gt=0  # invovled files > 0
    # ).only(
    #     'number', 'files'
    # )
    # # For each epistemic task, count the files it involves with
    # epistemicTasks = []  # each element is a set, which includes files involved in the epistemic task
    # for issue in issues:
    #     invFiles = set([])
    #     invPRs = issue['invPRs_ledTo']
    #     for number in invPRs:
    #         invPR = ReleaseCycleInvolvedPullRequest.objects(
    #             repository=repository, cycleNumber=cycleNumber, number=number
    #         ).only('files').first()
    #         if invPR is None:
    #             raise Exception("Debug!!!")
    #         else:
    #             files = [x[0] for x in invPR['files']]
    #             invFiles.update(files)  # set operator, add a list of elements to a set (keep only unique elements)
    #     if len(invFiles) != 0:
    #         epistemicTasks.append(invFiles)
    #     else:
    #         continue
    # for pr in prs:
    #     invFiles = set([x[0] for x in pr['files']])
    #     if len(invFiles) != 0:
    #         epistemicTasks.append(invFiles)
    #     else:
    #         continue
    # # Calculate the number of actual connections--jaccard index: shared/all files--exist between epistemic tasks
    # num_epistemicTasks = len(epistemicTasks)
    # if num_epistemicTasks < 1:
    #     issue_interdependence = 0  # All epistemic tasks have no involved files
    #     # raise Exception("Repo: {}, cycleNumber: {} has no epistemic tasks".format(repository, str(cycleNumber)))
    # elif num_epistemicTasks > 1:
    #     count_actualConnection = 0
    #     for i in range(0, num_epistemicTasks):
    #         i_files = epistemicTasks[i]
    #         for j in range(i + 1, num_epistemicTasks):
    #             j_files = epistemicTasks[j]
    #             # calculate Jaccard index of i and j
    #             jaccard_ij = len(i_files & j_files) / len(i_files | j_files)
    #             count_actualConnection += jaccard_ij
    #     # 1.3 Calculate the network density of pull requests
    #     issue_interdependence = count_actualConnection / count_possibleConnection
    # elif num_epistemicTasks == 1:
    #     issue_interdependence = 0
    # else:
    #     raise Exception("debug!!!")

    # Repair: Get issue interdependence
    release = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).only(
        'issue_interdependence_r4', 'inSample').first()
    if release['inSample'] == 0:
        return
    issue_interdependence = release['issue_interdependence_r4']

    # 2. Calculate file interdependence
    # 2.2 get all involved files
    files = ReleaseCycleInvolvedFile.objects(repository=repository, cycleNumber=cycleNumber).only(
        'path', 'prs'
    )
    num_files = len(files)
    if num_files < 1:
        return
    elif num_files > 1:
        # 2.2 Calculate the number of actual connections--Jaccard index: shared/all prs--exist between pull requests
        count_actualConnection = 0
        count_possibleConnection = 0
        for i in range(0, num_files):
            i_prNumbers = [x[0] for x in files[i]['prs']]

            # Get related epistemic tasks:
            # track back to its related issues; if no invIssues_cameFrom, than it is the original pr
            i_epistemicTasks = []
            for pr in i_prNumbers:
                pr_object = ReleaseCycleInvolvedPullRequest.objects(
                    repository=repository, cycleNumber=cycleNumber, number=int(pr)
                ).only('invIssues_cameFrom', 'num_issues_cameFrom').first()
                if pr_object['num_issues_cameFrom'] == 0:
                    epistemic = 'pr_' + pr
                    if epistemic not in i_epistemicTasks:
                        i_epistemicTasks.append(epistemic)
                else:
                    issues = pr_object['invIssues_cameFrom']
                    for issue in issues:
                        epistemic = 'issue_' + str(issue)
                        if epistemic not in i_epistemicTasks:
                            i_epistemicTasks.append(epistemic)

            for j in range(i + 1, num_files):
                count_possibleConnection += 1
                j_prNumbers = [x[0] for x in files[j]['prs']]

                # Get related epistemic tasks:
                # track back to its related issues; if no invIssues_cameFrom, than it is the original pr
                j_epistemicTasks = []
                for pr in j_prNumbers:
                    pr_object = ReleaseCycleInvolvedPullRequest.objects(
                        repository=repository, cycleNumber=cycleNumber, number=int(pr)
                    ).only('invIssues_cameFrom', 'num_issues_cameFrom').first()
                    if pr_object['num_issues_cameFrom'] == 0:
                        epistemic = 'pr_' + pr
                        if epistemic not in j_epistemicTasks:
                            j_epistemicTasks.append(epistemic)
                    else:
                        issues = pr_object['invIssues_cameFrom']
                        for issue in issues:
                            epistemic = 'issue_' + str(issue)
                            if epistemic not in j_epistemicTasks:
                                j_epistemicTasks.append(epistemic)

                # calculate Jaccard index of i and j
                jaccard_ij = len(set(i_epistemicTasks) & set(j_epistemicTasks)) / len(
                    set(i_epistemicTasks) | set(j_epistemicTasks)
                )
                count_actualConnection += jaccard_ij
        # 2.3 Calculate the network density of files
        file_interdependence = count_actualConnection / count_possibleConnection
    elif num_files == 1:
        file_interdependence = 0
    else:
        raise Exception("Debug!!!")

    # 3. Calculate task interdependence
    task_interdependence = 1 / 2 * (issue_interdependence + file_interdependence)

    # 4. Update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        issue_interdependence_r4=issue_interdependence, file_interdependence_r4=file_interdependence,
        task_interdependence_r4=task_interdependence
    )
    if num_updated != 1:
        raise Exception("Debug update_contingency_variables(case)!!")

    return
