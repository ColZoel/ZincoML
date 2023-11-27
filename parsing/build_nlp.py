"""
Use pretrained LLM from Spacy and Palm AI to extract text
"""
import spacy
from spacy_llm.util import assemble
from os import getenv
import os
from dotenv import load_dotenv
load_dotenv()
palm_key = getenv("PALM_API_KEY")


def build_new_llm(name):
    nlp = assemble("config.cfg")
    nlp.to_disk(os.path.join("parsing", name))
    return nlp


def load_llm(path):
    if not os.path.exists(path):
        return build_new_llm(path.split("/")[-1])
    return spacy.load(path)


# Could it be possible to use the LLM integration with pandas AI to parse the text in a series?
