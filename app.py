from flask import Flask, render_template, request
import os
import math

app = Flask(__name__)
TFIDF_DIR = 'tfidf_lemmas'

documents = {}

for filename in os.listdir(TFIDF_DIR):
    if filename.endswith('.txt'):
        doc_id = filename.replace('tfidf_', '').replace('.txt', '')
        terms = {}
        with open(os.path.join(TFIDF_DIR, filename), 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    term, idf, tfidf = parts
                    terms[term] = float(tfidf)
        documents[doc_id] = terms

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
        query_terms = query.split()

        query_vector = {}
        for term in query_terms:
            for doc in documents.values():
                if term in doc:
                    query_vector[term] = doc[term]
                    break

        scores = []
        for doc_id, tfidf_vector in documents.items():
            sim = compute_cosine_similarity(query_vector, tfidf_vector)
            if sim > 0:
                scores.append((doc_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = scores[:10]

    return render_template('index.html', results=results, query=query)


if __name__ == '__main__':
    app.run(debug=True)
