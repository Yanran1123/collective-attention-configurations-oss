"""
Step 5b. Collective attention attributes.
  calculate_primaryDivision / calculate_secondaryIntegration -> pdf, sif (technical, file level: main analysis);
      pdm, sim (technical, folder level: robustness test); also pdi, sii
  update_pdi_r4 / update_sii_r4 -> final pdi, sii (discursive; overwrite the values above)
Final paper variables (built in step6): dpi = 1 - pdi, dsi = sii, tpi = 1 - pdf, tsi = sif
(Robustness 3, folder level: tpi_f = 1 - pdm, tsi_f = sim).
"""

from classes.releasecycle.release_cycle import ReleaseCycle
from classes.releasecycle.release_cycle import ReleaseCycleInvolvedDeveloper
from step4_involved_elements.basics import calculate_average
from step4_involved_elements.basics import calculate_blau_index


def calculate_primaryDivision(repository, cycleNumber):
    # Return if there are less than 2 developers involved in the focal release cycle
    involvedDevelopers = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    if len(involvedDevelopers) <= 1:
        return

    # pdi: primary division by issues
    focal_dict = {}  # to store distribution of developers over ISSUEs (issue/pr) regarding developers' primary foci
    for d in involvedDevelopers:
        actorType_login = d['actorType_login']
        contribution_comment = d["contribution_comment"]
        if contribution_comment is None or contribution_comment == 0:
            continue
        primaryIssues = d["primaryIssues"]
        if len(primaryIssues) == 0:
            raise Exception("{} contributed comment but the primaryIssues is None in repo: {}, cycleNumber: {}".format(
                actorType_login, repository, str(cycleNumber)
            ))
        for issue in primaryIssues:  # divide the developer (1) by len(attentiveIssues)
            key = issue[0]
            if key in focal_dict:
                focal_dict[key] = focal_dict[key] + 1 / len(primaryIssues)
            else:
                focal_dict[key] = 1 / len(primaryIssues)
    pdi = calculate_blau_index(d=focal_dict)
    # pdf: primary division by files
    focal_dict = {}  # to store distribution of developers over FILEs regarding developers' primary foci
    for d in involvedDevelopers:
        contribution_code = d["contribution_code"]
        if contribution_code is None or contribution_code == 0:
            continue
        primaryFiles = d["primaryFiles"]
        if len(primaryFiles) == 0:
            raise Exception("{} contributed code but the primaryFiles is None in repo: {}, cycleNumber: {}".format(
                d['actorType_login'], repository, str(cycleNumber)
            ))
        for file in primaryFiles:  # divide the developer (1) by len(attentiveFiles)
            key = file[0]
            if key in focal_dict:
                focal_dict[key] = focal_dict[key] + 1 / len(primaryFiles)
            else:
                focal_dict[key] = 1 / len(primaryFiles)
    pdf = calculate_blau_index(d=focal_dict)
    # pdm: primary division by modules
    focal_dict = {}  # to store distribution of developers over MODULEs regarding developers' primary foci
    for d in involvedDevelopers:
        contribution_code = d["contribution_code"]
        if contribution_code is None or contribution_code == 0:
            continue
        primaryModules = d["primaryModules"]
        if len(primaryModules) == 0:
            raise Exception("{} contributed code but the primaryModules is None in repo: {}, cycleNumber: {}".format(
                d['actorType_login'], repository, str(cycleNumber)
            ))
        for module in primaryModules:  # divide the developer (1) by len(attentiveFiles)
            key = module[0]
            if key in focal_dict:
                focal_dict[key] = focal_dict[key] + 1 / len(primaryModules)
            else:
                focal_dict[key] = 1 / len(primaryModules)
    pdm = calculate_blau_index(d=focal_dict)

    # update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        pdi=pdi, pdf=pdf, pdm=pdm
    )
    if num_updated != 1:
        raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")

    return


