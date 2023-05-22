import math

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    bad_cols = [col for col in data.columns if (data[col] == 'Ошибка').sum() > len(data) / 2]
    data.drop(columns=bad_cols, inplace=True)
    data.model_name = data.model_name.fillna('Ошибка')
    data.brand_name = data.brand_name.fillna('Ошибка')
    data.is_bitten = data.is_bitten.astype(int)
    return data


def make_features_linear(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['year_lin'] = data.year * (data.year >= 2000)
    borders = [-math.inf] + list(range(1920, 2001, 5)) + [math.inf]
    for i in range(1, len(borders)):
        data[f'year_range_{i}'] = ((borders[i - 1] <= data.year) & (data.year < borders[i])).astype(int)

    data['small_mileage'] = (data.mileage < 50000).astype(int)
    data['large_mileage'] = 1 - data.small_mileage
    return data


def get_column_transformer(sparse_threshold: float = 0.3) -> ColumnTransformer:
    categorical = ['engine', 'body_type', 'fuel_type', 'transmission', 'seller_type', 'brand_name', 'model_name']
    numeric = ['mileage', 'horse_power', 'year']
    passthrough = ['is_bitten']

    return ColumnTransformer([
        ('scaling', StandardScaler(), numeric),
        ('ohe', OneHotEncoder(handle_unknown='ignore'), categorical),
        ('passthrough', 'passthrough', passthrough)
    ], sparse_threshold=sparse_threshold)


def get_column_transformer_for_linear_features(data: pd.DataFrame, sparse_threshold: float = 0.3):
    categorical = ['engine', 'body_type', 'fuel_type', 'transmission', 'seller_type', 'brand_name', 'model_name']
    numeric = ['horse_power', 'year_lin']
    passthrough = [col for col in data.columns if ((data[col] == 0) | (data[col] == 1)).all()]

    return ColumnTransformer([
        ('scaling', StandardScaler(), numeric),
        ('ohe', OneHotEncoder(handle_unknown='ignore'), categorical),
        ('passthrough', 'passthrough', passthrough)
    ], sparse_threshold=sparse_threshold)
