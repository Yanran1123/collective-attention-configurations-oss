"""
Builds the final variables described in Section 5 (Method) of the paper.

Run from this folder (code_data_analysis/). Steps must run in order; each one reads what the previous
steps saved in MongoDB (see setup/mongo_setup.py). Set RUN_STEPS to the step(s) you want to run.

    1  Data preparation: analysis collections and default-branch commits (needs a GitHub token)
    2  Release cycles; number of changed files and lines of each merge (needs internet access)
    3  Classification of outputs (merged PRs) and of issues/PRs
    4  Per release cycle: developers, involved issues/PRs/files, primary and secondary foci
    5  Per release cycle: outcomes, collective attention attributes, contingencies; then (5e) sample flags and
       final task interdependence
    6  Final sample, final variables, calibration, and CSV files for fsQCA 3.0
    -  (outside Python) fsQCA 3.0 truth tables and solutions; necessity analyses in R
    7  Merge the truth tables exported by fsQCA 3.0 into the paper's tables

Final variables (Section 5.3):
    speed, novelty, quality                     OSS development performance (step 5)
    dpi = 1 - pdi                               discursive primary integration (step 5, built in step 6)
    tpi = 1 - pdf                               technical primary integration, file level (step 5, built in step 6)
    dsi = sii                                   discursive secondary integration (step 5, built in step 6)
    tsi = sif                                   technical secondary integration, file level (step 5, built in step 6)
    task_interdependence, org, days             contingencies (steps 5, 5e, and 2; task interdependence is stored in
                                                MongoDB as task_interdependence_r4)
Robustness 3 (folder level): tpi_f = 1 - pdm, tsi_f = sim (see step6_sample_calibration/fsqca_sample.py).
"""
import datetime

from classes.releasecycle.release_cycle import ReleaseCycle
from setup import mongo_setup

from step1_data_preparation.prepare_actions import repo_info_db2, action_info_db2, \
    update_innovative_action_parentCount
from step1_data_preparation.default_branch import identify_most_recent_defaultBranch_commit, \
    repair_find_most_recent_defaultBranchCommit, mark_all_defaultBranch_commits
from step3_classification.outputs import construct_innovationOutput_dataset, \
    update_innovationOutput_category_removeEnhancement, classify_innovationOutputs
from step3_classification.input_issues import construct_inputIssue_dataset, \
    update_inputIssue_category_removeEnhancement, classify_inputIssues
from step2_release_cycles.release_cycles import slice_repo_byReleaseCycle, get_basic_releaseCycleInfo
from step2_release_cycles.merged_changes import calculate_novelty_mergedEvents, fetch_changedInfo_of_mergedEvents
from step4_involved_elements.code_part import scope_focal_commits, \
    create_invDevelopers_invFiles_invModules_invPRsCode, update_focal_files, update_focal_prs_codePart, \
    update_focal_developers_commits
from step4_involved_elements.comment_part import scope_focal_comments_r4, create_invIssues_invPRsComment_r4, \
    update_focal_issues_r4, update_focal_prs_commentPart_r4, update_focal_developers_comments_r4
from step5_variables.outcomes import calculate_performance_outcomes
from step5_variables.collective_attention import calculate_primaryDivision, calculate_secondaryIntegration, \
    update_pdi_r4, update_sii_r4
from step5_variables.contingencies import update_invPRs_ledTo_r4, calculate_task_interdependence_r4, \
    calculate_organizationOwnership
from step5_variables.sample_counts import update_numDev_with_PrimarySecondary
from step5_variables.in_sample import update_inSample_r4
from step5_variables.task_interdependence_final import \
    calculate_task_interdependence_r4 as calculate_task_interdependence_r4_final
from step6_sample_calibration.fsqca_sample import construct_sample_r4
from step7_results.merge_truthTables import paper_tables_r4, merge_main_robustness_truthTables_r4

RUN_STEPS = []  # e.g., [1], [2], ..., or [1, 2, 3, 4, 5, 6]; step 7 after the fsQCA 3.0 analyses

threshold = 1  # Humans whose contribution of code changes is less than 1 are not focal developers
#               (Robustness 5: threshold = 15)


