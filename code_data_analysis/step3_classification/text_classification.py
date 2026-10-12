"""
Text classifier shared by Step 3 (output categories and input-issue labels).
"""

import nltk
import numpy
import pandas
import xgboost
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn import linear_model
from sklearn import metrics
from sklearn import model_selection
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from statistics import multimode


ps = PorterStemmer()


def text_classification(x, y):

    # 1. Split the trainDF into train and valid datasets
    train_x, valid_x, train_y, valid_y = model_selection.train_test_split(x, y)
    # label encode the target variable
    encoder = preprocessing.LabelEncoder()
    train_y = encoder.fit_transform(train_y)
    valid_y = encoder.fit_transform(valid_y)

    # 2. Engineer the features
    count_vect, xtrain_count, xvalid_count, tfidf_vect, xtrain_tfidf, xvalid_tfidf = engineer_features(
        train_x=train_x, valid_x=valid_x
    )

    # 3. Build Models

    print("************************************")
    print("Use all text, including the mergedCommitMessage, title, and body")

    # Linear Classifier
    """
    Logistic regression measures the relationship between the categorical dependent variable and one or more 
    independent variables by estimating probabilities using a logistic/sigmoid function. One can read more about 
    logistic regression here: https://www.analyticsvidhya.com/blog/2015/10/basics-logistic-regression/
    """

    # Linear Classifier on Count Vectors
    lr_count, pred_lrC, accuracy, precision = train_model(
        linear_model.LogisticRegression(), xtrain_count, train_y, xvalid_count, valid_y)
    print("LR, Count Vectors: ", accuracy, precision)

    # Linear Classifier on Word Level TF IDF Vectors
    lr_tfidf, pred_lrT, accuracy, precision = train_model(
        linear_model.LogisticRegression(), xtrain_tfidf, train_y, xvalid_tfidf, valid_y)
    print("LR, WordLevel TF-IDF: ", accuracy, precision)

    # Boosting model
    """
    Boosting models are another type of ensemble models part of tree based models. Boosting is a machine learning ensemble 
    meta-algorithm for primarily reducing bias, and also variance in supervised learning, and a family of machine learning 
    algorithms that convert weak learners to strong ones. A weak learner is defined to be a classifier that is only slightly 
    correlated with the true classification (it can label examples better than random guessing). 
    Read more about these models here: https://www.analyticsvidhya.com/blog/2016/01/xgboost-algorithm-easy-steps/
    """

    # Extereme Gradient Boosting on Count Vectors
    xgb_count, pred_xgbC, accuracy, precision = train_model(
        xgboost.XGBClassifier(), xtrain_count.tocsc(), train_y, xvalid_count.tocsc(), valid_y)
    print("Xgb, Count Vectors: ", accuracy, precision)

    # Extereme Gradient Boosting on Word Level TF IDF Vectors
    xgb_tfidf, pred_xgbT, accuracy, precision = train_model(
        xgboost.XGBClassifier(), xtrain_tfidf.tocsc(), train_y, xvalid_tfidf.tocsc(), valid_y)
    print("Xgb, WordLevel TF-IDF: ", accuracy, precision)

    # 4. Max voting of ensemble learning

    # get the index of the best classifier for labeling
    best = input("Enter the index of the best classifier for labeling: ")
    best = int(best)  # Index count from 0, i.e., from 0 to (len - 1)

    pred_array = [
        pred_lrC, pred_lrT, pred_xgbC, pred_xgbT,
    ]
    final_pred = get_final_pred_by_maxVoting(pred_array=pred_array, best_pred=pred_array[best])
    accuracy = metrics.accuracy_score(final_pred, valid_y)
    precision = metrics.precision_score(y_true=valid_y, y_pred=final_pred, average='weighted')
    print("\n-----------------------------------------------------")
    print("Max Voting 20 models", accuracy, precision)

    valid_y = encoder.inverse_transform(valid_y)
    final_pred = encoder.inverse_transform(final_pred)
    report = metrics.classification_report(y_true=valid_y, y_pred=final_pred)
    print(report)
    print("""
EXPLANATIONS
--> tp: true positives, fp: false positives, tn: true negatives, fn: false negatives
--> The precision is the ratio tp / (tp + fp), which intuitively is the ability of the classifier 
    not to label as positive a sample that is negative.
--> The recall is the ratio tp / (tp + fn), which intuitively is the ability of the classifier to 
    find all the positive samples.
--> The F-beta score can be interpreted as a weighted harmonic mean of the precision and recall, 
    where a F-beta score reaches its best value at 1 and worst score at 0.
--> macro avg: averaging the unweigthed mean per label
--> weighted average: averaging the support-weighted mean per label
    """)
    print("-----------------------------------------------------\n")

    # 5. Collect trained classifiers and the corresponding fitted feature vectors for prediction

    classifiers = [
        lr_count, lr_tfidf, xgb_count, xgb_tfidf
    ]
    feature_vectors = [
        count_vect, tfidf_vect, count_vect, tfidf_vect
    ]

    return encoder, best, list(classifiers), list(feature_vectors)


