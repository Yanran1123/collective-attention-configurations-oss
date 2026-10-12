"""
Step 4a. Technical work: scope the commits made in a release cycle, create the cycle's developers
(those who contributed code), involved files and PRs, and each developer's primary/secondary files.
"""

from classes.analysis.innovationoutput import InnovationOutput
from classes.analysis.innovativeaction import InnovativeAction
from classes.analysis.inputissue import InputIssue
from classes.github.issuecollection.pullrequest import PullRequest
from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedFile
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedModule
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedPullRequest
from itertools import groupby
from mongoengine.queryset.visitor import Q
from step4_involved_elements.basics import distribution_of_actions_over_developers
from step4_involved_elements.basics import distribution_of_actions_over_files
from step4_involved_elements.basics import distribution_of_actions_over_modules
from step4_involved_elements.basics import distribution_of_actions_over_prs
from step4_involved_elements.basics import get_primary_secondary_items_highest
from step4_involved_elements.basics import return_firstCommitTime
from step4_involved_elements.basics import return_open_prs_of_an_action


def scope_focal_commits(repository, cycleNumber, startTime, endTime, threshold):
    """
    :return: focal_commits, commits contributed to the open PRs for the repository during the release cycle by two
            types of accounts — User and Organization
    """
    # 1. Get all commits
    #   * associated with the focal repository's pull requests
    #   * committed within the focal release cycle
    #   * conducted by GitHub users (i.e., not bots or aliens)
    commits = InnovativeAction.objects().filter(
        (Q(prConnections__repository=repository)) &
        (Q(committedDate__gte=startTime) & Q(committedDate__lt=endTime)) &
        (Q(authorType="User") | Q(authorType="Organization"))
    ).only(
        "id", "authorLogin", "authorType", "additions", "deletions",
        "prConnections", "changedFiles"
    )
    # 2. Exclude commits that connect to PRs that has not been open in the focal release cycle of the repository
    # (e.g., legacy PRs from last release cycle); this means that the commit is not relevant to the focal release
    focal_commits0 = []
    for a in commits:
        prs = return_open_prs_of_an_action(action=a, repository=repository, startTime=startTime, endTime=endTime)
        if len(prs) != 0:
            focal_commits0.append(a)
    # 3. Exclude commits that are made by developers who contribute less than the threshold, e.g., 1 line of code
    # 3.1 calculate lines each developer changed in total; note that here we use focal_commits0
    user_dict, org_dict = distribution_of_actions_over_developers(focal_commits0)
    # 3.2 identify developers whose lines of change is less than the threshold
    user_removed = {key: user_dict[key] for key in user_dict if user_dict[key] < threshold}
    org_removed = {key: org_dict[key] for key in org_dict if org_dict[key] < threshold}
    # 3.3 keep the actions not taken by removed users or organizations
    focal_commits = []
    total_additions = 0
    total_deletions = 0
    for a in focal_commits0:
        if a["authorType"] == "User":
            if a["authorLogin"] not in user_removed:
                focal_commits.append(a)
                total_additions = total_additions + a['additions']
                total_deletions = total_deletions + a['deletions']
        elif a["authorType"] == "Organization":
            if a["authorLogin"] not in org_removed:
                focal_commits.append(a)
                total_additions = total_additions + a['additions']
                total_deletions = total_deletions + a['deletions']
        else:
            raise Exception("{} is unrecognized author type".format(a["authorType"]))
    total_commits = len(focal_commits)
    # 4. Calculate and update commit-related summaries of the release cycle
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        total_commits=total_commits, total_additions=total_additions, total_deletions=total_deletions
    )
    if num_updated != 1:
        raise Exception("Debug scope_focal_commits(case)")

    return focal_commits