def main():
    start_time = datetime.datetime.now()
    mongo_setup.global_init()

    if 1 in RUN_STEPS:
        step1_data_preparation()
    if 2 in RUN_STEPS:
        step2_release_cycles()
    if 3 in RUN_STEPS:
        step3_classification()
    if 4 in RUN_STEPS or 5 in RUN_STEPS:
        # Steps 4 and 5 run release cycle by release cycle
        num_cycles = ReleaseCycle.objects().count()  # 18,630 release cycles
        for i in range(0, num_cycles):
            case = ReleaseCycle.objects[i:i + 1].only(
                "repository", "cycleNumber", "startTime", "endTime", "days").first()
            print("Working on cases[{}]: repo: {}, cycleNumber: {}".format(
                str(i), case["repository"], str(case["cycleNumber"])))
            if 4 in RUN_STEPS:
                step4_involved_elements(case)
            if 5 in RUN_STEPS:
                step5_variables(case)
    if 5 in RUN_STEPS:
        # Step 5e runs after all release cycles are done, because sample membership needs speed and the
        # developer counts of every cycle
        step5e_final_task_interdependence()
    if 6 in RUN_STEPS:
        step6_sample_calibration()
    if 7 in RUN_STEPS:
        step7_merge_truthTables()

    delta = datetime.datetime.now() - start_time
    print("Finished in {} minutes".format(str(int(delta.total_seconds() / 60))))


def step1_data_preparation():
    # 1a. Analysis collections built from the raw GitHub data
    repo_info_db2()  # repos_info_2539
    action_info_db2()  # supportive_actions (discursive actions) and innovative_actions (commits)
    update_innovative_action_parentCount()
    # 1b. Default-branch commits (GitHub GraphQL and REST APIs)
    identify_most_recent_defaultBranch_commit()
    repair_find_most_recent_defaultBranchCommit()  # manual repair of one repository (see its docstring)
    mark_all_defaultBranch_commits()


def step3_classification():
    # 3a. Outputs (merged pull requests): NewFeature, BugFixing, or Documentation
    construct_innovationOutput_dataset()
    update_innovationOutput_category_removeEnhancement()
    classify_innovationOutputs()
    # 3b. Issues and pull requests: BugReport, FeatureRequest, Documentation, or Question
    construct_inputIssue_dataset()
    update_inputIssue_category_removeEnhancement()
    classify_inputIssues()


def step2_release_cycles():
    # 2a. Release cycles
    slice_repo_byReleaseCycle()  # repoByReleaseCycle_2539 in db1_small_analysis
    get_basic_releaseCycleInfo()  # copy into ReleaseCycle (collection sample0 in db2_paper_r4)
    # 2b. Number of changed files, lines added, and lines deleted of each merge (GitHub compare pages);
    # used by step 3a and, through the outputs, by hasNoChangeInfo (step 5a)
    calculate_novelty_mergedEvents(repoFrame="RepoByReleaseCycle")  # merges within each release cycle
    fetch_changedInfo_of_mergedEvents()  # catch-up pass over all merges still missing this information


def step4_involved_elements(case):
    repository = case["repository"]
    cycleNumber = case["cycleNumber"]
    startTime = case["startTime"]
    endTime = case["endTime"]

    # 4a. Technical work (code changes): developers, files, PRs, and primary/secondary files
    focal_commits = scope_focal_commits(
        repository=repository, cycleNumber=cycleNumber, startTime=startTime, endTime=endTime, threshold=threshold)
    if focal_commits:
        create_invDevelopers_invFiles_invModules_invPRsCode(
            focal_commits=focal_commits, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)
        update_focal_files(
            focal_commits=focal_commits, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)
        update_focal_prs_codePart(
            focal_commits=focal_commits, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)
        update_focal_developers_commits(
            focal_commits=focal_commits, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)

    # 4b. Discursive work (comments, IssueCreated, PullRequestCreated): issues/PRs and primary/secondary issues
    focal_comments, focal_comments_issue, focal_comments_pr = scope_focal_comments_r4(
        repository=repository, cycleNumber=cycleNumber, startTime=startTime, endTime=endTime)
    if focal_comments:
        create_invIssues_invPRsComment_r4(
            focal_comments_issue=focal_comments_issue, focal_comments_pr=focal_comments_pr,
            repository=repository, cycleNumber=cycleNumber)
        update_focal_issues_r4(
            focal_comments_issue=focal_comments_issue, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)
        update_focal_prs_commentPart_r4(
            focal_comments_pr=focal_comments_pr, repository=repository, cycleNumber=cycleNumber,
            startTime=startTime, endTime=endTime)
        update_focal_developers_comments_r4(
            focal_comments=focal_comments, repository=repository, cycleNumber=cycleNumber)


