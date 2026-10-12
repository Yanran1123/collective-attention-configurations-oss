"""
Step 3b. Label issues and pull requests (BugReport, FeatureRequest, Documentation, Question)
(collection input_issues). These labels do not enter the final variables, but the Step 4 code requires
every involved issue/PR to have one.
"""

import pandas
from classes.analysis.inputissue import InputIssue
from classes.github.event.label.labeled import LabeledEvent
from classes.github.event.label.unlabeled import UnlabeledEvent
from classes.github.issuecollection.issue import Issue
from classes.github.issuecollection.pullrequest import PullRequest
from pymongo import MongoClient
from step3_classification.text_classification import clean_doc
from step3_classification.text_classification import get_final_pred_by_maxVoting
from step3_classification.text_classification import text_classification


def classify_inputIssues():
    """
    Algorithm (three child functions):
    1. Pull out pull-requests and its associated issue that are labeled as bug-fixing, new-feature, or documentation
    2. Do text classifier, try different techniques of supervised machine learning
    3. Use the classifier to classify the rest merged outputs
    :return:
    """
    # !!!!! Include merged event that has a valid mergedCommit, some oid is None
    # 35 merged events have commitOid as None

    # The data collection of input issues is constructed beforehand by construct_inputIssue_dataset()
    # and update_inputIssue_category_removeEnhancement() (see main.py)

    # Construct pandas dataframes (trainDF, and toBePredictedDF) by connecting to MongoDB

    print("\nWork on text classification of input issues")

    conn_str = 'mongodb://localhost:27017'
    client = MongoClient(conn_str)
    db = client['db1_small_analysis']  # Specify name of the database
    coll = db.input_issues  # Specify the collection
    trainDF = pandas.DataFrame(
        list(coll.find(
            {"category1": {"$ne": None}},
            {"_id": 1, "category1": 1, "title": 1, "body": 1}
        ))
    )

    trainDF['all'] = trainDF['title'] + ' ' + trainDF['body']
    trainDF = trainDF.drop(['title', 'body'], axis=1)

    # 1. Train a text classifier that classifies the innovation outputs into:
    #   BugFixing, NewFeature, and Documentation by using trainDF
    encoder_label, best_label, classifiers_label, feature_vectors_label = text_classification(
        x=trainDF['all'], y=trainDF['category1']
    )

    # 2. Label whether an innovation output is NewFeature or not
    trainDF['isFeature'] = trainDF['category1']
    trainDF.loc[trainDF['category1'] != 'FeatureRequest', 'isFeature'] = "NotFeatureRequest"
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
            {"_id": 1, "title": 1, "body": 1}
        ))
    )
    toBePredictedDF['all'] = toBePredictedDF['title'] + ' ' + toBePredictedDF['body']
    toBePredictedDF = toBePredictedDF.drop(['title', 'body'], axis=1)

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
        save_chunk_predictions_inputIssue_MongoDB(chunk)
        print(" --> Saved the predicted label and isFeature information of toBePredictedDF[{} - {}]"
              .format(str(begin), str(cursor)))
        print("****************************************")

        begin = cursor

    # 4. Save the label and feature-or-not information of trainDF in MongoDB
    print("****************************************")
    print("Working on the known input issues in trainDF: ")
    trainDF['label'] = trainDF['category1']
    df = trainDF[['_id', 'label', 'isFeature']]
    save_chunk_predictions_inputIssue_MongoDB(df)
    print(" --> Saved the label and isFeature information of trainDF input issues in MongoDB")

    return


def save_chunk_predictions_inputIssue_MongoDB(chunk):
    begin = 0
    end = chunk.shape[0]
    for i in range(begin, end):
        output_id = chunk.iloc[i, 0]
        label = chunk.iloc[i, 1]
        content = chunk.iloc[i, 2]
        if content == "FeatureRequest":
            isFeature = 1
        elif content == "NotFeatureRequest":
            isFeature = 0
        else:
            raise Exception("!! {} is an unidentified value of the content for isFeature".format(content))
        num_update = InputIssue.objects(id=output_id).update(label=label, isFeature=isFeature)
        if num_update != 1:
            raise Exception("There should be only one input issue with object ID: {}".format(output_id))
    return