def calculate_secondaryIntegration(repository, cycleNumber):
    # Return if there are less than 2 developers involved in the focal release cycle
    involvedDevelopers = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    if len(involvedDevelopers) <= 1:
        return

    # sii, sif, and sim (secondary integration by issues, files, modules) calculation
    # 0. initiate arrays that store proportions of secondary focus that overlaps others scope of attention
    pros_issue = []
    pros_file = []
    pros_module = []
    for d in involvedDevelopers:
        # 1. get the proportion of secondary focus that overlaps others' range of attention
        # in terms of issues, files and modules
        pro_issue, pro_file, pro_module = calculate_individual_secondaryFocus_overlapProportion(
            focalDeveloper=d, involvedDevelopers=involvedDevelopers)
        pros_issue.append(pro_issue)
        pros_file.append(pro_file)
        pros_module.append(pro_module)
        # update the proportion information
        actorType_login = d["actorType_login"]
        num_updated = ReleaseCycleInvolvedDeveloper.objects(
            repository=repository, cycleNumber=cycleNumber, actorType_login=actorType_login
        ).update(
            pro_secondaryIssueOverlap=pro_issue, pro_secondaryFileOverlap=pro_file,
            pro_scondaryModuleOverlap=pro_module
        )
        if num_updated != 1:
            raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")
    # 2. average the proportions
    sii = calculate_average(pros_issue)
    sif = calculate_average(pros_file)
    sim = calculate_average(pros_module)
    # update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        sii=sii, sif=sif, sim=sim
    )
    if num_updated != 1:
        raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")

    return


def calculate_individual_secondaryFocus_overlapProportion(focalDeveloper, involvedDevelopers):
    # 1. Get the focal developers' secondary focus
    secondaryIssues = [i[0] for i in focalDeveloper["secondaryIssues"]]
    secondaryFiles = [i[0] for i in focalDeveloper["secondaryFiles"]]
    secondaryModules = [i[0] for i in focalDeveloper["secondaryModules"]]
    # 2. Check how issues in the secondary focus overlaps others' scope of attention
    secondaryIssues_overlapped = []
    if len(secondaryIssues) == 0:
        # if no issues are in secondary focus, overlapping proportion is None;
        #   this focal developer is not taken into account for calculating attention augmentation by issues
        pro_issue = 0
    else:
        for d in involvedDevelopers:
            # should be other developers
            if d["actorType_login"] == focalDeveloper["actorType_login"]:
                continue
            # get all the issues that this other developer has worked on
            other_items = d["primaryIssues"]
            other_items.extend(d["secondaryIssues"])
            other_issues = [i[0] for i in other_items]
            # see whether those issues overlap any of the focal developer's secondary focus
            for issue in other_issues:
                if (issue in secondaryIssues) and (issue not in secondaryIssues_overlapped):
                    secondaryIssues_overlapped.append(issue)
        pro_issue = len(secondaryIssues_overlapped) / len(secondaryIssues)
    # 3. Check how files in the secondary focus overlaps others' scope of attention
    secondaryFiles_overlapped = []
    if len(secondaryFiles) == 0:
        # if no files are in secondary focus, overlapping proportion is None;
        #   this focal developer is not taken into account for calculating attention augmentation by files
        pro_file = 0
    else:
        for d in involvedDevelopers:
            # should be other developers
            if d["actorType_login"] == focalDeveloper["actorType_login"]:
                continue
            other_items = d["primaryFiles"]
            other_items.extend(d["secondaryFiles"])
            other_files = [i[0] for i in other_items]
            for file in other_files:
                if (file in secondaryFiles) and (file not in secondaryFiles_overlapped):
                    secondaryFiles_overlapped.append(file)
        pro_file = len(secondaryFiles_overlapped) / len(secondaryFiles)
    # 4. Check how modules in the secondary focus overlaps others' scope of attention
    secondaryModules_overlapped = []
    if len(secondaryModules) == 0:
        # if no modules are in secondary focus, overlapping proportion is None;
        #   this focal developer is not taken into account for calculating attention augmentation by modules
        pro_module = 0
    else:
        for d in involvedDevelopers:
            # should be other developers
            if d["actorType_login"] == focalDeveloper["actorType_login"]:
                continue
            other_items = d["primaryModules"]
            other_items.extend(d["secondaryModules"])
            other_modules = [i[0] for i in other_items]
            for module in other_modules:
                if (module in secondaryModules) and (module not in secondaryModules_overlapped):
                    secondaryModules_overlapped.append(module)
        pro_module = len(secondaryModules_overlapped) / len(secondaryModules)

    return pro_issue, pro_file, pro_module


