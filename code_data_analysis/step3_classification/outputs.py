"""
Step 3a. Build the set of outputs (merged pull requests) and classify each as NewFeature, BugFixing,
or Documentation (collection innovation_outputs). Developer labels are the training baseline;
unlabeled outputs are predicted by the text classifier.
"""

import pandas
from classes.analysis.innovationoutput import InnovationOutput
from classes.analysis.innovativeaction import InnovativeAction
from classes.github.event.label.labeled import LabeledEvent
from classes.github.event.label.unlabeled import UnlabeledEvent
from classes.github.event.output.merged import Merged
from classes.github.issuecollection.pullrequest import PullRequest
from pymongo import MongoClient
from step1_data_preparation.fetch_commits import fetch_repo_commit
from step3_classification.text_classification import clean_doc
from step3_classification.text_classification import get_final_pred_by_maxVoting
from step3_classification.text_classification import text_classification


def classify_innovationOutputs():
    """
    Algorithm (three child functions):
    1. Find merged events which are labeled by developers as bug, feature, or documentation
    2. Find the best text classifier for the innovation outputs
        (done by explore_text_classifiers(trainDF) function in textclassification.py)
    3. Use the classifier to classify the rest merged outputs
    :return:
    """
    # The data collection of innovation outputs is constructed beforehand by construct_innovationOutput_dataset()
    # and update_innovationOutput_category_removeEnhancement() (see main.py)

    # Construct pandas dataframes (trainDF, and toBePredictedDF) by connecting to MongoDB

    print("Work on text classification of innovation outputs")

    conn_str = 'mongodb://localhost:27017'
    client = MongoClient(conn_str)
    db = client['db1_small_analysis']  # Specify name of the database
    coll = db.innovation_outputs  # Specify the collection
    trainDF = pandas.DataFrame(
        list(coll.find(
            {"category1": {"$ne": None}},
            {"_id": 1, "category1": 1, "mergedCommitMessage": 1, "title": 1, "body": 1}
        ))
    )  # we find that it is better to use text instead of clean_text

    trainDF['all'] = trainDF['mergedCommitMessage'] + ' ' + trainDF['title'] + ' ' + trainDF['body']
    trainDF = trainDF.drop(['mergedCommitMessage', 'title', 'body'], axis=1)

    # 1. Train a text classifier that classifies the innovation outputs into:
    #   BugFixing, NewFeature, and Documentation by using trainDF
    encoder_label, best_label, classifiers_label, feature_vectors_label = text_classification(
        x=trainDF['all'], y=trainDF['category1']
    )

    # 2. Train a text classifier that labeles whether an innovation output is NewFeature or not
    trainDF['isFeature'] = trainDF['category1']
    trainDF.loc[trainDF['category1'] != 'NewFeature', 'isFeature'] = "NotNewFeature"
    encoder_isFeature, best_isFeature, classifiers_isFeature, feature_vectors_isFeature = text_classification(
        x=trainDF['all'], y=trainDF['isFeature']
    )

    trainDF = trainDF.drop(['all'], axis=1)

    # 3. Predict chunks of toBePredicted and save the information in MongoDB

    num_models = len(classifiers_label)
    if num_models != len(classifiers_isFeature):
        raise Exception("!! Debug")

    toBePredictedDF = pandas.DataFrame(
        list(coll.find(
            {"category1": {"$eq": None}},
            {"_id": 1, "mergedCommitMessage": 1, "title": 1, "body": 1}
        ))
    )
    toBePredictedDF['all'] = toBePredictedDF['mergedCommitMessage'] + ' ' + toBePredictedDF['title'] + ' ' \
                             + toBePredictedDF['body']
    toBePredictedDF = toBePredictedDF.drop(['mergedCommitMessage', 'title', 'body'], axis=1)

    begin = 0
    delta = 10000
    end = toBePredictedDF.shape[0]

    while begin < end:
        cursor = begin + delta
        if cursor > end:
            cursor = end

        # predict a chunk of toBePredicted
        pred_label = []
        pred_isFeature = []
        chunk = pandas.DataFrame()
        for i in range(0, num_models):
            chunk = toBePredictedDF.iloc[begin:cursor, :]
            text = chunk['all']
            text_feature_label = feature_vectors_label[i].transform(text.values.astype('U'))
            predictions = classifiers_label[i].predict(text_feature_label)
            pred_label.append(predictions)

            text_feature_isFeature = feature_vectors_isFeature[i].transform(text.values.astype('U'))
            predictions = classifiers_isFeature[i].predict(text_feature_isFeature)
            pred_isFeature.append(predictions)

        # Get the final predictions by max voting
        final_pred_label = get_final_pred_by_maxVoting(
            pred_array=pred_label, best_pred=pred_label[best_label]
        )
        final_pred_isFeature = get_final_pred_by_maxVoting(
            pred_array=pred_isFeature, best_pred=pred_isFeature[best_isFeature]
        )

        final_pred_label = encoder_label.inverse_transform(final_pred_label)
        final_pred_isFeature = encoder_isFeature.inverse_transform(final_pred_isFeature)

        if len(final_pred_label) != (cursor - begin) or len(final_pred_isFeature) != (cursor - begin):
            raise Exception("!! Debug")

        chunk['label'] = final_pred_label
        chunk['isFeature'] = final_pred_isFeature
        chunk = chunk.drop(['all'], axis=1)

        # Save the inforamtion about final predictions in MongoDB
        save_chunk_predictions_innovationOutput_MongoDB(chunk)
        print(" --> Saved the predicted label and isFeature information of toBePredictedDF[{} - {}]"
              .format(str(begin), str(cursor)))
        print("****************************************")

        begin = cursor

    # 4. Save the label and feature-or-not information of trainDF in MongoDB
    print("****************************************")
    print("Working on the known innovation outputs in trainDF: ")
    trainDF['label'] = trainDF['category1']
    df = trainDF[['_id', 'label', 'isFeature']]
    save_chunk_predictions_innovationOutput_MongoDB(df)
    print(" --> Saved the label and isFeature information of trainDF innovation outputs in MongoDB")

    return


