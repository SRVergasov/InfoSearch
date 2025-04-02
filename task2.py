import os
import re
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import pymorphy3

DATA_FOLDER = "data"
morph = pymorphy3.MorphAnalyzer()

nltk.download("stopwords")
russian_stopwords = set(stopwords.words("russian"))

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

def tokenize_text(text):
    words = re.findall(r'\b[а-яА-ЯёЁ]{2,}\b', text.lower())
    tokens = set(words) - russian_stopwords
    return tokens

for i in range(1, 101):
    tokens_file = "tokens/tokens_{}.txt".format(i)
    lemmas_file = "lemmas/lemmas_{}.txt".format(i)
    all_tokens = set()
    lemma_dict = {}

    file_path = os.path.join(DATA_FOLDER, f"{i}.txt")
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден, пропускаем.")
        continue

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
        text = extract_text_from_html(html_content)
        tokens = tokenize_text(text)
        all_tokens.update(tokens)

    with open(tokens_file, "w", encoding="utf-8") as out_file:
        for token in sorted(all_tokens):
            out_file.write(token + "\n")

    for token in all_tokens:
        lemma = morph.parse(token)[0].normal_form
        if lemma not in lemma_dict:
            lemma_dict[lemma] = set()
        lemma_dict[lemma].add(token)

    with open(lemmas_file, "w", encoding="utf-8") as out_file:
        for lemma, tokens in sorted(lemma_dict.items()):
            out_file.write(f"{lemma}: {', '.join(sorted(tokens))}\n")
