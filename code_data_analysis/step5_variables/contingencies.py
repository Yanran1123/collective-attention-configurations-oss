"""
Step 5c. Contingencies: task interdependence (first pass) and project ownership (org).
calculate_task_interdependence_r4 here computes and stores issue_interdependence_r4 (the discursive part).
Its file-based part is recomputed at the issue level by step5_variables/task_interdependence_final.py
(step 5e), which writes the final task_interdependence_r4. Release-cycle length (days) is set in step 2.
"""

from classes.analysis.repoinfo import RepoDescription
from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedFile
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedIssue
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest


def update_invPRs_ledTo_r4(repository, cycleNumber):
    # 1. For each issue, find focal prs that it led to
    # invPRs_ledTo, num_prs_ledTo
    issues = ReleaseCycleInvolvedIssue.objects(repository=repository, cycleNumber=cycleNumber).only(
        "con_prs", "number")
    for issue in issues:
        # Find all connected prs
        con_prs = issue["con_prs"]
        issue_number = issue['number']
        # Identify connected prs that are involved in this focal release cycle
        invPRs_ledTo = []
        num_prs_ledTo = 0
        for pr in con_prs:
            count = ReleaseCycleInvolvedPullRequest.objects(
                repository=repository, cycleNumber=cycleNumber, number=pr
            ).count()
            if count == 1:
                invPRs_ledTo.append(pr)
                num_prs_ledTo += 1
            elif count == 0:
                continue
            else:
                raise Exception("Multiple records for repo: {}, cycleNumber: {}, pr #: {}".format(
                    repository, str(cycleNumber), str(pr)
                ))
        # Update the invPRs_ledTo, num_prs_ledTo of this issue
        num_updated = ReleaseCycleInvolvedIssue.objects(
            repository=repository, cycleNumber=cycleNumber, number=issue_number
        ).update(invPRs_ledTo=invPRs_ledTo, num_prs_ledTo=num_prs_ledTo)
        if num_updated != 1:
            raise Exception("Debug!")

    # 2. For each pr, find focal issues that it linked to
    # invIssues_cameFrom, num_issues_cameFrom
    prs = ReleaseCycleInvolvedPullRequest.objects(repository=repository, cycleNumber=cycleNumber).only(
        "con_issues", "number")
    for pr in prs:
        # Get all issues connected to this pr
        con_issues = pr['con_issues']
        pr_number = pr['number']
        # Identify connected issues that are involved in this focal release cycle
        invIssues_cameFrom = []
        num_issues_cameFrom = 0
        for issue in con_issues:
            count = ReleaseCycleInvolvedIssue.objects(
                repository=repository, cycleNumber=cycleNumber, number=issue
            ).count()
            if count == 1:
                invIssues_cameFrom.append(issue)
                num_issues_cameFrom += 1
            elif count == 0:
                continue
            else:
                raise Exception("Multiple records for repo: {}, cycleNumber: {}, issue #: {}".format(
                    repository, str(cycleNumber), str(issue)
                ))
        # Update the invIssues_cameFrom, num_issues_cameFrom
        num_updated = ReleaseCycleInvolvedPullRequest.objects(
            repository=repository, cycleNumber=cycleNumber, number=pr_number
        ).update(invIssues_cameFrom=invIssues_cameFrom, num_issues_cameFrom=num_issues_cameFrom)
        if num_updated != 1:
            raise Exception("Debug!")

    return


def calculate_task_interdependence_r4(repository, cycleNumber):
    # 1. Calculate epistemic interdependence;
    # 1.1 Calculate the count of possible connections between epistemic tasks
    # Get all epistemic tasks: issues whose num_prs_ledTo > 0, and pull requests whose num_issues_cameFrom = 0
    num_invIssues = ReleaseCycleInvolvedIssue.objects(repository=repository, cycleNumber=cycleNumber).count()
    num_invPRs = ReleaseCycleInvolvedPullRequest.objects(
        repository=repository, cycleNumber=cycleNumber, num_issues_cameFrom=0).count()
    n = num_invIssues + num_invPRs
    # Compute the possible connections
    count_possibleConnection = n * (n - 1) / 2

    # 1.2 Calculate the count of actual connections between epistemic tasks
    # Get all epistemic tasks that have involved files
    issues = ReleaseCycleInvolvedIssue.objects(
        repository=repository, cycleNumber=cycleNumber, num_prs_ledTo__gt=0  # prs led to is greater than 0
    ).only('number', 'invPRs_ledTo')
    prs = ReleaseCycleInvolvedPullRequest.objects(
        repository=repository, cycleNumber=cycleNumber, num_issues_cameFrom=0, num_files__gt=0  # invovled files > 0
    ).only(
        'number', 'files'
    )
    # For each epistemic task, count the files it involves with
    epistemicTasks = []  # each element is a set, which includes files involved in the epistemic task
    for issue in issues:
        invFiles = set([])
        invPRs = issue['invPRs_ledTo']
        for number in invPRs:
            invPR = ReleaseCycleInvolvedPullRequest.objects(
                repository=repository, cycleNumber=cycleNumber, number=number
            ).only('files').first()
            if invPR is None:
                raise Exception("Debug!!!")
            else:
                files = [x[0] for x in invPR['files']]
                invFiles.update(files)  # set operator, add a list of elements to a set (keep only unique elements)
        if len(invFiles) != 0:
            epistemicTasks.append(invFiles)
        else:
            continue
    for pr in prs:
        invFiles = set([x[0] for x in pr['files']])
        if len(invFiles) != 0:
            epistemicTasks.append(invFiles)
        else:
            continue
    # Calculate the number of actual connections--jaccard index: shared/all files--exist between epistemic tasks
    num_epistemicTasks = len(epistemicTasks)
    if num_epistemicTasks < 1:
        issue_interdependence = 0  # All epistemic tasks have no involved files
        # raise Exception("Repo: {}, cycleNumber: {} has no epistemic tasks".format(repository, str(cycleNumber)))
    elif num_epistemicTasks > 1:
        count_actualConnection = 0
        for i in range(0, num_epistemicTasks):
            i_files = epistemicTasks[i]
            for j in range(i + 1, num_epistemicTasks):
                j_files = epistemicTasks[j]
                # calculate Jaccard index of i and j
                jaccard_ij = len(i_files & j_files) / len(i_files | j_files)
                count_actualConnection += jaccard_ij
        # 1.3 Calculate the network density of pull requests
        issue_interdependence = count_actualConnection / count_possibleConnection
    elif num_epistemicTasks == 1:
        issue_interdependence = 0
    else:
        raise Exception("debug!!!")

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
            for j in range(i + 1, num_files):
                count_possibleConnection += 1
                j_prNumbers = [x[0] for x in files[j]['prs']]
                # calculate Jaccard index of i and j
                jaccard_ij = len(set(i_prNumbers) & set(j_prNumbers)) / len(set(i_prNumbers) | set(j_prNumbers))
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


def calculate_organizationOwnership(repository, cycleNumber):
    """
    Update whether the focal repository is owned by organizations
    :param repository: owner/name of the focal release cycle's repository
    :param cycleNumber: cycle number of the focal release cycle
    :return org: 1 if the focal repo is sponsored by organization; 0 if it is sponsored by user
    """
    repo = RepoDescription.objects(nameWithOwner=repository).only('ownerType').first()
    ownerType = repo['ownerType']
    if ownerType == 'Organization':
        org = 1
    elif ownerType == 'User':
        org = 0
    else:
        raise Exception("{} is unexpected type of repo owner".format(ownerType))

    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        org=org
    )
    if num_updated != 1:
        raise Exception("Debug!!!")

    return
