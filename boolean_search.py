import json
import re
from collections import deque


def eval_term(term):
    return index.get(term, set())


def eval_expr(expr):
    if isinstance(expr, str):
        return eval_term(expr)
    op = expr[0]
    if op == "NOT":
        return all_docs - eval_expr(expr[1])
    elif op == "AND":
        return eval_expr(expr[1]) & eval_expr(expr[2])
    elif op == "OR":
        return eval_expr(expr[1]) | eval_expr(expr[2])


def parse_query(query):
    tokens = deque(re.findall(r'\(|\)|AND|OR|NOT|[а-яА-ЯёЁa-zA-Z0-9_]+', query))

    def parse_factor():
        token = tokens.popleft()
        if token == '(':
            expr = parse_or()
            return expr
        elif token == "NOT":
            operand = parse_factor()
            return ["NOT", operand]
        elif token not in {"AND", "OR", ")", "("}:
            return token

    def parse_and():
        left = parse_factor()
        while tokens and tokens[0] == "AND":
            tokens.popleft()
            right = parse_factor()
            left = ["AND", left, right]
        return left

    def parse_or():
        left = parse_and()
        while tokens and tokens[0] == "OR":
            tokens.popleft()
            right = parse_and()
            left = ["OR", left, right]
        return left

    return parse_or()


if __name__ == '__main__':
    with open("inverted_index.json", "r", encoding="utf-8") as f:
        index = json.load(f)
        index = {k: set(v) for k, v in index.items()}

    all_docs = set()
    for docs in index.values():
        all_docs.update(docs)

    query = input(">>> ")
    while query != "exit":
        try:
            expr_tree = parse_query(query)
            result = eval_expr(expr_tree)
            print("Документы:", sorted(result))
            query = input(">>> ")
        except Exception as e:
            print("Ошибка в запросе:", e)
