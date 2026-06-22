"""
Call the PalmAI API to get the parsed text given the examples and observation text
"""
from utils.config import palm_key
import google.generativeai as palm
import os
import yaml

palm.configure(api_key=palm_key)

def parse_examples():
    examples_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples.yaml')
    with open(examples_path, 'r') as f:
        examples = yaml.safe_load(f)
        example = ""
        for line in examples:
            paragraph = "\n\nParagraph: " + line['text'] + "\nAnswer:"
            entity = ""
            for i, ent in enumerate(line['spans']):
                entity += f"\n{i+1}. {ent['text']} | {ent['label']} | {ent['is_entity']} | {ent['reason']}"
            example += paragraph + entity
    return example


def set_prompt(example, entry):
    """
    Calls the PalmAI API to get the parsed text given the examples and observation text
    """
    prompt = (f'You are an expert Named Entity Recognition (NER) system.'
              f'\nYour task is to accept Text as input and extract named entities.'
              f'\nEntities must have one of the following labels: '
              f'ADDRESS, MILITARY BRANCH, OCCUPATION, ORGANIZATION, PERSON, POSITION, TELEPHONE.'
              f'\nIf a span is not an entity label it: `==NONE==`.'
              f'\n\n\nEntities are names, places, employment and contact information, '
              f'and other information associated with the people mentioned in the directory, '
              f'as well as associated identifiers such as Mrs. or Jr.'
              f'\nAdjectives are part of an entity. Verbs are part of an entity. '
              f'Adverbs are part of an entity.'
              f'\nBelow are definitions of each label to help aid you in what kinds of named '
              f'entities to extract for each label.\nAssume these definitions are written by an '
              f'expert and follow them closely.\nperson: first and last name of a person,'
              f' which can include titles such as Mr., Mrs., or Jr. or a leading quotation "'
              f'\norganization: name of an organization or business and can include a leading quotation '
              f'"\naddress: street address as well as any state, city, zip or other location information'
              f'\nposition: title of the job held by the person, e.g., President, Vice President, Manager, etc.'
              f'\noccupation: type of job held by the person, usually the industry or field of work'
              f'\ntelephone: phone number of the person'
              f'\nmilitary branch: branch of the military the person was in, if any. e.g., USA, USMC, USN, USCG, USAF'
              f'\n\nQ: Given the paragraph below, identify a list of entities, '
              f'and for each entry explain why it is or is not an entity:{example}'
              f'\n\nParagraph: {entry}\n\n\nAnswer:'
              f'')
    return prompt


def parse_response(response):
    lines = response.split('\n').split('.')[1]
    ents = []
    for line in lines:
        elements = line.split('|')
        if elements[2] == 'True':
            ents += [(elements[0], elements[1])]
    return ents


def call(entry):

    prompt_txt = set_prompt(example, entry)
    prompt = palm.generate_text(
        model='models/text-bison-001',
        prompt=prompt_txt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=1500
    )
    db = prompt.result
    return prompt.result


example = parse_examples()
