import math
import typing as tp

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import torch
from torch.utils.data import DataLoader

from price_prediction.dataset import CarsDataset
from price_prediction.models import LSTMModel, AttentionModel
from price_prediction.preprocess import preprocess, make_features_linear, get_column_transformer_for_linear_features
from price_prediction.train import train

device = torch.device(
    'cuda:0' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu'))


def get_loaders(data: pd.DataFrame,
                model_type: str = 'bpe', vocab_size: int = 2000,
                batch_size=256) -> tp.Tuple[DataLoader, DataLoader]:
    data = make_features_linear(preprocess(data))

    data_train, data_val, y_train, y_val = train_test_split(data, data.price.values, test_size=0.2, random_state=42)

    column_transformer = get_column_transformer_for_linear_features(data, sparse_threshold=0.0)

    features_train = column_transformer.fit_transform(data_train)
    features_val = column_transformer.transform(data_val)

    sp_model = model_type + str(vocab_size)
    train_dataset = CarsDataset(features_train, data_train.description, y_train, train=True,
                                sp_model_prefix=sp_model, model_type=model_type, vocab_size=vocab_size)
    val_dataset = CarsDataset(features_val, data_val.description, y_val, train=False,
                              sp_model_prefix=sp_model, model_type=model_type, vocab_size=vocab_size,
                              max_length=train_dataset.max_length)

    return DataLoader(train_dataset, batch_size, shuffle=True), DataLoader(val_dataset, batch_size, shuffle=False)


def train_lstm(data: pd.DataFrame) -> tp.Tuple[tp.List[float], tp.List[float], tp.List[float], tp.List[float]]:
    train_loader, val_loader = get_loaders(data)
    model = LSTMModel(train_loader.dataset, num_layers=3).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[10, 15], gamma=0.1)
    res = train(model, optimizer, scheduler, train_loader, val_loader, 20)
    torch.save(model.state_dict(), 'lstm')
    return res


def train_transformer(data: pd.DataFrame) -> tp.Tuple[tp.List[float], tp.List[float], tp.List[float], tp.List[float]]:
    train_loader, val_loader = get_loaders(data)
    model = AttentionModel(train_loader.dataset).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4, betas=(0.9, 0.98))
    res = train(model, optimizer, None, train_loader, val_loader, 20)
    torch.save(model.state_dict(), 'transformer')
    return res