def save_chunk_predictions_innovationOutput_MongoDB(chunk):
    begin = 0
    end = chunk.shape[0]
    for i in range(begin, end):
        output_id = chunk.iloc[i, 0]
        label = chunk.iloc[i, 1]
        content = chunk.iloc[i, 2]
        if content == "NewFeature":
            isFeature = 1
        elif content == "NotNewFeature":
            isFeature = 0
        else:
            raise Exception("!! {} is an unidentified value of the content for isFeature".format(content))
        num_update = InnovationOutput.objects(id=output_id).update(label=label, isFeature=isFeature)
        if num_update != 1:
            raise Exception("There should be only one innovation output with object ID: {}".format(output_id))
    return


# Child function of def classify_mergedOutput()
def construct_innovationOutput_dataset():
    """
    Save the constructed file dataset into a text file
    1. Pull out the texts with labels relevant to bug, feature, documentation
    2. Clear each text and store it with label into the dataset file
    :return: saved file dataset
    """

    # Traverse merged prs and find those that are labeled as the three categories
    # Save them in the collection: innovation_output (InnovationOutput class)
    begin = 0
    delta = 10000
    end = Merged.objects().count()  # 249670
    while begin < end:
        # move the cursor by delta; if the cursor exceeds the length, then cursor = end
        cursor = begin + delta
        if cursor > end:
            cursor = end

        # get a block of Mergd events
        merges = Merged.objects[begin:cursor]
        for merge in merges:
            # get the information of category based on developers labeling
            category = check_output_category_by_labelName(merge=merge)
            if category:  # double check the returned category
                if category != "BugFixing" and category != "NewFeature" and category != "Documentation":
                    raise Exception("{} is unrecognized category".format(category))

            # get basic pr info
            repository = merge["repository"]
            number = merge["number"]
            mergedCommitOid = merge["commitOid"]

            # Continue if the mergedCommitOid is None or the changedFilesCount == 0
            changedFilesCount = merge["changedFilesCount"]
            if not mergedCommitOid or changedFilesCount == 0:
                continue

            # get information on whether the merged commit is in the final default branch
            # and the message of merged commit
            commits = InnovativeAction.objects(commitRepository=repository, oid=mergedCommitOid). \
                only("isInDefaultBranch", "message")
            # deal with the situation that the merged commit cannot be found in the innovative_actions collection
            # note that this commit must not in the default branch
            isToDefaultBranch = None
            message = None
            if len(commits) == 1:
                isToDefaultBranch = commits[0]["isInDefaultBranch"]
                message = commits[0]["message"]
            elif len(commits) == 0:
                if repository and mergedCommitOid:
                    message = fetch_repo_commit(repository=repository, commitOid=mergedCommitOid)
            else:
                raise Exception("!! There should be only one commit with repo: {}, oid: {}".
                                format(repository, mergedCommitOid))

            # get the text and cleaned text of the merged pull request
            prs = PullRequest.objects(repository=repository, number=number).only("title", "body")
            if len(prs) != 1:
                raise Exception("There should be a pr with #{} in repo {}".format(str(number), repository))
            # Get the title and body and let them constitute the text to be mined
            title = prs[0]["title"]
            body = prs[0]["body"]
            clean_mergedCommitMessage = clean_doc(message)
            clean_title = clean_doc(title)
            clean_body = clean_doc(body)

            # save the innovation output
            output = InnovationOutput(
                repository=repository, number=number, createdAt=merge["createdAt"],
                isToDefaultBranch=isToDefaultBranch, category=category,
                mergedCommitOid=mergedCommitOid,
                mergedEventId=merge["id"], mergedEventUrl=merge["url"],
                changedFilesCount=changedFilesCount,
                additions=merge["additions"], deletions=merge["deletions"],
                mergedCommitMessage=message, title=title, body=body,
                clean_mergedCommitMessage=clean_mergedCommitMessage, clean_title=clean_title, clean_body=clean_body
            )
            output.save()
        print("Merged events from index {} - {} is finished".format(str(begin), str(cursor)))
        print("***********************************************************")
        begin = cursor

    return


