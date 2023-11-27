
from build_nlp import load_llm
import pandas as pd
import os
# Path: parsing/parse.py

model = load_llm("parsing/llm")


def set_dict(tup):
    info = {}
    for n, i in enumerate(tup):
        if i[1] in info:
            info[i[1]] += [i[0]]
        else:
            info[i[1]] = [i[0]]
    return info


def fill_df(info_dict, personal_vars):
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in info_dict.items()]))
    for col in df.columns:
        df[col] = df[col].ffill() if col not in personal_vars else df[col]
        info_dict = df.to_dict()
    return info_dict


def parse(text):
    doc = model(text)
    results = [(ent.text, ent.label_) for ent in doc.ents]
    info = set_dict(results)
    info_dict = fill_df(info, ["POSITION", "OCCUPATION", "MILITARY BRANCH"])

    return info_dict


def parse_df(df):
    df2 = df["raw_ocr"].apply(parse)
    df2 = pd.DataFrame(df2.tolist())
    return df2


def parse_image(path, save_dir, output='csv'):
    """
    Parse an image and return a dataframe with the parsed information joined with the original dataframe
    :param path: path to image parquet file
    :param output: output type, one of 'csv', 'parquet', or 'dta', or None. Always saves a feather. Default is 'csv'

    """
    df = pd.read_parquet(path)
    df2 = parse_df(df)
    df2 = df2.join(df)

    filename = path.split('/')[-1].replace('.parquet', '_processed.feather')
    df2.to_feather(os.path.join(save_dir, filename))
    if output == 'csv':
        filename = path.split('/')[-1].replace('.parquet', '_processed.csv')
        df2.to_csv(os.path.join(save_dir, filename), index=False)
    elif output == 'parquet':
        filename = path.split('/')[-1].replace('.parquet', '_processed.parquet')
        df2.to_parquet(os.path.join(save_dir, filename), index=False)
    elif output == 'dta':
        filename = path.split('/')[-1].replace('.parquet', '_processed.dta')
        df2.to_stata(os.path.join(save_dir, filename), write_index=False)
    elif output is None:
        pass
    else:
        raise ValueError("output must be one of 'csv', 'parquet', 'dta', or None")

    return

