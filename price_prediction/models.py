from abc import ABC, abstractmethod
import math

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from price_prediction.dataset import CarsDataset


class ModelBase(nn.Module, ABC):
    def __init__(self, dataset: CarsDataset, text_dim: int):
        super().__init__()
        self.dataset = dataset
        self.n_features = dataset.n_features
        self.vocab_size = dataset.vocab_size
        self.max_length = dataset.max_length
        self.pad_id = dataset.pad_id

        self.linear = nn.Linear(in_features=self.n_features + text_dim, out_features=1)

    @property
    def device(self) -> torch.device:
        return next(self.parameters()).device

    def forward(self, features: torch.Tensor, indices: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        text_features = self._get_text_features(indices, lengths)
        return self.linear(torch.hstack([features, text_features])).ravel()

    @abstractmethod
    def _get_text_features(self, indices: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        pass

    @torch.inference_mode()
    def get_text_features(self, indices: torch.Tensor, lengths: torch.Tensor) -> np.ndarray:
        self.eval()
        return self._get_text_features(indices, lengths).detach().cpu().numpy()


class LSTMModel(ModelBase):
    def __init__(self, dataset: CarsDataset, embed_dim: int = 256,
                 hidden_size: int = 256, num_layers: int = 1, dropout: float = 0.2):
        super().__init__(dataset, hidden_size * num_layers)
        self.embedding = nn.Embedding(num_embeddings=dataset.vocab_size, embedding_dim=embed_dim,
                                      padding_idx=self.pad_id)
        self.lstm = nn.LSTM(input_size=embed_dim, hidden_size=hidden_size, num_layers=num_layers, batch_first=True,
                            dropout=dropout)

    def _get_text_features(self, indices: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        embeds = self.embedding(indices)
        packed_embeds = pack_padded_sequence(embeds, lengths, batch_first=True, enforce_sorted=False)
        _, (h_n, _) = self.lstm(packed_embeds)
        return h_n.reshape(len(indices), -1)


class PositionalEmbedding(nn.Module):
    def __init__(self, vocab_size: int, pad_idx: int, max_length: int, dim: int, dropout: float):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=dim, padding_idx=pad_idx)
        den = torch.exp(- torch.arange(0, dim, 2) * math.log(10000) / dim)
        pos = torch.arange(0, max_length).reshape(max_length, 1)
        pos_embedding = torch.zeros((max_length, dim))
        pos_embedding[:, 0::2] = torch.sin(pos * den)
        pos_embedding[:, 1::2] = torch.cos(pos * den)
        self.pos_embedding = pos_embedding
        self.dropout = nn.Dropout(dropout)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        embeds = self.embedding(tokens)
        pos_embeds = self.pos_embedding[:tokens.shape[1]].to(next(self.parameters()).device)
        return self.dropout(embeds + pos_embeds)


class AttentionModel(ModelBase):
    def __init__(self, dataset: CarsDataset, num_layers: int = 6, attention_heads: int = 8, dim: int = 512,
                 dropout: float = 0.2) -> None:
        super().__init__(dataset, dim)
        self.cls_token = self.vocab_size
        self.embedding = PositionalEmbedding(self.vocab_size + 1, self.pad_id, self.max_length + 1, dim, dropout)

        encoder_layer = nn.TransformerEncoderLayer(dim, attention_heads, dim * 4, dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)

        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def _get_text_features(self, indices: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        n = len(indices)
        cls_tokens = torch.full(size=(n, 1), fill_value=self.cls_token).to(self.device)
        new_indices = torch.hstack([cls_tokens, indices])
        padding_mask = (new_indices == self.pad_id)
        embeds = self.embedding(new_indices)
        return self.encoder(src=embeds, src_key_padding_mask=padding_mask)[:, 0, :]
