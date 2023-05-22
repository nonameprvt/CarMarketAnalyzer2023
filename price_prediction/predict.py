import json
import os
import typing as tp

import pandas as pd
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor

from price_prediction.preprocess import preprocess


def predict_price(data_: pd.DataFrame) -> pd.DataFrame:
    pretrained_dir = os.path.dirname(__file__) + '/pretrained'
    data = preprocess(data_)

    with open(pretrained_dir + '/col_t.pkl', 'rb') as f:
        col_t: ColumnTransformer = pickle.load(f)

    with open(pretrained_dir + '/random_forest.pkl', 'rb') as f:
        forest: RandomForestRegressor = pickle.load(f)

    price = forest.predict(col_t.transform(data))

    data = data_.copy()
    data.predicted_price = price
    return data


def convert_jsons_to_dataframe(jsons: tp.List[str]) -> pd.DataFrame:
    dicts = [json.loads(row) for row in jsons]
    return pd.DataFrame.from_records(dicts)


def convert_dataframe_to_jsons(df: pd.DataFrame) -> tp.List[str]:
    return [json.dumps(row.to_dict()) for _, row in df.iterrows()]