def step5_variables(case):
    repository = case["repository"]
    cycleNumber = case["cycleNumber"]
    startTime = case["startTime"]
    endTime = case["endTime"]
    days = case["days"]

    # 5a. Outcomes: speed, novelty, quality
    calculate_performance_outcomes(
        repository=repository, cycleNumber=cycleNumber, startTime=startTime, endTime=endTime, days=days)

    # 5b. Collective attention attributes
    # pdf and sif (technical); these functions also write pdi and sii, which update_pdi_r4 and update_sii_r4
    # then overwrite with the final discursive measures
    calculate_primaryDivision(repository=repository, cycleNumber=cycleNumber)
    calculate_secondaryIntegration(repository=repository, cycleNumber=cycleNumber)
    update_pdi_r4(repository=repository, cycleNumber=cycleNumber)
    update_sii_r4(repository=repository, cycleNumber=cycleNumber)

    # 5c. Contingencies: task interdependence (first pass; stores the issue-based part, issue_interdependence_r4)
    # and project ownership (days is set in step 2)
    update_invPRs_ledTo_r4(repository=repository, cycleNumber=cycleNumber)
    calculate_task_interdependence_r4(repository=repository, cycleNumber=cycleNumber)
    calculate_organizationOwnership(repository, cycleNumber)

    # 5d. Number of developers with a primary discursive focus (used in sample selection, step 6)
    update_numDev_with_PrimarySecondary(repository=repository, cycleNumber=cycleNumber)


def step5e_final_task_interdependence():
    # 5e-1. Flag the release cycles in the final sample (inSample); loops over all release cycles itself
    update_inSample_r4()
    num_cycles = ReleaseCycle.objects().count()
    # 5e-2. Final task interdependence: file-based part linked through the discursive tasks (issues, or PRs not
    # linked to an issue) behind each file's PRs; computed for release cycles in the sample
    for i in range(0, num_cycles):
        case = ReleaseCycle.objects[i:i + 1].only("repository", "cycleNumber").first()
        calculate_task_interdependence_r4_final(repository=case["repository"], cycleNumber=case["cycleNumber"])


def step6_sample_calibration():
    # Writes sample0.csv, sample0_descriptive.csv, sample0_fsQCA.csv, and contingency subsamples to `folder`
    # (set in step6_sample_calibration/fsqca_sample.py)
    construct_sample_r4()


def step7_merge_truthTables():
    # Requires the truth tables exported by fsQCA 3.0 (truthTable_ca_*.csv) in the folder structure of
    # data_truthTables_results/ (set results_folder in step7_results/merge_truthTables.py)
    paper_tables_r4()  # main analysis: all outcomes and all contingency subsamples (Tables A.1 and A.2)
    merge_main_robustness_truthTables_r4()  # main analysis next to Robustness 2-6 (Table B.2)


"""
Robustness tests (Section 6.3, Table 6, Appendix B)
----------------------------------------------------
Each test writes its own copy of the step-6 files (set `folder` in step6_sample_calibration/fsqca_sample.py to the
test's folder, e.g., .../robust2_calibaration_90th_10th/), which are then analyzed in fsQCA 3.0 as in the main
analysis. Folder names follow data_truthTables_results/.

Robustness 1 (deviation scores): step7_results/robustness1_deviation_score.do (Stata 14), on the main-analysis
    files written by step 6.

Robustness 2 (calibration anchors): in step6_sample_calibration/fsqca_sample.py, calibration_r4(), uncomment
    (a) the block that sets full/non-membership anchors to the 90th/10th percentiles, or
    (b) the block that moves the crossover by percent=25 or percent=-25 (crossover_tuning_r3),
    change `folder`, and re-run step 6.

Robustness 3 (folder-level modules): in step6_sample_calibration/fsqca_sample.py, replace the 'tpi', 'tsi' (and
    'tpi1', 'tsi1') entries with the commented 'tpi_f', 'tsi_f' (and 'tpi_f1', 'tsi_f1') lines, change `folder`, and
    re-run step 6. pdm and sim are computed in step 5b.

Robustness 4 (primary focus): copy the release-cycle collections in db2_paper_r4 (sample0, sample0_invDevelopers,
    ...) to a new sample, point the `meta` collections in classes/releasecycle/release_cycle.py to the copy, then
    for each release cycle run
        update_involvedDevelopers_primaryChange(repository, cycleNumber,
            change_primary_secondary=change_primary_secondary_1st2ndHighest)   # second-highest rank
            # or change_primary_secondary=change_primary_secondary_1stQuantile  # top decile
        calculate_primaryDivision(repository, cycleNumber)
        calculate_secondaryIntegration(repository, cycleNumber)
    (step5_variables/robustness_primary_focus.py), and re-run step 6 on the copied collection.

Robustness 5 (excluding peripheral developers): copy the release-cycle collections in db2_paper_r4 to
    sample1_scopeDev, sample1_scopeDev_invDevelopers, ... ; point the `meta` collections in
    classes/releasecycle/release_cycle.py to them; set threshold = 15 above; re-run steps 4, 5 and 6 (in step 6, read
    db.sample1_scopeDev in construct_sample_r4()).

Robustness 6 (removing small groups): in step6_sample_calibration/fsqca_sample.py, sample_selection_r4(), uncomment
    df = df.loc[df['num_developers'] >= 5], change `folder`, and re-run step 6.
"""

if __name__ == '__main__':
    main()
