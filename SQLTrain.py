import MySQLdb, nltk, SQL2, re

def entity_features(word):
    tokens= re.split(r'\W+', word)
    return {'length':len(tokens)}

def main():
    db= SQL2.IMDBSQL()
    names= db.getPeople(10000)
    movies= db.getMovies(10000)

    while len(names) < 1000 or len(movies) < 1000:
        names+= db.getPeople(1000)
        movies+= db.getMovies(1000)

    names= set(names)
    movies= set(movies)

    print "%d  %d" % (len(names), len(movies))

    entities= ([(name,'person') for name in names] + [(movie,'movie') for movie in
                                                     movies])
    import random

    random.shuffle(entities)

    featuresets= [(entity_features(e),t) for (e,t) in entities]
    train_set, test_set= featuresets[600:], featuresets[:600]
    classifier= nltk.NaiveBayesClassifier.train(train_set)

    print nltk.classify.accuracy(classifier, test_set)
    try:
        import cPickle as pickle
    except:
        import pickle

    fh= open('sqlclassifier.pkl', 'w')
    pickle.dump(classifier, fh)
    fh.close()

    fh= open('entity_features.pkl','w')
    pickle.dump(entity_features, fh)
    fh.close()


if __name__ == '__main__':
    main()
