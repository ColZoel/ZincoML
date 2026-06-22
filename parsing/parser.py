import pandas as pd
import os
from utils.dirs import subdirectories, read_any
from spacy_llm.util import assemble
from utils.config import load_config, root, set_llm_examples, set_llm_labels
import Palmai
import spacy

unique_vars = load_config('main')['unique_vars']
llm_config = os.path.join(root, 'parsing', 'config.cfg')
set_llm_examples()
set_llm_labels()
nlp = assemble(llm_config)

# nlp = spacy.blank("en")
# config = {"task": {"@llm_tasks": "spacy.NER.v3", "labels": ["PERSON", "ORGANISATION", "LOCATION", "OCCUPATION", "ADDRESS"]},
#           "model": {"@llm_models": "spacy.PaLM.v1", "name": "chat-bison-001", "config": {"temperature":0.0}}}
# llm = nlp.add_pipe("llm", config=config)


def set_llm():
    set_llm_examples()
    set_llm_labels()
    model = assemble(llm_config)
    return model


def set_dict(tup):
    info = {}
    for n, i in enumerate(tup):
        if i[1] in info:
            info[i[1]] += [i[0]]
        else:
            info[i[1]] = [i[0]]
    return info


def fill_df(info_dict, personal_vars):
    """
    Fill missing values in dataframe. Personal variables are not filled. They are assumed to be unique to each person,
    e.g. position at employment, occupation, military branch while the address, phone, location, etc. are assumed to be
    shared by everyone on the household (entry)
    """
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in info_dict.items()]))
    for col in df.columns:
        df[col] = df[col].ffill() if col not in personal_vars else df[col]
        info_dict = df.to_dict()
    return info_dict


def parse(text):
    text = text.replace('\n', ' ')
    doc = nlp(text)
    results = [(ent.text, ent.label_) for ent in doc.ents]
    print(f'Text: {text}\nResults: {results}')
    info = set_dict(results)
    info_dict = fill_df(info, unique_vars)

    return info_dict


def palm(text):
    doc = nlp(text)
    p_doc = llm(doc)
    results = [(ent.text, ent.label_) for ent in p_doc.ents]
    return results


def parse_df(df):
    df2 = df["raw_string"].apply(parse)
    df2 = pd.DataFrame(df2.tolist())
    return df2


def save_parse(df, path, save_dir, parse_dir, output='csv'):

    filename = path.split('/')[-1].replace('.parquet', '_processed.feather')
    df.to_feather(os.path.join(parse_dir, filename))
    if output == 'csv':
        filename = path.split('/')[-1].replace('.parquet', '_processed.csv')
        df.to_csv(os.path.join(save_dir, filename), index=False)
    elif output == 'parquet':
        filename = path.split('/')[-1].replace('.parquet', '_processed.parquet')
        df.to_parquet(os.path.join(save_dir, filename), index=False)
    elif output == 'dta':
        filename = path.split('/')[-1].replace('.parquet', '_processed.dta')
        df.to_stata(os.path.join(save_dir, filename), write_index=False)
    elif output is None:
        pass
    else:
        raise ValueError("output must be one of 'csv', 'parquet', 'dta', or None")
    print(f'Finished. {filename} saved.')


def parse_image(path, year_city_type_path, output='csv'):
    """
    Parse an image and return a dataframe with the parsed information joined with the original dataframe
    :param path: path to image parquet file
    :param year_city_type_path: path to save directory
    :param output: output type, one of 'csv', 'parquet', or 'dta', or None. Always saves a feather. Default is 'csv'

    """
    save_dir = subdirectories(year_city_type_path)[0]
    parse_dir = subdirectories(year_city_type_path)[5]
    df = read_any(path)
    df = df.sample(1)
    df2 = parse_df(df)
    df2 = df2.join(df)
    save_parse(df2, path, save_dir, parse_dir, output=output)

    return


def combine_from_folder(path, year_city_type_path, output='csv'):
    """
    Parse all images in a folder and return a dataframe with the parsed information joined with the original dataframe
    :param path: path to folder of image parquet files
    :param year_city_type_path: path to save directory
    :param output: output type, one of 'csv', 'parquet', or 'dta', or None. Always saves a feather. Default is 'csv'

    """
    save_dir = subdirectories(year_city_type_path)[0]
    parse_dir = subdirectories(year_city_type_path)[5]
    df = pd.concat([pd.read_parquet(file) for file in os.listdir(path) if file.endswith('.parquet')])
    df2 = parse_df(df)
    df2 = df2.join(df)
    save_parse(df2, path, save_dir, parse_dir, output=output)

    return


# parse_image('/Users/collinzoeller/city_directories/AZ/test_out/debug/temp/2/1994_ROC_1__0188.parquet',
#             '/Users/collinzoeller/city_directories/AZ/test')
