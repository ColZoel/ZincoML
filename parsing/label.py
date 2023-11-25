
from build_nlp import load_llm
# Path: parsing/parse.py

model = load_llm("parsing/llm")


def parse(text):
    results = model(text)
    info = {}
    for result in results:
        info[result[-1]] = result[0]  # todo: make the persona unit of observation so there is 1 dict per person
