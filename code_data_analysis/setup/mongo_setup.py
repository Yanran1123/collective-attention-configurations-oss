import mongoengine

# MongoDB databases (local server, default port)
alias_core = 'core'
db = 'db1_small'  # raw GitHub data collected by code_data_collection (repos, issues, prs, commits, events)

alias_analysis = 'analysis'
db_analysis = 'db1_small_analysis'  # derived collections: actions, classified outputs/issues, release cycles

alias_paper_r2 = 'paper_r2'
db_paper_r2 = 'db2_paper_r4'  # release-cycle-level data and variables used in the paper


# Just call this function in the main program to execute the connection
def global_init():
    mongoengine.register_connection(alias=alias_core, name=db)
    mongoengine.register_connection(alias=alias_analysis, db=db_analysis)
    mongoengine.register_connection(alias=alias_paper_r2, db=db_paper_r2)
