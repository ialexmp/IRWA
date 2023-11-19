from math import ceil
import os
from json import JSONEncoder
import json
import pickle
import time

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument, Session_IP
from myapp.search.search_engine import SearchEngine
from myapp.search.algorithms import create_index
from wordcloud import WordCloud
import base64
from io import BytesIO

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.config['SESSION_COOKIE_NAME'] = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.
file_path = path + "/Rus_Ukr_war_data.json"

# file_path = "../../tweets-data-who.json"
corpus = load_corpus(file_path)
print("loaded corpus. first elem:", list(corpus.values())[0])

archivo_index_tf_idf = path + '/index_tf_idf.pkl'
archivo_tf = path + '/tf.pkl'
archivo_idf = path + '/idf.pkl'

if os.path.exists(archivo_index_tf_idf) and os.path.exists(archivo_tf) and os.path.exists(archivo_idf):
    with open(archivo_index_tf_idf, 'rb') as archivo:
        index_tf_idf = pickle.load(archivo)
    with open(archivo_tf, 'rb') as archivo:
        tf = pickle.load(archivo)
    with open(archivo_idf, 'rb') as archivo:
        idf = pickle.load(archivo)
else:
    index_tf_idf, tf, idf = create_index(corpus)
    with open(archivo_index_tf_idf, 'wb') as archivo:
        pickle.dump(index_tf_idf, archivo)
    with open(archivo_tf, 'wb') as archivo:
        pickle.dump(tf, archivo)
    with open(archivo_idf, 'wb') as archivo:
        pickle.dump(idf, archivo)

search_queries = []

try:
    with open("sessions.txt", 'r+') as archivo:
        actual_session = int(archivo.readline().strip())
        next_session = actual_session + 1
        archivo.seek(0)
        archivo.write(str(next_session) + "\n")
except FileNotFoundError:
    actual_session = 0
    next_session = actual_session
    with open("sessions.txt", 'w') as archivo:
        archivo.write(str(next_session) + "\n")
        
start_time = time.time()

val_session = actual_session
# Home URL "/"
@app.route('/')
def index():
    global val_session
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2023 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)
    
    if(val_session == actual_session):
        with open("sessions.txt", 'a') as archivo:
            archivo.write(user_ip + ";" + agent["platform"]["name"] + " " + agent["platform"]["version"] + ";" + agent["browser"]["name"] + '\n')
        
    val_session = val_session + 1    

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    search_queries.append(search_query)
    session['last_search_query'] = search_query
    
    search_id = analytics_data.save_query_terms(search_query)

    engine_used = request.form['search-option']
    results = search_engine.search(search_query, search_id, corpus, index_tf_idf, tf, idf, engine_used)
        
    found_count = len(results)
    session['last_found_count'] = found_count
    
    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    # store data in statistics table 1
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))
    
    tweet: Document = corpus[int(clicked_doc_id)]

    return render_template('doc_details.html', tweet=tweet)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    
    # Dashboard
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited=[]
    for doc in visited_docs:
        visited.append(doc.to_json())
    
    if (len(search_queries) != 0):
        queries = ' '.join(search_queries)
        wordcloud = WordCloud(background_color='white', colormap='viridis').generate(queries)
        word_cloud = wordcloud.to_image()
        buffered = BytesIO()
        word_cloud.save(buffered, format="PNG")
        word_cloud = base64.b64encode(buffered.getvalue()).decode()    
        return render_template('stats.html', clicks_data=docs, visited_docs=visited, wordcloud=word_cloud)
    else:
        return render_template('stats.html', clicks_data=docs, visited_docs=visited)
    


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited=[]
    for doc in visited_docs:
        visited.append(doc.to_json())
    return render_template('dashboard.html', visited_docs=visited)


@app.route('/sentiment')
def sentiment_form():
    docs = []

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    
    return render_template('sentiment.html', clicks_data=docs)


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    
    docs = []

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    
    return render_template('sentiment.html', score=score, clicks_data=docs)


@app.route('/session', methods=['GET'])
def session_function():
    user_agent = request.headers.get('User-Agent')
    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)
    user = Session_IP(user_ip, agent)
    time_now = time.time()
    total_time = time_now - start_time
    total_time = round(total_time / 60)
    
    sessions = []
    with open("sessions.txt", 'r') as archivo:
        all_session = archivo.readlines()
        if len(all_session) >= 2:
            sessions.append(all_session[-1].strip())
            for s in reversed(all_session[1:-1]):
                sessions.append(s.strip())

    print(sessions)
    
    frequency = {}
    for query in search_queries:
        frequency[query] = frequency.get(query, 0) + 1
    
    if (len(search_queries) != 0):
        queries = ' '.join(search_queries)
        wordcloud = WordCloud(background_color='white', colormap='viridis').generate(queries)
        word_cloud = wordcloud.to_image()
        buffered = BytesIO()
        word_cloud.save(buffered, format="PNG")
        word_cloud = base64.b64encode(buffered.getvalue()).decode()    
        return render_template('session.html', user=user, time=total_time, sessions=sessions, history=search_queries, frequency=frequency, wordcloud=word_cloud)
    else:
        return render_template('session.html', user=user, time=total_time, sessions=sessions, history=search_queries, frequency=frequency)

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
