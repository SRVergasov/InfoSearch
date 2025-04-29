import os
import math
from collections import defaultdict

TFIDF_FOLDER = "tfidf_lemmas"
TOP_K = 10


def load_tfidf_vectors():
    doc_vectors = {}
    idf_values = {}
    for filename in os.listdir(TFIDF_FOLDER):
        if not filename.endswith(".txt"):
            continue
        doc_id = filename.replace("tfidf_", "").replace(".txt", "")
        vector = {}
        with open(os.path.join(TFIDF_FOLDER, filename), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                term, idf, tfidf = parts
                idf = float(idf)
                tfidf = float(tfidf)
                vector[term] = tfidf
                idf_values[term] = idf  # idf одинаков для всех документов
        doc_vectors[doc_id] = vector
    return doc_vectors, idf_values


def vectorize_query(query_terms, idf_values):
    tf = defaultdict(int)
    for term in query_terms:
        tf[term] += 1
    total_terms = sum(tf.values())
    query_vector = {}
    for term, count in tf.items():
        tf_rel = count / total_terms
        idf = idf_values.get(term, math.log(1 + len(doc_vectors)))  # Fallback idf
        query_vector[term] = tf_rel * idf
    return query_vector


def cosine_similarity(vec1, vec2):
    common_terms = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum(vec1[t] * vec2[t] for t in common_terms)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def search_loop():
    while True:
        query = input("Введите запрос (или 'exit'): ").strip()
        if query.lower() == "exit":
            break
        query_terms = query.lower().split()
        query_vector = vectorize_query(query_terms, idf_values)
        results = []
        for doc_id, doc_vector in doc_vectors.items():
            score = cosine_similarity(query_vector, doc_vector)
            if score > 0:
                results.append((doc_id, score))
        results.sort(key=lambda x: x[1], reverse=True)
        for doc_id, score in results[:TOP_K]:
            print("Результаты:")
            print(f"Документ {doc_id} — релевантность: {score:.4f}")
        if not results:
            print("Ничего не найдено.")


doc_vectors, idf_values = load_tfidf_vectors()
search_loop()
