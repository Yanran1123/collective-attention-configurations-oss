# code_data_collection

This folder contains the code that collected the paper's GitHub data: public **machine-learning** root repositories created from GitHub's launch through December 2019, tracked until August 2020 (Section 5.1). The data are stored in the MongoDB database **`db1_small`**, which `../code_data_analysis` reads (alias `core`).

**Parallel collection.** The data were collected on three machines at the same time, each working on a different part of the repository list, and the results were combined into `db1_small`. This folder is built from the copy used on one of these machines (the server). It is the only copy still in the state used for this sample: the other two were later revised for a different, larger data collection. In those two copies, the functions that save timeline events, merges, reviews and comments are still identical to the ones here.

**Source.** This is the authors' collection code for this sample. The files are unchanged except for the [edits listed below](#changes-from-the-original-code). In the original working copy, many files had been displaced into neighboring folders (e.g., `Classes/event/assign/unassigned.py` was stored under `Classes/commit/`, and `setup/mongo_setup.py` under `setup/__pycache__/`). Each file has been put back at the location its import statements refer to, and all imports resolve.

## How to run

1. Requirements:
   - Python 3.7 (the version used for the original runs)
   - `mongoengine`, `pymongo`, `requests`, `pathlib2`
   - A local MongoDB server
2. Set a GitHub token: `export GITHUB_TOKEN="..."` (see the main README). `fetchGitHub/fetchcommit.py` can rotate among three tokens (`GITHUB_TOKEN_1`, `_2`, `_3`).
3. Call the functions below in order, e.g., from a Python console in this folder after `from setup import mongo_setup; mongo_setup.global_init()`.

**Do not run `python main.py` as it is.** The file ends with a call to `main()`, which is left in the state of the authors' last run: a repair that **deletes** the stored timeline events of one pull request (apple/turicreate #2819) and fetches them again. Use the step functions directly instead.

## Steps

| Step | Function (module) | What it does |
|---|---|---|
| 1 | `save_repo_list(path)` (`main.py`) | Calls `fetch_repo_list("machine-learning", "2019-12-31")` (`fetchGitHub/fetchrepolist.py`). It searches `is:public is:root topic:machine-learning created:…` year by year from 2008, splitting a year into months or days when a search would exceed GitHub's 1,000-result limit. Writes the list (`owner,name`) to a CSV file. |
| 2 | *(by hand)* | Remove duplicate repositories. Save the result as `repo_list_dupRemoved.csv` with a header row (step 3 skips the first row). |
| 3 | `save_repo_info(path)` (`main.py`) | For each repository still found on GitHub: `add_repo`, `update_release`, `update_topic`, `update_language` (`fetchGitHub/fetchrepoinfo.py`). |
| 4 | `repo_list_final_csv(path)` (`main.py`) | Writes the list of collected repositories: the **36,280** machine-learning projects. |
| 5 | `get_small_sample()` (`explore/reposelection.py`) | **Deletes** repositories with no recorded release (`releaseCount = 0`) or no codebase (`languageSize = 0`), leaving the **2,539** projects of the paper's sample. |
| 6 | `add_issues(owner, name)`; `update_issue_edits(owner, name, number)` (`fetchGitHub/fetchissueinfo.py`) | Issues and their edit histories |
| 7 | `add_prs_part1(owner, name)`; then for each pull request `update_pr_part2`, `update_pr_base_associationPRs`, `update_pr_head_associationPRs`, `update_pr_changed_files`, `update_pr_edits`, `update_pr_suggested_reviewers` (`fetchGitHub/fetchprinfo.py`) | Pull requests and their details |
| 8 | `save_repo_commits(repository, remaining, reset, page)` and `update_changed_info(...)` (`fetchGitHub/fetchcommit.py`, REST API v3); `save_repo_commit_graphQL(repository, commitOid)` (`fetchGitHub/fetchcommit_graphql.py`) for commits the REST API cannot return | Commits with additions, deletions, and changed files |
| 9 | `update_issue_timeline(owner, name, number)` (`fetchGitHub/fetchissueevents.py`) | Issue timeline events |
| 10 | `update_pr_timeline_items(owner, name, number)` (`fetchGitHub/fetchprevents.py`); `update_pr_timeline_items_repair(...)` (`fetchprevents_repair.py`) for pull requests whose query returned GitHub's "Something went wrong" error | Pull request timeline events (merges, reviews, review comments, commit comments, and other events) |

`main.py` keeps the drivers of steps 1, 3 and 4. Steps 6–10 were run with loops over the repositories, issues, or pull requests in MongoDB that are no longer in `main.py`; each function takes the repository and number as arguments.

The number of files, lines added and lines deleted of each merge (`Merged` events) are filled in later, in `code_data_analysis` (step 2, `merged_changes.py`).

## Folder structure

| Folder / file | Role |
|---|---|
| `main.py` | Drivers of steps 1, 3, 4; the `main()` repair state described above; `delete_pr_event()` used by that repair |
| `fetchGitHub/` | Functions that query the GitHub GraphQL and REST APIs |
| `Classes/` | `mongoengine` schemas of repositories, actors, issues, pull requests, commits, and each type of timeline event |
| `explore/` | `get_small_sample()` (step 5); `issue_pr_count_csv()` (counts of issues and PRs per repository) |
| `setup/` | MongoDB connection (`mongo_setup.py`, database `db1_small`), GitHub GraphQL helpers and rate-limit handling (`graphql.py`), repository-renaming helper (`functions.py`) |

`fetchrepolist_new.py` (`fetch_repo_list_period`, a date-window search without a topic) is imported by `main.py` but was not used for this sample.

## Notes on reproducing the collection

- **Live data.** The data were collected from the live GitHub API in 2020. Because repositories are deleted, renamed and edited over time, re-running the code will not produce exactly the same dataset.
- **Manual restarts.** Long runs were restarted by hand after connection or rate-limit failures, using hard-coded start indices.
- **Rate limits.** The code checks the remaining API quota and sleeps until it resets.
- **Known quirk.** In `fetch_repo_list`, the leap-year February branch calls `repos.extend(first, search_repo(search_query))` with its arguments swapped. That branch runs only when a single February month has 990 or more matching repositories, which did not occur for this sample.

## Changes from the original code

- **Files moved back to their canonical locations** (see above). Empty `__init__.py` files were added.
- **Credentials.** GitHub tokens were replaced with the `GITHUB_TOKEN` environment variables. The lists of the authors' tokens and accounts were removed, and the `User-Agent` is now `research-data-collection`.
- **Personal information.**
  - Local paths were replaced with placeholders (`path/to/errors/…`, `/path/to/project/…`).
  - A personal name was removed from a printed message.
  - An example in a comment that named two GitHub users was rewritten generically.
- **Not included:**
  - `explore/repostatistics.py`, an exploratory topic model of repository descriptions
  - `fetchGitHub/fetchcommitcomment.py`, an empty file

  Neither is imported anywhere.
