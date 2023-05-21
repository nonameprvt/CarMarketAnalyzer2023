import typing as tp

import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import wandb

from price_prediction.models import ModelBase


def training_epoch(model: ModelBase,
                   optimizer: torch.optim.Optimizer,
                   loader: DataLoader,
                   tqdm_desc: str) -> tp.Tuple[float, float]:
    train_mse = 0.0
    train_mape = 0.0

    model.train()
    for features, indices, lengths, y_true in tqdm(loader, desc=tqdm_desc):
        optimizer.zero_grad()
        output = model(
            features.to(model.device),
            indices[:, :max(lengths)].to(model.device),
            lengths
        ).cpu()

        loss = nn.MSELoss()(output, y_true)
        loss.backward()
        optimizer.step()

        train_mse += loss.item() * len(features)
        train_mape += (torch.abs(output - y_true) / y_true).sum().item()

    train_mse /= len(loader.dataset)
    train_mape /= len(loader.dataset)
    return train_mse, train_mape


@torch.no_grad()
def validation_epoch(model: ModelBase,
                     loader: DataLoader,
                     tqdm_desc: str) -> tp.Tuple[float, float]:
    val_mse = 0.0
    val_mape = 0.0

    model.eval()
    for features, indices, lengths, y_true in tqdm(loader, desc=tqdm_desc):
        output = model(
            features.to(model.device),
            indices[:, :max(lengths)].to(model.device),
            lengths
        ).cpu()

        loss = nn.MSELoss()(output, y_true)
        loss.backward()

        val_mse += loss.item() * len(features)
        val_mape += (torch.abs(output - y_true) / y_true).sum().item()

    val_mse /= len(loader.dataset)
    val_mape /= len(loader.dataset)
    return val_mse, val_mape


def train(model: ModelBase,
          optimizer: torch.optim.Optimizer,
          scheduler: tp.Optional[tp.Any],
          train_loader: DataLoader,
          val_loader: DataLoader,
          num_epochs: int,
          log_wandb: bool = False
          ) -> tp.Tuple[tp.List[float], tp.List[float], tp.List[float], tp.List[float]]:
    train_losses, val_losses = [], []
    train_mapes, val_mapes = [], []

    for epoch in range(1, num_epochs + 1):
        train_loss, train_mape = training_epoch(
            model, optimizer, train_loader,
            tqdm_desc=f'Training {epoch}/{num_epochs}'
        )
        val_loss, val_mape = validation_epoch(
            model, val_loader,
            tqdm_desc=f'Validating {epoch}/{num_epochs}'
        )

        if scheduler is not None:
            scheduler.step()

        if log_wandb:
            wandb.log({
                'train_mse': train_loss,
                'val_mse': val_loss,
                'train_mape': train_mape,
                'val_mape': val_mape
            })

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_mapes.append(train_mape)
        val_mapes.append(val_mape)

    return train_losses, val_losses, train_mapes, val_mapes