def create_invDevelopers_invFiles_invModules_invPRsCode(focal_commits, repository, cycleNumber, startTime, endTime):
    """
    :return: MongoDB:
    created involved developers, files, modules, and PRs identified by
            repository, cycleNumber, and identifier (actorType_login, path, path, number)
    update the release cycle's num_developers, num_files, num_modules, num_prs
    """
    # 1. Identify developers involved in the focal commits of the release cycle
    focal_user_dict, focal_org_dict = distribution_of_actions_over_developers(focal_commits)
    num_developers = len(focal_user_dict) + len(focal_org_dict)
    for key in focal_user_dict:
        actorType = "User"
        login = key
        actorType_login = 'user_' + key
        invDev = ReleaseCycleInvolvedDeveloper(
            repository=repository, cycleNumber=cycleNumber, actorType=actorType, login=login,
            actorType_login=actorType_login)
        invDev.save()
    for key in focal_org_dict:
        actorType = "Organization"
        login = key
        actorType_login = 'org_' + key
        invDev = ReleaseCycleInvolvedDeveloper(
            repository=repository, cycleNumber=cycleNumber, actorType=actorType, login=login,
            actorType_login=actorType_login)
        invDev.save()
    # print("--> {} developers are identified and saved in MongoDB".format(str(num_developers)))
    # 2. Identify files involved in the focal commits of the release cycle
    file_dict = distribution_of_actions_over_files(focal_commits)
    num_files = len(file_dict)
    for path in file_dict:
        invFile = ReleaseCycleInvolvedFile(repository=repository, cycleNumber=cycleNumber, path=path)
        invFile.save()
    # print("--> {} files are identified and saved in MongoDB".format(str(num_files)))
    # 3. Identify modules involved in the focal commits of the release cycle
    module_dict = distribution_of_actions_over_modules(focal_commits)
    num_modules = len(module_dict)
    for path in module_dict:
        invModule = ReleaseCycleInvolvedModule(repository=repository, cycleNumber=cycleNumber, path=path)
        invModule.save()
    # print("--> {} modules are identified and saved in MongoDB".format(str(num_modules)))
    # 4. Identify pull requests involved in the focal commits of the release cycle
    pr_dict = distribution_of_actions_over_prs(
        actions=focal_commits, repository=repository, startTime=startTime, endTime=endTime)
    num_prs = len(pr_dict)
    for pr in pr_dict:
        number = int(pr)
        invPR = ReleaseCycleInvolvedPullRequest(repository=repository, cycleNumber=cycleNumber, number=number)
        invPR.save()
    # print("--> {} pull requests are identified and saved in MongoDB".format(str(num_prs)))
    # 5. Update the focal release cycle with the number of developers, files, modules, and prs
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        num_developers=num_developers, num_files=num_files, num_modules=num_modules, num_prs=num_prs
    )
    if num_updated != 1:
        raise Exception("Debug scope_focalInnovativeActions(case)")

    return


def update_focal_files(focal_commits, repository, cycleNumber, startTime, endTime):
    focal_files = ReleaseCycleInvolvedFile.objects(repository=repository, cycleNumber=cycleNumber).only('path')
    for file in focal_files:
        path = file['path']
        # 1. Calculate associated prs and developers of this issue
        # 1a. extract actions conducted to changes to this file
        focal_actions = []
        linesChanged = 0   # Total lines of change made for this file
        linesAdded = 0  # Total lines of change made for this file
        for action in focal_commits:
            # initiate additions and deletions for saving deletions for the focal file instead of all files
            a = InnovativeAction(
                id=action["id"], authorLogin=action["authorLogin"], authorType=action["authorType"],
                additions=0, deletions=0, prConnections=action['prConnections'], changedFiles=action['changedFiles']
            )
            files = a["changedFiles"]
            for f in files:
                if f["path"] == path:
                    a["additions"] = f["additions"]  # update the action's additions to that of the focal file
                    a["deletions"] = f["deletions"]  # update the action's deletions to that of to the focal file
                    focal_actions.append(a)
                    linesChanged = linesChanged + f["additions"] + f["deletions"]
                    linesAdded = linesAdded + f["additions"]
                    break
        # NOTE: Hereafter, the additions and deletions in each action is only for the focal file
        # 1b. find prs associated with this file
        pr_dict = distribution_of_actions_over_prs(
            actions=focal_actions, repository=repository, startTime=startTime, endTime=endTime)
        prs = []
        for key in pr_dict:
            prs.append([key, pr_dict[key]])
        # 1c. find developers changing this file
        developers = []
        user_dict, org_dict = distribution_of_actions_over_developers(actions=focal_actions)
        for key in user_dict:
            dev = "user_" + key
            developers.append([dev, user_dict[key]])
        for key in org_dict:
            dev = "org_" + key
            developers.append([dev, org_dict[key]])
        # 1d. count
        num_prs = len(prs)
        num_developers = len(developers)
        # 2. Update the above information for  this involvedFile in MongoDB
        num_updated = ReleaseCycleInvolvedFile.objects(
            repository=repository, cycleNumber=cycleNumber, path=path
        ).update(
            linesChanged=linesChanged, linesAdded=linesAdded,
            prs=prs, developers=developers, num_prs=num_prs, num_developers=num_developers
        )
        if num_updated != 1:
            raise Exception("Debug update_focal_files")

    return


