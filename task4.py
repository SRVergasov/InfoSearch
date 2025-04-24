import os
import math
from collections import defaultdict, Counter

TOKENS_FOLDER = "tokens"
LEMMAS_FOLDER = "lemmas"
TFIDF_TOKENS_FOLDER = "tfidf_tokens"
TFIDF_LEMMAS_FOLDER = "tfidf_lemmas"

os.makedirs(TFIDF_TOKENS_FOLDER, exist_ok=True)
os.makedirs(TFIDF_LEMMAS_FOLDER, exist_ok=True)


def compute_token_tfidf():
    filenames = sorted([f for f in os.listdir(TOKENS_FOLDER) if f.endswith(".txt")])
    N = len(filenames)

    docs = {}
    df = defaultdict(int)
    for filename in filenames:
        doc_id = filename.replace(".txt", "").split("_")[-1]
        with open(os.path.join(TOKENS_FOLDER, filename), "r", encoding="utf-8") as f:
            terms = f.read().splitlines()
        term_counts = Counter(terms)
        docs[doc_id] = (term_counts, len(terms))
        for term in term_counts:
            df[term] += 1

    idf = {term: math.log(N / df[term]) for term in df}

    for doc_id, (term_counts, total_terms) in docs.items():
        lines = []
        for term, count in term_counts.items():
            tf = count / total_terms
            tfidf = tf * idf[term]
            lines.append(f"{term} {idf[term]:.6f} {tfidf:.6f}")
        with open(os.path.join(TFIDF_TOKENS_FOLDER, f"tfidf_{doc_id}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def compute_lemma_tfidf():
    filenames = sorted([f for f in os.listdir(LEMMAS_FOLDER) if f.endswith(".txt")])
    N = len(filenames)

    docs = {}
    df = defaultdict(int)

    for filename in filenames:
        doc_id = filename.replace(".txt", "").split("_")[-1]
        lemma_map = {}

        # Преобразуем форму → лемма
        with open(os.path.join(LEMMAS_FOLDER, filename), "r", encoding="utf-8") as f:
            for line in f:
                if ":" not in line:
                    continue
                lemma, forms_str = line.strip().split(":")
                lemma = lemma.strip()
                forms = [form.strip() for form in forms_str.split(",")]
                for form in forms:
                    lemma_map[form] = lemma
                # добавим и саму лемму на всякий случай
                lemma_map[lemma] = lemma

        # Считываем соответствующий tokens-файл
        token_file = f"tokens_{doc_id}.txt"
        with open(os.path.join(TOKENS_FOLDER, token_file), "r", encoding="utf-8") as f:
            tokens = f.read().splitlines()

        # Преобразуем токены в леммы
        lemma_list = [lemma_map.get(token, token) for token in tokens]
        lemma_counts = Counter(lemma_list)
        docs[doc_id] = (lemma_counts, len(lemma_list))
        for lemma in lemma_counts:
            df[lemma] += 1

    idf = {lemma: math.log(N / df[lemma]) for lemma in df}

    for doc_id, (lemma_counts, total_terms) in docs.items():
        lines = []
        for lemma, count in lemma_counts.items():
            tf = count / total_terms
            tfidf = tf * idf[lemma]
            lines.append(f"{lemma} {idf[lemma]:.6f} {tfidf:.6f}")
        with open(os.path.join(TFIDF_LEMMAS_FOLDER, f"tfidf_{doc_id}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


compute_token_tfidf()
compute_lemma_tfidf()
