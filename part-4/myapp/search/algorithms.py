import numpy as np
import collections
from collections import defaultdict
from array import array
import math
from numpy import linalg as la
from myapp.search.objects import ResultItem, Document
import re
import nltk
from nltk.corpus import stopwords

stemmer = nltk.stem.SnowballStemmer('english')
custom_stopwords = set(stopwords.words('english'))

def search_in_corpus(corpus: dict, query, index, tf, idf):
    # 1. create create_tfidf_index
    # DONE IN WEB_APP FOR FASTER EXECUTION

    # 2. apply ranking
    ranked_tweets = search_tf_idf(query, index, tf, idf)
    
    print(ranked_tweets[:10], "\n\n\n")
    
    return ranked_tweets

def create_index(corpus):
    num_tweets = len(corpus)
    index = defaultdict(list)
    tf = defaultdict(list)
    df = defaultdict(int)
    idf = defaultdict(float)
    for doc_id, row in corpus.items():
        full_tweet = preprocess(row.description)
        tweet_index = {}
        for position, tweet in enumerate(full_tweet.split(" ")):
            try:
                tweet_index[tweet][1].append(position)
            except:
                tweet_index[tweet]=[doc_id, array('I',[position])]            
        norm = 0
        for tweet, posting in tweet_index.items():
            norm += len(posting[1]) ** 2
        norm = math.sqrt(norm)
        for tweet, posting in tweet_index.items():
            tf[tweet].append(np.round(len(posting[1])/norm,4))
            df[tweet] += 1
        for doc, position in tweet_index.items():
            index[doc].append(position)
        # Compute IDF:
        for term in df:
            idf[term] = np.round(np.log(float(num_tweets/df[term])), 4)
    return index, tf, idf

def search_tf_idf(query, index, tf, idf):
    query = preprocess(query)
    tweets = set()
    for each_query in query.split(" "):
        try:
            query_tweet=[posting[0] for posting in index[each_query]]
            tweets = tweets.union(query_tweet)
        except:
            pass
    tweets = list(tweets)
    ranked_tweets = rank_tweets(query, tweets, index, idf, tf)
    return ranked_tweets

def rank_tweets(terms, tweets, ourindex, idf, tf):
    terms = terms.split(" ")
    tweet_vectors = defaultdict(lambda: [0] * len(terms))
    query_vector = [0] * len(terms)
    query_terms_count = collections.Counter(terms)
    query_norm = la.norm(list(query_terms_count.values()))
    for termIndex, term_i in enumerate(terms):
        if term_i not in ourindex:
            continue
        query_vector[termIndex] = query_terms_count[term_i] / query_norm * idf[term_i]
        for row_tweet, (tweet, postings) in enumerate(ourindex[term_i]):
            if tweet in tweets:
                tweet_vectors[tweet][termIndex] = tf[term_i][row_tweet] * idf[term_i]
    tweet_scores=[[np.dot(curTweetVec, query_vector), tweet] for tweet, curTweetVec in tweet_vectors.items() ]
    tweet_scores.sort(reverse=True)
    result_tweets = [x[1] for x in tweet_scores]
    if len(result_tweets) == 0:
        print("No results found, try again")
    return tweet_scores

def preprocess(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove newline characters
    text = text.replace('\\n', '')
    # Remove extra whitespaces
    text = ' '.join(text.split())
    # Delete URLs on the tweet because we won't be able to access to them
    text = re.sub(r'\S*https?:\S*', '', text)
    # Remove spaces at first and at the end of a message
    text.strip()
    # Remove punctuation
    text = re.sub(r'[^a-z0-9 ]+', '', text)
    # Tokenize the text
    words = text.split()
    # Remove stopwords and apply stemming
    processed_words = [stemmer.stem(word) for word in words if word not in custom_stopwords]
    return ' '.join(processed_words)