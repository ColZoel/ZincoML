import pandas as pd
import os
from utils.dirs import subdirectories, read_any
from spacy_llm.util import assemble
from utils.config import load_config, llm_config, llm_examples, set_llm_examples

unique_vars = load_config('main')['unique_vars']
set_llm_examples(llm_config, llm_examples)
model = assemble(llm_config)


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
    doc = model(text)
    results = [(ent.text, ent.label_) for ent in doc.ents]
    info = set_dict(results)
    info_dict = fill_df(info, unique_vars)

    return info_dict


def parse_df(df):
    df2 = df["raw_ocr"].apply(parse)
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
    unique_vars = load_config('main')['unique_vars']
    model = assemble("config.cfg")
    save_dir = subdirectories(year_city_type_path)[0]
    parse_dir = subdirectories(year_city_type_path)[5]
    df = read_any(path)
    df2 = parse_df(df, model, unique_vars)
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
