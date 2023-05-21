import pandas as pd


def predict_price(data: pd.DataFrame) -> pd.DataFrame:
    data.predicted_price = data.price
    return data
