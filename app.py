from flask import Flask, render_template, request
import os
import math
import json
import re

app = Flask(__name__)

TFIDF_DIR = 'tfidf_lemmas'
INDEX_FILE = 'inverted_index.json'

documents = {}
for filename in os.listdir(TFIDF_DIR):
    if filename.endswith('.txt'):
        doc_id = filename.replace('tfidf_', '').replace('.txt', '')
        tfidf_vector = {}
        with open(os.path.join(TFIDF_DIR, filename), 'r', encoding='utf-8') as f:
            for line in f:
                term, idf, tfidf = line.strip().split()
                tfidf_vector[term] = float(tfidf)
        documents[doc_id] = tfidf_vector

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

all_lemmas = set(inverted_index.keys())

def lemmatize_query_tokens(query):
    tokens = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', query.lower())
    matched_lemmas = []

    for token in tokens:
        for lemma in all_lemmas:
            if token == lemma or token in lemma:
                matched_lemmas.append(lemma)
                break
    return matched_lemmas

def compute_cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector.get(term, 0.0) * doc_vector.get(term, 0.0) for term in query_vector)
    query_norm = math.sqrt(sum(val ** 2 for val in query_vector.values()))
    doc_norm = math.sqrt(sum(val ** 2 for val in doc_vector.values()))
    if query_norm == 0 or doc_norm == 0:
        return 0.0
    return dot_product / (query_norm * doc_norm)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ''

    if request.method == 'POST':
        query = request.form['query'].lower().strip()
        query_lemmas = lemmatize_query_tokens(query)

        query_vector = {}
        for lemma in query_lemmas:
            for doc_id in inverted_index.get(lemma, []):
                if lemma in documents.get(doc_id, {}):
                    query_vector[lemma] = documents[doc_id][lemma]
                    break

        scores = []
        for doc_id, tfidf_vector in documents.items():
            similarity = compute_cosine_similarity(query_vector, tfidf_vector)
            if similarity > 0:
                scores.append((doc_id, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = scores[:10]

    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