def update_focal_prs_codePart(focal_commits, repository, cycleNumber, startTime, endTime):
    prs = ReleaseCycleInvolvedPullRequest.objects(repository=repository, cycleNumber=cycleNumber).only('number')
    for pr in prs:
        # 1. Obtain the basic information of each pull request for the focal release cycle
        number = pr['number']
        # 1a. Get url, author, authorType of the pull request
        pull = PullRequest.objects(repository=repository, number=number).only('url', 'author', 'authorType').first()
        url = pull['url']
        author = pull['author']
        authorType = pull['authorType']
        # 1b. Get corresponding inputIssue_label
        inputIssue = InputIssue.objects(repository=repository, number=number).only('label').first()
        inputIssue_label = inputIssue['label']
        # 1c. Calculate isResolved, mergedLines, and outputId of this issue
        mergedLines = None
        mergedAdditions = None
        changedFilesCount = None
        outputId = None
        output_type = None
        noChangeInfo_GitHubRestriction = False
        outputs = InnovationOutput.objects(
            repository=repository, number=number, createdAt__gte=startTime, createdAt__lt=endTime
        ).only("id", "additions", "deletions", "changedFilesCount", "label")
        if len(outputs) > 1:
            raise Exception(
                "Pull request #{} in repo {} is merged more than one time in the release cycle:".format(pr, repository)
            )
        elif len(outputs) == 1:
            isResolved = True
            if not outputs[0]["additions"] and not outputs[0]["deletions"]:  # No info because we cannot compare
                # two commits whose changes exceed GitHub restrictions
                mergedLines = None
                mergedAdditions = None
                noChangeInfo_GitHubRestriction = True
            else:
                mergedLines = outputs[0]["additions"] + outputs[0]["deletions"]
                mergedAdditions = outputs[0]["additions"]
            changedFilesCount = outputs[0]["changedFilesCount"]
            outputId = outputs[0]["id"]
            output_type = outputs[0]["label"]
        else:  # len(ouputs) < 1
            isResolved = False
        # 2. Calculate files, modules, and developers associated with this pr
        # 2a. extract actions conducted to resolve this pr
        focal_actions = []
        linesChanged = 0
        linesAdded = 0
        for action in focal_commits:
            prs = action["prConnections"]
            for p in prs:
                if p["repository"] == repository and int(p["number"]) == number:
                    focal_actions.append(action)
                    linesChanged += action['additions'] + action['deletions']
                    linesAdded += action['additions']
                    break
        # 2b. find files relating to this pr
        focal_dict = distribution_of_actions_over_files(actions=focal_actions)
        files = []
        for key in focal_dict:
            files.append([key, focal_dict[key]])
        # 2c. find modules relating to this pr
        focal_dict = distribution_of_actions_over_modules(actions=focal_actions)
        modules = []
        for key in focal_dict:
            modules.append([key, focal_dict[key]])
        # 2d. find developers addressing this pr
        developers_code = []
        user_dict, org_dict = distribution_of_actions_over_developers(actions=focal_actions)
        for key in user_dict:
            dev = "user_" + key
            developers_code.append([dev, user_dict[key]])
        for key in org_dict:
            dev = "org_" + key
            developers_code.append([dev, org_dict[key]])
        # 2e. count
        num_files = len(files)
        num_modules = len(modules)
        num_developers_code = len(developers_code)
        # 3. Update the information of this involvedPR in MongoDB
        num_updated = ReleaseCycleInvolvedPullRequest.objects(
            repository=repository, cycleNumber=cycleNumber, number=number
        ).update(
            url=url, author=author, authorType=authorType,
            isResolved=isResolved, noChangeInfo_GitHubRestriction=noChangeInfo_GitHubRestriction,
            mergedLines=mergedLines, mergedAdditions=mergedAdditions,
            changedFilesCount=changedFilesCount, outputId=outputId, output_type=output_type,
            inputIssue_label=inputIssue_label,
            linesChanged=linesChanged, linesAdded=linesAdded,
            files=files, modules=modules, developers_code=developers_code,
            num_files=num_files, num_modules=num_modules, num_developers_code=num_developers_code
        )
        if num_updated != 1:
            raise Exception("Debug update_focal_prs_codePart")

    return