# Child function of construct_innovationOutput_dataset()
def check_output_category_by_labelName(merge):
    category = None  # Revised as BugFixing, NewFeature, or Documentation
    repository = merge["repository"]
    number = merge["number"]
    labeledEvents = LabeledEvent.objects(repository=repository, number=number, labelableType="PullRequest"). \
        only("createdAt", "labelName").order_by("+createdAt")
    for event in labeledEvents:
        label = event["labelName"]
        # Check whether the label is removed
        unlabeled = UnlabeledEvent.objects(
            repository=repository, number=number, labelableType="PullRequest", createdAt__gte=event["createdAt"],
            labelName=event["labelName"]).count()
        if unlabeled > 0:
            continue
        # Check whether label is relevant to BugFixing, NewFeature, or Documentation
        label = label.lower()
        if "bug" in label:
            category = "BugFixing"
        elif "feature" in label or "enhancement" in label:
            category = "NewFeature"
        elif "documentation" in label:
            category = "Documentation"
        else:
            continue

    return category


def update_innovationOutput_category_removeEnhancement():
    begin = 0
    end = InnovationOutput.objects().count()

    outputs = InnovationOutput.objects().only("id", "repository", "number")
    for i in range(begin, end):
        output_id = outputs[i]["id"]
        repository = outputs[i]["repository"]
        number = outputs[i]["number"]
        category1 = check_innovationOutput_category_by_labelName1_removeEnhancement(repository=repository,
                                                                                    number=number)
        num_updated = InnovationOutput.objects(id=output_id).update(category1=category1)
        if num_updated != 1:
            raise Exception("!! Debug")

        print("Innovation output with index {} is finished.".format(str(i)))
        print("**************************************************")

    return


def check_innovationOutput_category_by_labelName1_removeEnhancement(repository, number):
    category = None  # Revised as BugFixing, NewFeature, or Documentation
    labeledEvents = LabeledEvent.objects(repository=repository, number=number, labelableType="PullRequest"). \
        only("createdAt", "labelName").order_by("+createdAt")
    for event in labeledEvents:
        label = event["labelName"]
        # Check whether the label is removed
        unlabeled = UnlabeledEvent.objects(
            repository=repository, number=number, labelableType="PullRequest", createdAt__gte=event["createdAt"],
            labelName=event["labelName"]).count()
        if unlabeled > 0:
            continue
        # Check whether label is relevant to BugFixing, NewFeature, or Documentation
        label = label.lower()
        if "bug" in label:
            category = "BugFixing"
        elif "feature" in label:
            category = "NewFeature"
        elif "documentation" in label:
            category = "Documentation"
        else:
            continue

    return category