def get_final_pred_by_maxVoting(pred_array, best_pred):
    final_pred = numpy.array([], dtype='i')

    length = len(pred_array[0])

    x = 0
    for i in range(0, length):
        # Get an array of all predicts
        values = []
        for p in pred_array:
            values.append(p[i])

        modes = multimode(values)

        # If more than one mode, take the value of the best model
        if len(modes) == 1:
            pred = modes[0]
        else:
            pred = best_pred[i]
            x = x + 1

        final_pred = numpy.append(final_pred, pred)

    print("{} items have equal votes".format(str(x)))
    return final_pred


def engineer_features(train_x, valid_x):
    """
    Return the engineered count vectors and word-level-TF-IDF vectors
    :param train_x: The column of text for train dataset
    :param valid_x: The column of text for valid dataset
    :return: return the count vectors and tf-idf vectors of the three datasets
                xtrain_count, xvalid_count, xpredict_count, xtrain_tfidf, xvalid_tfidf, xpredict_tfidf
    """

    df = pandas.concat([train_x, valid_x])

    # Count Vectors
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')  # tokenize only words of 1+ chars

    # Use mergedCommitMessage as the focal text, this message seem to have some unexpected character

    # count_vect.fit(df.values.astype('U'))  # Even astype(str) would work
    # xtrain_count = count_vect.transform(train_x.values.astype('U'))
    # xvalid_count = count_vect.transform(valid_x.values.astype('U'))

    count_vect.fit(df)
    xtrain_count = count_vect.transform(train_x)
    xvalid_count = count_vect.transform(valid_x)

    # TF-IDF Vectors

    # word level tf-idf
    tfidf_vect = TfidfVectorizer(analyzer='word',
                                 token_pattern=r'\w{1,}',  # tokenize only words of 1+ chars
                                 max_features=5000)

    # tfidf_vect.fit(df.values.astype('U'))
    # xtrain_tfidf = tfidf_vect.transform(train_x.values.astype('U'))
    # xvalid_tfidf = tfidf_vect.transform(valid_x.values.astype('U'))

    tfidf_vect.fit(df)
    xtrain_tfidf = tfidf_vect.transform(train_x)
    xvalid_tfidf = tfidf_vect.transform(valid_x)

    return count_vect, xtrain_count, xvalid_count, tfidf_vect, xtrain_tfidf, xvalid_tfidf


# Child function of explore_text_classifiers(trainDF)
# define a utility function which can be used to train a model
def train_model(classifier, feature_vector_train, train_y, feature_vector_valid, valid_y, is_neural_net=False):
    """
    Return accuracy of the classifier by predicting the label of the valid dataset
    :param classifier: The model that is built
    :param feature_vector_train: Feature vector of the texts in the train dataset
    :param train_y: Encoded label vector in the train dataset
    :param feature_vector_valid:  Feature vector of the texts in the valid dataset to be predicted
    :param valid_y: Encoded label vector in the valid dataset
    :param is_neural_net: Whether the classifier is based on neural network
    :return:
    """
    # fit the training dataset on the classifier
    classifier.fit(feature_vector_train, train_y)

    # predict the labels on validation dataset
    predictions = classifier.predict(feature_vector_valid)

    if is_neural_net:
        predictions = predictions.argmax(axis=-1)

    accuracy = metrics.accuracy_score(predictions, valid_y)
    precision = metrics.precision_score(y_true=valid_y, y_pred=predictions, average='weighted')

    return classifier, predictions, accuracy, precision


def clean_doc(doc):
    if not doc:
        return None
    # convert to lowercase
    doc_lower = doc.lower()

    # # remove punctuation marks
    # table = str.maketrans(dict.fromkeys(string.punctuation))
    # doc_no_punctuation = doc_lower.translate(table)
    # tokenize the doc

    tokens = nltk.word_tokenize(doc_lower)

    # # remove words that are not coded in alphabet or numbers
    # new_tokens = []
    # for w in tokens:
    #     if w.isalnum():
    #         new_tokens.append(w)

    # remove stopwords
    doc_filtered = [w for w in tokens if w not in stopwords.words("english")]

    # stem the tokens
    doc_stemmed = [ps.stem(w) for w in doc_filtered]

    # organize the token into a new text
    doc_new = ""
    for w in doc_stemmed:
        doc_new = doc_new + w + ' '

    return doc_new
