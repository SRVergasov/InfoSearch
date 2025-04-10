import os
import json

LEMMAS_FOLDER = "lemmas"
INDEX_FILE = "inverted_index.json"


def build_index():
    index = {}

    for filename in os.listdir(LEMMAS_FOLDER):
        if filename.endswith(".txt"):
            doc_id = filename.replace(".txt", "")
            doc_id = doc_id.replace("lemmas_", "")
            filepath = os.path.join(LEMMAS_FOLDER, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    lemma, _ = line.split(":", 1)
                    lemma = lemma.strip()
                    index.setdefault(lemma, set()).add(doc_id)

    index_serializable = {k: sorted(list(v)) for k, v in index.items()}

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_serializable, f, ensure_ascii=False, indent=2)

    print(f"Индекс построен и сохранён в {INDEX_FILE}")


if __name__ == "__main__":
    build_index()
