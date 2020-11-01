import tweepy
from dotenv import load_dotenv
import os
import pandas as pd
import gensim
import numpy as np
import nltk
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from gensim import corpora, models


"""
Prepping dependencies
"""
load_dotenv()
nltk.download('wordnet')
np.random.seed(2020)
stemmer = SnowballStemmer("english")
stop_words = ['http']

"""
Getting twitter credentials from environment variables and instantiating a tweepy instance
"""

auth = tweepy.OAuthHandler(os.environ.get("consumer_key"), os.environ.get("consumer_secret"))
auth.set_access_token(os.environ.get("access_token"), os.environ.get("access_token_secret"))

api = tweepy.API(auth)

"""
Text preprocessing
"""

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3 and token not in stop_words and '@' not in token:
            result.append(lemmatize_stemming(token))
    return result

"""
Converting the news dataset to a pandas dataframe and omitting other info
"""

data = pd.read_json('News_Category_Dataset_v2.json', lines=True)
data['to_vec'] = data[['category', 'headline']].agg(' '.join, axis=1)
data.set_index('headline', drop=True, append=False, inplace=False, verify_integrity=False)
data['index'] = data.index
documents = data
print("Loaded into dataframe")

"""
pre process the news headlines to lemmatize and destem
"""

processed_docs = documents['to_vec'].map(preprocess)
print("Headlines preprocessing complete!")

"""
generate the corpus and the bag of words model and finally the lda model
"""

dictionary = gensim.corpora.Dictionary(processed_docs)
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
print("Bag or words corpus created")
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=40, id2word=dictionary, passes=2, workers=2)
print("Model building complete")

"""
Uses tweepy to get information about the twitter user
"""

def getTwitterInfo(username):
    return api.get_user(screen_name=username)

def getTwitterTimeline(username):
    topics = {}
    timeline = api.user_timeline(screen_name=username, count=100)
    tweets_for_csv = [tweet.text for tweet in timeline]
    # Traverse through the first 100 tweets
    for latest_tweet in tweets_for_csv:
        bow_vector = dictionary.doc2bow(preprocess(latest_tweet))
        for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
            topic = lda_model.print_topic(index, 5)
            if topic in topics:
                topics.update({topic: topics.get(topic) + score.item()})
            else:
                topics.update({topic: score.item()})
    sorted_topics = {k: v for k, v in sorted(topics.items(), key=lambda item: item[1], reverse=True)}
    return sorted_topics