def update_focal_developers_commits(focal_commits, repository, cycleNumber, startTime, endTime):
    sorted_commits = sorted(focal_commits, key=lambda x: (x.authorType, x.authorLogin))
    groupedCommits_byDev = [list(group) for _, group in groupby(
        sorted_commits, key=lambda x: (x.authorType, x.authorLogin)
    )]
    for commits in groupedCommits_byDev:
        # 0. Identifier of the developer
        actorType = commits[0]['authorType']
        login = commits[0]['authorLogin']
        # 1. Calculate tenure of the developer
        firstCommitTime = return_firstCommitTime(login=login, actorType=actorType, repository=repository)
        # calculate tenure
        if firstCommitTime >= startTime:
            tenure = 0
        else:
            delta = startTime - firstCommitTime
            tenure = delta.days

        # 2. Information about file interactions: added, removed, modified, renamed
        addedFiles = []  # Files added by the focal developer (may be removed, modified, or renamed after added)
        removedFiles = []  # Files removed by the developer (may be added, modified, or renamed before removed)
        modifiedFiles = []  # Files modified by the developer (may be added, removed, or renamed before or after)
        renamedFiles = []  # Files renamed by the developer
        contribution_code = 0
        contribution_codeAdded = 0
        for c in commits:
            contribution_code += c['additions'] + c['deletions']
            contribution_codeAdded += c['additions']
            changedFiles = c['changedFiles']
            for file in changedFiles:
                path = file['path']
                status = file['status']
                if status == 'added':
                    if path not in addedFiles:
                        addedFiles.append(path)
                elif status == 'removed':
                    if path not in removedFiles:
                        removedFiles.append(path)
                elif status == 'modified':
                    if path not in modifiedFiles:
                        modifiedFiles.append(path)
                elif status == 'renamed':
                    if path not in renamedFiles:
                        renamedFiles.append(path)
                else:
                    raise Exception("{} is an unexpected status of changedFiles".format(status))
        # 3. Distribution of code changes over files, sorted in descending order by # of changes for the file
        file_dict_unsorted = distribution_of_actions_over_files(commits)
        file_dict = dict(sorted(file_dict_unsorted.items(), reverse=True))  # sorted by the path
        num_files = len(file_dict)
        pro_addedFiles = len(addedFiles) / num_files
        pro_removedFiles = len(removedFiles) / num_files
        primaryFiles, secondaryFiles, primaryRate_file = get_primary_secondary_items_highest(
            focal_dict=file_dict
        )
        num_primaryFiles = len(primaryFiles)
        num_secondaryFiles = len(secondaryFiles)
        # 4. Distribution of code changes over modules, sorted in descending order by # of changes for the module
        module_dict_unsorted = distribution_of_actions_over_modules(commits)
        module_dict = dict(sorted(module_dict_unsorted.items(), reverse=True))  # sorted by the path
        num_modules = len(module_dict)
        primaryModules, secondaryModules, primaryRate_module = get_primary_secondary_items_highest(
            focal_dict=module_dict
        )
        num_primaryModules = len(primaryModules)
        num_secondaryModules = len(secondaryModules)

        # 5. Orientation to bugs and to features
        num_code_bug = 0
        num_code_feature = 0
        pr_dict = distribution_of_actions_over_prs(commits, repository=repository, startTime=startTime, endTime=endTime)
        for key in pr_dict:
            number = int(key)
            lines = pr_dict[key]
            invPR = ReleaseCycleInvolvedPullRequest.objects(
                repository=repository, cycleNumber=cycleNumber, number=number
            ).only('inputIssue_label').first()
            if invPR is not None:
                inputIssue_label = invPR['inputIssue_label']
                if inputIssue_label == 'BugReport':
                    num_code_bug += lines
                elif inputIssue_label == 'FeatureRequest':
                    num_code_feature += lines
                elif inputIssue_label == 'Documentation' or inputIssue_label == 'Question':
                    continue
                else:
                    raise Exception('{} is an unexpected InputIssue label'.format(inputIssue_label))
            else:
                raise Exception("Issue #{} does not exist in repo:{}, cycleNumber: {}".format(
                    str(number), repository, str(cycleNumber)
                ))
        orient_bugs_code = num_code_bug / contribution_code
        orient_features_code = num_code_feature / contribution_code

        # 6. Update the information
        num_updated = ReleaseCycleInvolvedDeveloper.objects(
            repository=repository, cycleNumber=cycleNumber, actorType=actorType, login=login
        ).update(
            firstCommitTime=firstCommitTime, tenure=tenure,
            contribution_code=contribution_code, contribution_codeAdded=contribution_codeAdded,
            pro_addedFiles=pro_addedFiles, pro_removedFiles=pro_removedFiles,
            addedFiles=addedFiles, removedFiles=removedFiles, modifiedFiles=modifiedFiles, renamedFiles=renamedFiles,
            num_files=num_files, num_modules=num_modules, primaryFiles=primaryFiles, primaryModules=primaryModules,
            num_primaryFiles=num_primaryFiles, num_primaryModules=num_primaryModules,
            secondaryFiles=secondaryFiles, secondaryModules=secondaryModules,
            num_secondaryFiles=num_secondaryFiles, num_secondaryModules=num_secondaryModules,
            primaryRate_file=primaryRate_file, primaryRate_module=primaryRate_module,
            orient_bugs_code=orient_bugs_code, orient_features_code=orient_features_code
        )
        if num_updated != 1:
            raise Exception("{} involved developers in repo: {}, cycle: {}, actorType: {}, login: {}".format(
                str(num_updated), repository, str(cycleNumber), actorType, login
            ))

    return
