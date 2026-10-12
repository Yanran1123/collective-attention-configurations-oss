# code_data_analysis

This folder contains the code behind Sections 5 (Method) and 6 (Analyses and Results) and Appendices A–B of the paper, and nothing else. It does four things:
1. Reads the raw GitHub data collected by `../code_data_collection` (MongoDB database `db1_small`).
2. Builds the sample and the variables (steps 1–6).
3. Writes the CSV files analyzed in fsQCA 3.0.
4. After the fsQCA runs, merges the truth tables and runs the necessity and deviation-score analyses (step 7).

The outputs of the published analyses are in `../data_truthTables_results/` (see [Outputs](#outputs-data_truthtables_results)).

**Source.** The Python functions were taken **verbatim** from the authors' final analysis code. For the few deliberate edits, see [Changes from the final analysis code](#changes-from-the-final-analysis-code). Only module and folder names, imports, and variable names differ. Each module's docstring says which step it belongs to.

## How to run

1. Requirements:
   - **Python 3.8 or later** (`statistics.multimode` is used)
   - A local MongoDB server
   - Packages: `mongoengine`, `pymongo`, `pandas`, `numpy`, `requests`, `scikit-learn`, `xgboost`, `nltk` (with the `punkt` and `stopwords` data), `beautifulsoup4`, `urllib3`, `python-dateutil`, `openpyxl` (step 7)
   - fsQCA 3.0; R with the `QCA` package; Stata 14 with `outreg2`
2. Set a GitHub token: `export GITHUB_TOKEN="..."`. Steps 1 and 3a call the GitHub API; step 2b reads public GitHub compare pages. See the main README.
3. In `main.py`, set `RUN_STEPS` and run `python main.py` from this folder. Steps must run in order, because each step reads what earlier steps saved in MongoDB.
4. Set the output folders:
   - `folder` in `step6_sample_calibration/fsqca_sample.py`. It needs the subfolders listed there.
   - `results_folder` in `step7_results/merge_truthTables.py`.
   - The paths at the top of the R and Stata scripts.

Notes before running:
- `text_classification()` asks at the console for the index of the best classifier.
- The train/test split has no random seed, so classification metrics vary slightly between runs.

## Pipeline

| Step | Module | What it produces |
|---|---|---|
| 1a | `step1_data_preparation/prepare_actions.py` | `repos_info_2539` (project info, incl. owner type); `supportive_actions` (discursive actions); `innovative_actions` (commits) |
| 1b | `step1_data_preparation/default_branch.py`, `fetch_commits.py` | `isInDefaultBranch` flag on commits |
| 2a | `step2_release_cycles/release_cycles.py` | `repoByReleaseCycle_2539`, then `ReleaseCycle` (`sample0` in `db2_paper_r4`): 18,630 release cycles with `startTime`, `endTime`, `days` |
| 2b | `step2_release_cycles/merged_changes.py` | `changedFilesCount`, `additions`, `deletions` of each merge (`Merged` events), from the GitHub compare page between the PR's base commit and the merged commit |
| 3a | `step3_classification/outputs.py`, `text_classification.py` | `innovation_outputs`: each merged PR classified as NewFeature, BugFixing, or Documentation (merges with no changed files are skipped) |
| 3b | `step3_classification/input_issues.py` | `input_issues`: issue/PR labels. These do not enter any variable, but step 4 requires them. |
| 4a | `step4_involved_elements/code_part.py` | Per cycle: developers (authors of code changes), involved files and PRs, each developer's primary/secondary files and folders |
| 4b | `step4_involved_elements/comment_part.py` | Per cycle: involved issues/PRs, each developer's primary/secondary issues |
| 5a | `step5_variables/outcomes.py` | `speed`, `novelty`, `quality`, `hasNoChangeInfo` |
| 5b | `step5_variables/collective_attention.py` | `pdi`, `sii` (discursive); `pdf`, `sif` (technical, file level); `pdm`, `sim` (technical, folder level) |
| 5c | `step5_variables/contingencies.py` | `issue_interdependence_r4` (discursive part of task interdependence); `org` |
| 5d | `step5_variables/sample_counts.py` | `num_devWithPrimary_comment` (used for sample selection) |
| 5e | `step5_variables/in_sample.py`, `task_interdependence_final.py` | `inSample` flags; final `file_interdependence_r4` and `task_interdependence_r4` for cycles in the sample |
| 6 | `step6_sample_calibration/fsqca_sample.py`, `calibration.py` | Final sample, final variables, calibration. Writes `sample0.csv`, `sample0_descriptive.csv` (Table 2), `correlationPearson_sample0.csv` and `correlationSpearman_sample0.csv` (Table 3), `sample0_fsQCA.csv`, and the contingency subsamples |
| — | fsQCA 3.0 (by hand) | Truth tables and solutions; see [Analyses in fsQCA 3.0](#analyses-in-fsqca-30) |
| 7 | `step7_results/merge_truthTables.py` | Merged truth tables (Tables A.1, A.2, B.2) |
| 7 | `step7_results/necessity_analysis.R` | Necessity analyses (Section 6.1) |
| 7 | `step7_results/robustness1_deviation_score.do` | Robustness 1, deviation score analyses (Table B1) |

Steps 1–5 write to MongoDB. Step 6 and step 7 write files.

Supporting folders:
- `classes/`: MongoDB document schemas.
  - `github/`: raw GitHub data
  - `analysis/`: derived collections
  - `releasecycle/`: release-cycle data
- `setup/`: database connection and GitHub API helpers.
- `logs/repo_notFound.txt`: the 11 projects that could no longer be found on GitHub. Step 2 excludes them.

## Variables in the paper and in the code

| Paper | Column in `sample0.csv` | Calibrated column in `sample0_fsQCA.csv` | Computed by |
|---|---|---|---|
| Speed: outputs merged per day | `speed` | `s1` (negation `s0`) | `calculate_performance_outcomes` (step 5a) |
| Novelty: count of new features | `novelty` | `n1` (`n0`) | same |
| Quality: count of bugs fixed | `quality` | `q1` (`q0`) | same |
| Discursive primary integration (dpi) | `dpi` = 1 − `pdi` | `dpi1` | `update_pdi_r4` (step 5b) |
| Discursive secondary integration (dsi) | `dsi` = `sii` | `dsi1` | `update_sii_r4` (step 5b) |
| Technical primary integration (tpi) | `tpi` = 1 − `pdf` | `tpi1` | `calculate_primaryDivision` (step 5b) |
| Technical secondary integration (tsi) | `tsi` = `sif` | `tsi1` | `calculate_secondaryIntegration` (step 5b) |
| Overall task interdependence (OTI) | `task_interdependence` | `ti1` | steps 5c and 5e (see below) |
| Discursive task interdependence (DTI) | `discursive_task_interdependence` | `dti1` | step 5c (component of OTI; not analyzed separately in the paper) |
| Technical task interdependence (TTI) | `technical_task_interdependence` | `tti1` | step 5e (component of OTI; not analyzed separately in the paper) |
| Project ownership (1 = organization) | `org` | `org` (not calibrated) | `calculate_organizationOwnership` (step 5c) |
| Release-cycle length (days) | `days` | `days1` | `slice_repo_byReleaseCycle` (step 2a) |

**Names stored in MongoDB.** Steps 1–5 store intermediate fields under their original names. Step 6 builds the paper's variables from them:

| Stored field | Paper variable |
|---|---|
| `pdi` | `dpi` = 1 − `pdi` |
| `sii` | `dsi` |
| `pdf` | `tpi` = 1 − `pdf` |
| `sif` | `tsi` |
| `pdm`, `sim` | `tpi_f` = 1 − `pdm`, `tsi_f` (Robustness 3) |
| `task_interdependence_r4` | `task_interdependence` |
| `issue_interdependence_r4` | `discursive_task_interdependence` |
| `file_interdependence_r4` | `technical_task_interdependence` |

All files written by steps 6–7 and all files in `../data_truthTables_results/` use the paper's names.

Notes on the collective-attention measures:
- **Technical unit.** The main analysis uses file-level modules: each changed file's full path (`pdf`, `sif`). Robustness 3 uses folder-level modules: each file's folder (`pdm`, `sim`, giving `tpi_f` = 1 − `pdm` and `tsi_f` = `sim`).
- **Who counts.** Developers are the cycle's code authors. Discursive actions count only when made by these developers.
- **Primary and secondary foci.** A developer's primary focus is the item with the most actions; ties make all tied items primary. Other engaged items are secondary. Code changes are weighted by lines added plus deleted.
- **Primary integration.** `pdi` and `pdf` are Blau's index, 1 − Σ*P*ᵢ², with a developer split equally across tied primary items. So `dpi` and `tpi` equal Σ*P*ᵢ², as defined in the paper.
- **Secondary integration.** A developer with no secondary items has an overlap of *Q*_d = 0 and is still counted in the average across all *D* developers.
- **Discursive actions** are issue comments, commit comments, PR reviews, PR review comments, and the creation of issues and PRs. `calculate_primaryDivision` and `calculate_secondaryIntegration` also write `pdi` and `sii`. `update_pdi_r4` and `update_sii_r4` then overwrite them with the final discursive measures, using the same formulas.

Task interdependence is the mean of a discursive (issue-based) part and a technical (file-based) part, as in the paper.
- **Discursive tasks** are issues (issue-first workflow) and PRs not linked to any issue (PR-first workflow).
- **Discursive part:** each discursive task is represented by the files its PRs changed. Step 5c (`contingencies.py`) computes this (DTI; stored as `issue_interdependence_r4`, output as `discursive_task_interdependence`).
- **Technical part:** each file is represented by the discursive tasks behind the PRs that changed it, i.e. the issue(s) a PR came from, or the PR itself. Step 5e (`task_interdependence_final.py`) computes this for the cycles in the sample (`inSample = 1`, set by `in_sample.py`; TTI, output as `technical_task_interdependence`) and writes the final overall measure (OTI; stored as `task_interdependence_r4`, output as `task_interdependence`).
- **Why two steps:** this reproduces how the final values were produced. Step 5c's own file-based part (which links files by PR) is overwritten in step 5e. A read-only check confirmed that the stored `task_interdependence_r4` equals this definition in all 4,291 sample cycles.

## Sample selection

The filters are in `sample_selection_r4()` (step 6) and, with the same criteria, `update_inSample_r4()` (step 5e). The comments in `sample_selection_r4()` hold counts from earlier runs; the numbers below follow the paper.

| Paper | Code |
|---|---|
| Remove 9,439 cycles shorter than 14 days | `days >= 14` |
| Remove 4,597 cycles with fewer than two developers doing technical work **and** two doing discursive work | `num_developers > 1` (coders) and `num_devWithPrimary_comment >= 2` (coders who also comment) |
| Remove 239 cycles with missing data (API limits) | `hasNoChangeInfo != True` |
| Remove 64 cycles with no software updates | `speed > 0` |
| Final sample: 4,291 cycles, 1,004 projects | |

## Calibration

`calibration_r4()` (step 6) uses Ragin's direct method (`calibrate()`).
- **Anchors:** full membership, crossover and full nonmembership are set at the 75th, 50th and 25th percentiles.
- **Novelty and quality:** the crossover is the midpoint of the full and nonmembership anchors.

## Analyses in fsQCA 3.0

Section 6 and Appendix A. These steps were done in fsQCA 3.0, not in code.
- **Data:** `sample0_fsQCA.csv` (full sample) and the contingency subsamples written by step 6:
  - `contingency_task_interdependence/sample0_fsQCA_task_interdependence{1,M,0}.csv` (high: ≥ 75th percentile, moderate, low: ≤ 25th percentile)
  - `contingency_org/sample0_fsQCA_org{1,0}.csv`
  - `contingency_days/sample0_fsQCA_days{1,M,0}.csv`
- **Model:** outcome = f(`dpi1`, `dsi1`, `tpi1`, `tsi1`), for outcomes `s1`, `n1`, `q1` and their negations `s0`, `n0`, `q0` (full sample), and for `s1`, `n1`, `q1` in each subsample.
- **Truth table:** Quine–McCluskey algorithm. No frequency threshold was imposed (the smallest configuration has 45 cases).
- **Sufficiency:** raw consistency ≥ 0.80 (acceptable: 0.75) and PRI consistency ≥ 0.70, adjusted slightly where a sharp gap occurred near a threshold. Complex solutions are reported.
- **Outputs:** each truth table was exported as `truthTable_ca_<outcome>.csv` (subsamples: `truthTable_ca_<outcome>_<ti|org|days><1|M|0>.csv`), and the solutions saved as `results_ca_*.txt`, in the output folder of the analysis.

## Step 7: tables, necessity, and deviation scores

- **Merged truth tables** (`merge_truthTables.py`; `main.py` runs it as step 7):
  - `paper_tables_r4()` merges the main-analysis truth tables across outcomes (Table A.1) and contingency subsamples (Table A.2).
  - `merge_main_robustness_truthTables_r4()` places the main analysis next to Robustness 2–6 for each high-performance outcome, in the full sample and in each subsample (Table B.2).
  - Both read and write in the folder structure of `../data_truthTables_results/`.
- **Necessity analyses** (`necessity_analysis.R`, Section 6.1):
  - Uses `pof()` from the R package `QCA`, which reports consistency, relevance of necessity (RoN) and coverage.
  - Tests the absence of primary integration and the presence of secondary integration against high speed, novelty and quality.
  - Runs in the full sample and in each subsample analyzed.
  - The original analyses were run in the R console; the logs are in `../data_truthTables_results/main/necessity_analysis/`. The script repeats the logged tests for every sample.
- **Robustness 1, deviation scores** (`robustness1_deviation_score.do`, Table B1):
  - For each solution, a case's deviation is its Euclidean distance from the solution's ideal type.
  - Where an outcome has several solutions, fit is the negative of the minimum deviation across them.
  - Fit predicts membership in the outcome in a two-limit Tobit model, with standard errors clustered by project.

## Robustness tests

Each test (Table 6) writes its own copy of the step-6 files to its own folder, named as in `../data_truthTables_results/`. Those files are analyzed in fsQCA 3.0 as in the main analysis, then merged by step 7. The same sample selection and subsample criteria apply throughout. `main.py` ends with step-by-step instructions.

| Test | Output folder | How to run |
|---|---|---|
| R1. Deviation score analyses | `robust1_deviationScore/` | `step7_results/robustness1_deviation_score.do` on the main-analysis files |
| R2. Calibration: 90th/10th anchors | `robust2_calibaration_90th_10th/` | Uncomment the 90th/10th block in `calibration_r4()`. Applies to the four collective-attention conditions; outcomes, task interdependence and days keep 75/25 (the block resets the anchors at the first outcome). |
| R2. Calibration: crossover −25% / +25% | `robust2_calibaration_crossover_down25/`, `…_up25/` | Uncomment the crossover block in `calibration_r4()` (`percent=-25` or `25`). Applies to the collective-attention conditions and the contingencies. |
| R3. Folder-level modules | `robust3_folder/` | In `fsqca_sample.py`, use the commented `tpi_f`, `tsi_f` (`tpi_f1`, `tsi_f1`) lines in place of `tpi`, `tsi` (`tpi1`, `tsi1`). |
| R4. Primary focus: first and second rank | `robust4_sample2_primary1st2ndHighest/` | `robustness_primary_focus.py` with `change_primary_secondary_1st2ndHighest`, on a copy of the collections, then steps 5b and 6 |
| R4. Primary focus: top decile | `robust4_sample2_primary1stQuantile/` | Same, with `change_primary_secondary_1stQuantile`. The decile is each developer's own 90th percentile across items; developers with 10 or fewer items keep their highest-ranked items. |
| R5. Excluding peripheral developers | `robust5_sample1_scopeDevelopers/` | Set `threshold = 15` in `main.py` (developers with fewer than 15 lines of code change are excluded), point the release-cycle schemas to the `sample1_scopeDev…` collections, and re-run steps 4–6. |
| R6. Removing small groups | `robust6_remove_smallCollectives_noLessThan5/` | Uncomment `df = df.loc[df['num_developers'] >= 5]` in `sample_selection_r4()` (2,122 cycles). |

## Outputs (`data_truthTables_results/`)

| Folder | Contents | Paper |
|---|---|---|
| `main/` | `sample0.csv`; `sample0_descriptive.csv/.xlsx`; Pearson and Spearman correlations; `sample0_fsQCA.csv`; truth tables `truthTable_ca_{s1,n1,q1,s0,n0,q0}.csv`; solutions `results_ca_all.txt` | Tables 2–4, A.1 |
| `main/contingency_*/` | Subsample files, truth tables and solutions for task interdependence, ownership and cycle length | Tables 5, A.2 |
| `main/necessity_analysis/` | Inputs, R console logs and results of the necessity analyses. The inputs are copies of the step-6 files; `~x` columns equal 1 − x. In the full-sample copy, `ti1` is from an earlier version of task interdependence, but no necessity test uses it. | Section 6.1 |
| `robust1_deviationScore/` | Stata do-file (`regression.do`), log (`regression.smcl`), input files, and the Tobit tables of the final run (`table1_*.rtf`, with plain-text copies `table1_*.txt`) | Table B1 |
| `robust2_…` to `robust6_…` | Files, truth tables and solutions of Robustness 2–6 | Tables 6, B.2 |
| `merged_truthTables/` | Merged truth tables written by step 7. `final/` holds the tables assembled for the paper, some of them combined by hand (e.g., `ca_allDVs_ti1_tiM.xlsx`). | Tables A.1, A.2, B.2 |

## Other details worth knowing

1. **Speed** counts merged PRs that are involved in the cycle, i.e. that received at least one human commit during the cycle.
   - **Missing data.** A cycle has `hasNoChangeInfo = True` (the paper's 239 cycles with missing data) when one of its outputs has no lines-changed information, because GitHub's compare page could not report the merge's changes in step 2b.
   - **Fragility.** Step 2b reads the HTML of GitHub's compare pages, which have changed since 2020, so re-running it may need an update to the page parsing in `compare_commits_url()`.
2. **Discursive units.** A developer's comments on a PR linked to an issue they also commented on are attributed to that issue. Otherwise the PR is the unit.
3. **Projects behind the 18,630 cycles.**
   - Step 2 skips the 11 projects in `logs/repo_notFound.txt`.
   - It also skips releases made before any default-branch commit.
   - Prereleases count as releases; draft releases do not.

## Changes from the final analysis code

- **Module, folder and schema-package names.** In the original, modules lived in several folders, one per revision round. Their functions are unchanged.
- **Task interdependence.** The final code's `calculate_task_interdependence_r4` is the second-pass version, which recomputes the file-based part. Its first-pass discursive part is commented out there (lines 75–138). To run both passes:
  - The first-pass version is included as step 5c. Its discursive part is identical to those commented lines.
  - The second-pass version is included unchanged as step 5e, together with `update_inSample_r4()`, which it requires.
- **Variable names,** to match the paper:
  - `epc` → `dpi` (1 − `pdi`)
  - `esc` → `dsi` (`sii`)
  - `tpc` → `tpi` (1 − `pdf`)
  - `tsc` → `tsi` (`sif`)
  - folder level: `tpc_f` → `tpi_f`, `tsc_f` → `tsi_f`
  - `task_interdependence_r4` → `task_interdependence`; `issue_interdependence_r4` → `discursive_task_interdependence` (`ii1` → `dti1`); `file_interdependence_r4` → `technical_task_interdependence` (`fi1` → `tti1`)

  The same renaming applies in the step-7 scripts and in all files, folder names and file names in `../data_truthTables_results/`. Only labels changed; every value is unchanged.
- **Settings left from the last robustness run:**
  - The release-cycle schemas pointed to the Robustness 5 collections (`sample1_scopeDev…`); they point to the main collections (`sample0…`) here.
  - The Robustness 6 filter was set to at least 3 developers, an unreported variant; it is set to 5 here, as in the reported test.
  - `folder` and `results_folder` are placeholders.
- **Merge changes (step 2b).** `calculate_novelty_mergedEvents()`, `compare_commits_url()`, `convert_str_to_int()` and `fetch_changedInfo_of_mergedEvents()` were copied from the final code. They fill the `Merged` fields that steps 3a and 5a use. In the final code they sat among older calculations, and their resume index was reset to 0.
- **Supportive actions.** `action_info_db2()` and `save_supportive_action_db2()` keep only the six discursive action types used in the paper. The original also copied 44 other event types that no variable uses.
- **Classification datasets.** The dataset-construction calls were moved out of `classify_innovationOutputs()` and `classify_inputIssues()` into `main.py`. This lets the label clean-up step run between construction and classification, as in the original workflow.
- **Fresh-run defaults:**
  - Hard-coded resume indices were reset to 0.
  - Windows paths were replaced with `logs/…`.
  - The Windows database name `db1_analysis_small` was replaced with `db1_small_analysis`.
  - GitHub tokens were replaced with the `GITHUB_TOKEN` environment variable.
- **Step 7:**
  - `merge_truthTables.py` is the authors' merge script, with paths replaced by `results_folder`.
  - `robustness1_deviation_score.do` is the authors' do-file, with paths replaced.
  - `necessity_analysis.R` repeats the commands logged in the R console.
- **Comments and docstrings** that referred to an earlier sample or to local paths were updated.
- **`main.py` is new.** It runs the steps in the order the original code was run.