# -----------------------------------------------
# Part 2 (of 2): Update the epistemic variables
def update_pdi_r4(repository, cycleNumber):
    # Return if there are less than 2 developers involved in the focal release cycle
    involvedDevelopers = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    if len(involvedDevelopers) <= 1:
        return

    # pdi: primary division by issues
    focal_dict = {}  # to store distribution of developers over ISSUEs (issue/pr) regarding developers' primary foci
    for d in involvedDevelopers:
        actorType_login = d['actorType_login']
        contribution_comment = d["contribution_comment"]
        if contribution_comment is None or contribution_comment == 0:
            continue
        primaryIssues = d["primaryIssues"]
        if len(primaryIssues) == 0:
            raise Exception("{} contributed comment but the primaryIssues is None in repo: {}, cycleNumber: {}".format(
                actorType_login, repository, str(cycleNumber)
            ))
        for issue in primaryIssues:  # divide the developer (1) by len(attentiveIssues)
            key = issue[0]
            if key in focal_dict:
                focal_dict[key] = focal_dict[key] + 1 / len(primaryIssues)
            else:
                focal_dict[key] = 1 / len(primaryIssues)
    pdi = calculate_blau_index(d=focal_dict)

    # update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        pdi=pdi
    )
    if num_updated != 1:
        raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")

    return


def update_sii_r4(repository, cycleNumber):
    # Return if there are less than 2 developers involved in the focal release cycle
    involvedDevelopers = ReleaseCycleInvolvedDeveloper.objects(repository=repository, cycleNumber=cycleNumber)
    if len(involvedDevelopers) <= 1:
        return

    # sii, sif, and sim (secondary integration by issues, files, modules) calculation
    # 0. initiate arrays that store proportions of secondary focus that overlaps others scope of attention
    pros_issue = []
    for d in involvedDevelopers:
        # 1. get the proportion of secondary focus that overlaps others' range of attention
        # in terms of issues, files and modules
        pro_issue = calculate_individual_secondaryFocus_overlapProportion_issueOnly(
            focalDeveloper=d, involvedDevelopers=involvedDevelopers)
        pros_issue.append(pro_issue)
        # update the proportion information
        actorType_login = d["actorType_login"]
        num_updated = ReleaseCycleInvolvedDeveloper.objects(
            repository=repository, cycleNumber=cycleNumber, actorType_login=actorType_login
        ).update(
            pro_secondaryIssueOverlap=pro_issue
        )
        if num_updated != 1:
            raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")
    # 2. average the proportions
    sii = calculate_average(pros_issue)
    # update the information in MongoDB
    num_updated = ReleaseCycle.objects(repository=repository, cycleNumber=cycleNumber).update(
        sii=sii
    )
    if num_updated != 1:
        raise Exception("Debug calculate_attentionPartition_andAugmentation(repository, cycleNumber)!!")

    return


def calculate_individual_secondaryFocus_overlapProportion_issueOnly(focalDeveloper, involvedDevelopers):
    # 1. Get the focal developers' secondary focus
    secondaryIssues = [i[0] for i in focalDeveloper["secondaryIssues"]]
    # 2. Check how issues in the secondary focus overlaps others' scope of attention
    secondaryIssues_overlapped = []
    if len(secondaryIssues) == 0:
        # if no issues are in secondary focus, overlapping proportion is None;
        #   this focal developer is not taken into account for calculating attention augmentation by issues
        pro_issue = 0
    else:
        for d in involvedDevelopers:
            # should be other developers
            if d["actorType_login"] == focalDeveloper["actorType_login"]:
                continue
            # get all the issues that this other developer has worked on
            other_items = d["primaryIssues"]
            other_items.extend(d["secondaryIssues"])
            other_issues = [i[0] for i in other_items]
            # see whether those issues overlap any of the focal developer's secondary focus
            for issue in other_issues:
                if (issue in secondaryIssues) and (issue not in secondaryIssues_overlapped):
                    secondaryIssues_overlapped.append(issue)
        pro_issue = len(secondaryIssues_overlapped) / len(secondaryIssues)

    return pro_issue
