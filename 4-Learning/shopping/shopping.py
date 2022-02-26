import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - (0)Administrative, an integer
        - (1)Administrative_Duration, a floating point number
        - (2)Informational, an integer
        - (3)Informational_Duration, a floating point number
        - (4)ProductRelated, an integer
        - (5)ProductRelated_Duration, a floating point number
        - (6)BounceRates, a floating point number
        - (7)ExitRates, a floating point number
        - (8)PageValues, a floating point number
        - (9)SpecialDay, a floating point number
        - (10)Month, an index from 0 (January) to 11 (December)
        - (11)OperatingSystems, an integer
        - (12)Browser, an integer
        - (13)Region, an integer
        - (14)TrafficType, an integer
        - (15)VisitorType, an integer 0 (not returning) or 1 (returning)
        - (16)Weekend, an integer 0 (if false) or 1 (if true)

    (17)labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    int_index = [0,2,4,11,12,13,14]
    flt_index = [1,3,5,6,7,8,9,]
    month_dict = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11
        }

    bol_index = [16,17]

    info = []
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:

            data = list(row)
            #print(data)

            #convert to int if index where specified
            for index in int_index:
                data[index] = int(data[index])

            #convert to flat where needed
            for index in flt_index:
                data[index] = float(data[index])

            #convert month to number
            data[10] = month_dict[data[10]]

            #convert returning to an inti
            if data[15] ==  "Returning_Visitor":
                data[15] = 1
            else:
                data[15] = 0

            #convert bool to int
            for index in bol_index:
                if data[index] == "TRUE":
                    data[index] = 1
                elif data[index] == "FALSE":
                    data[index] = 0


            info.append(data)

    #convert info into seperate lists
    labels = [row[17] for row in info]
    evidence = [row[0:17] for row in info]

    return(evidence,labels)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    neighbour_model = KNeighborsClassifier(n_neighbors=1)
    return neighbour_model.fit(evidence,labels)
    #raise NotImplementedError


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    pos_correct = 0
    neg_correct = 0

    true_positive = 0
    true_negative = 0
    for true, guess in zip(labels,predictions):
        #count if negative or positive value, then check if they were correct
        if true == 1:
            pos_correct+=1
            if true == guess:
                true_positive+=1
        else:
            neg_correct +=1
            if true == guess:
                true_negative+=1
    
    return (float(true_positive/pos_correct),float(true_negative/neg_correct))
    #raise NotImplementedError


if __name__ == "__main__":
    main()
