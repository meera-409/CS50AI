import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    full_path = os.path.join(os.getcwd(),directory)
    file_dict = {}
    for file in os.listdir(full_path):
        if file.endswith(".txt"):

            with open(os.path.join(full_path,file), encoding="utf8") as f:
                text = f.read()
                file_dict[file]=text
                f.close()

    return file_dict



def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    text = nltk.word_tokenize(document.lower())
    stop_words = set(nltk.corpus.stopwords.words('english'))
    final_words = []
    for word in text:
        if word not in stop_words and word not in string.punctuation:
            final_words.append(word)

    return final_words



def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    no_docs = len(documents)
    
    word_idfs = dict()
    for file in documents:
        for word in documents[file]:
            
            if word not in word_idfs:
                count = 0
                for check_file in documents:
                    if word in documents[check_file]:
                        count+= 1
                word_idfs[word]=count

    for word in word_idfs:
        word_idfs[word] = math.log(no_docs/word_idfs[word])
    return word_idfs



def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = dict()
    for text in files:
        contents = files[text]
        tfidf = 0
        for word in query:
            tfidf += contents.count(word)*idfs[word]

        tfidfs[text]=tfidf


    sorted_results = sorted(tfidfs.items(), key=lambda tfidfs: tfidfs[1], reverse=True)

    sorted_files = []
    for result in sorted_results:
        sorted_files.append(result[0])

    return sorted_files[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    result = dict()
    for sentence in sentences:
        sentence_list = sentences[sentence]
        sentence_idf = 0
        sentence_density = 0
        for word in query:
            if word in sentence_list:
                sentence_idf += idfs[word]
                sentence_density += sentence_list.count(word)
        sentence_density = sentence_density/len(sentence_list)
        result[sentence] = [sentence_idf, sentence_density]

    sorted_result = sorted(result.items(), key=lambda e: (e[1][0],e[1][1]), reverse = True)

    sorted_files = []
    for result in sorted_result:
        sorted_files.append(result[0])

    return sorted_files[:n]



if __name__ == "__main__":
    main()