def construct_inputIssue_dataset():
    # Fetch the text of all issues and save the category information if it is clearly a
    # BugReport, FeatureRequest, Documentation, or Question
    begin = 0
    delta = 1000
    end = Issue.objects().count()  # 306503
    while begin < end:
        # move the cursor by delta; if the cursor exceeds the length, then cursor = end
        cursor = begin + delta
        if cursor > end:
            cursor = end

        # get a block os issues
        issues = Issue.objects[begin:cursor].only("id", "repository", "number", "createdAt", "url", "title", "body")
        for i in issues:
            issueType = "Issue"
            # get the category information
            category = check_inputIssue_category_by_labelName(issue=i, issueType=issueType)
            if category:  # double check the returned category
                if category != "BugReport" and category != "FeatureRequest" and category != "Documentation"\
                        and category != "Question":
                    raise Exception("{} is unrecognized category".format(category))
            title = i["title"]
            body = i["body"]
            clean_title = clean_doc(title)
            clean_body = clean_doc(body)
            input_issue = InputIssue(
                repository=i["repository"], number=i["number"], createdAt=i["createdAt"], issueType=issueType,
                category=category, eventId=i["id"], eventUrl=i["url"],
                title=title, body=body, clean_title=clean_title, clean_body=clean_body
            )
            input_issue.save()
        print("Issues from index {} - {} is finished".format(str(begin), str(cursor)))
        print("***********************************************************")
        begin = cursor

    # Fetch the text of all prs and save the category information if it is clearly a
    # BugReport, FeatureRequest, Documentation, or Question
    begin = 0
    delta = 1000
    end = PullRequest.objects().count()  # 328443
    while begin < end:
        # move the cursor by delta; if the cursor exceeds the length, then cursor = end
        cursor = begin + delta
        if cursor > end:
            cursor = end

        # get a block of issues
        prs = PullRequest.objects[begin:cursor].only("id", "repository", "number", "createdAt", "url", "title", "body")
        for pr in prs:
            issueType = "PullRequest"
            # get the category information
            category = check_inputIssue_category_by_labelName(issue=pr, issueType=issueType)
            if category:  # double check the returned category
                if category != "BugReport" and category != "FeatureRequest" and category != "Documentation" \
                        and category != "Question":
                    raise Exception("{} is unrecognized category".format(category))
            title = pr["title"]
            body = pr['body']
            clean_title = clean_doc(title)
            clean_body = clean_doc(body)
            input_issue = InputIssue(
                repository=pr["repository"], number=pr["number"], createdAt=pr["createdAt"], issueType=issueType,
                category=category, eventId=pr["id"], eventUrl=pr["url"],
                title=title, body=body, clean_title=clean_title, clean_body=clean_body
            )
            input_issue.save()
        print("Prs from index {} - {} is finished".format(str(begin), str(cursor)))
        print("***********************************************************")
        begin = cursor

    return


# Child function of construct_inputIssue_dataset()
def check_inputIssue_category_by_labelName(issue, issueType):
    category = None  # Revised as BugFixing, NewFeature, or Documentation
    repository = issue["repository"]
    number = issue["number"]
    if issueType != "Issue" and issueType != "PullRequest":
        raise Exception("The type '{}' is not identified".format(issueType))
    # Get the Labeled events
    labeledEvents = LabeledEvent.objects(repository=repository, number=number, labelableType=issueType).\
        only("createdAt", "labelName").order_by("+createdAt")
    for event in labeledEvents:
        label = event["labelName"]
        # Check whether the label is removed
        unlabeled = UnlabeledEvent.objects(
            repository=repository, number=number, labelableType=issueType, createdAt__gte=event["createdAt"],
            labelName=label).count()
        # if the label is removed, continue to check the following labeled events
        if unlabeled > 0:
            continue
        # Check whether label is relevant to BugFixing, NewFeature, or Documentation
        label = label.lower()
        if "bug" in label:
            category = "BugReport"
        elif "feature" in label or "enhancement" in label:
            category = "FeatureRequest"
        elif "documentation" in label:
            category = "Documentation"
        elif "question" in label:
            category = "Question"
        else:
            continue

    return category


def update_inputIssue_category_removeEnhancement():
    begin = 0
    delta = 10000
    end = InputIssue.objects().count()

    while begin < end:
        # move the cursor by delta; if the cursor exceeds the length, then cursor = end
        cursor = begin + delta
        if cursor > end:
            cursor = end

        inputs = InputIssue.objects[begin:cursor].only("id", "repository", "number", "issueType")
        for i in inputs:
            input_id = i["id"]
            repository = i["repository"]
            number = i["number"]
            issueType = i["issueType"]
            category1 = check_inputIssue_category_by_labelName1_removeEnhancement(
                repository=repository, number=number, issueType=issueType)
            num_updated = InputIssue.objects(id=input_id).update(category1=category1)
            if num_updated != 1:
                raise Exception("!! Debug")

        print("Innovation output with index {} - {} is finished.".format(str(begin), str(cursor)))
        print("**************************************************")

        begin = cursor

    return


def check_inputIssue_category_by_labelName1_removeEnhancement(repository, number, issueType):
    category = None  # Revised as BugFixing, NewFeature, or Documentation
    if issueType != "Issue" and issueType != "PullRequest":
        raise Exception("The type '{}' is not identified".format(issueType))
    # Get the Labeled events
    labeledEvents = LabeledEvent.objects(repository=repository, number=number, labelableType=issueType).\
        only("createdAt", "labelName").order_by("+createdAt")
    for event in labeledEvents:
        label = event["labelName"]
        # Check whether the label is removed
        unlabeled = UnlabeledEvent.objects(
            repository=repository, number=number, labelableType=issueType, createdAt__gte=event["createdAt"],
            labelName=label).count()
        # if the label is removed, continue to check the following labeled events
        if unlabeled > 0:
            continue
        # Check whether label is relevant to BugFixing, NewFeature, or Documentation
        label = label.lower()
        if "bug" in label:
            category = "BugReport"
        elif "feature" in label:
            category = "FeatureRequest"
        elif "documentation" in label:
            category = "Documentation"
        elif "question" in label:
            category = "Question"
        else:
            continue

    return category
