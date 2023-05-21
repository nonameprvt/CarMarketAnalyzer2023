import json
import typing as tp

import pandas as pd


def predict_price(data: pd.DataFrame) -> pd.DataFrame:
    data.predicted_price = data.price
    return data


def convert_jsons_to_dataframe(jsons: tp.List[str]) -> pd.DataFrame:
    dicts = [json.loads(row) for row in jsons]
    return pd.DataFrame.from_records(dicts)


def convert_dataframe_to_jsons(df: pd.DataFrame) -> tp.List[str]:
    return [json.dumps(row.to_dict()) for _, row in df.iterrows()]
