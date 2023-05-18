import os
import tempfile
import typing as tp

import numpy as np
import torch
# from typing import Union, List, Tuple, Optional
from sentencepiece import SentencePieceTrainer, SentencePieceProcessor
from torch.utils.data import Dataset


class CarsDataset(Dataset):
    def __init__(self, features: np.ndarray, texts: tp.Sequence[str], y_true: np.ndarray, train: bool,
                 sp_model_prefix: str, vocab_size: int = 2000, normalization_rule_name: str = 'nmt_nfkc_cf',
                 model_type: str = 'bpe', max_length: tp.Optional[int] = None):
        """
        Dataset with texts, supporting BPE tokenizer
        :param data_file: txt file containing texts
        :param train: whether to use train or validation split
        :param sp_model_prefix: path prefix to save tokenizer model
        :param vocab_size: sentencepiece tokenizer vocabulary size
        :param normalization_rule_name: sentencepiece tokenizer normalization rule
        :param model_type: sentencepiece tokenizer model type
        :param max_length: maximal length of text in tokens
        """
        assert len(features) == len(texts) == len(y_true)
        self.size = len(features)
        self.features = np.float32(features)
        self.n_features = features.shape[1]
        self.y_true = np.float32(y_true)
        self.texts: tp.List[str] = [text.replace('\n', ' ') for text in texts]
        if not os.path.isfile(sp_model_prefix + '.model'):
            assert train, 'Tokenizer is not trained yet'
            tmp_file = tempfile.NamedTemporaryFile('w')
            print(*self.texts, sep='\n', file=tmp_file)
            SentencePieceTrainer.train(
                input=tmp_file.name, vocab_size=vocab_size,
                model_type=model_type, model_prefix=sp_model_prefix,
                normalization_rule_name=normalization_rule_name,
                pad_id=3
            )
        # load tokenizer from file
        self.sp_model: SentencePieceProcessor = SentencePieceProcessor(model_file=sp_model_prefix + '.model')

        self.indices = self.sp_model.encode(self.texts)

        self.pad_id, self.unk_id, self.bos_id, self.eos_id = \
            self.sp_model.pad_id(), self.sp_model.unk_id(), \
                self.sp_model.bos_id(), self.sp_model.eos_id()
        if max_length is None:
            self.max_length = max([len(row) for row in self.indices]) + 2
        else:
            self.max_length = max_length
        self.vocab_size = self.sp_model.vocab_size()

    def text2ids(self, texts: tp.Union[str, tp.List[str]]) -> tp.Union[tp.List[int], tp.List[tp.List[int]]]:
        """
        Encode a text or list of texts as tokenized indices
        :param texts: text or list of texts to tokenize
        :return: encoded indices
        """
        return self.sp_model.encode(texts)

    def ids2text(self, ids: tp.Union[torch.Tensor, tp.List[int], tp.List[tp.List[int]]]) -> tp.Union[str, tp.List[str]]:
        """
        Decode indices as a text or list of tokens
        :param ids: 1D or 2D list (or torch.Tensor) of indices to decode
        :return: decoded texts
        """
        if torch.is_tensor(ids):
            assert len(ids.shape) <= 2, 'Expected tensor of shape (length, ) or (batch_size, length)'
            ids = ids.cpu().tolist()

        return self.sp_model.decode(ids)

    def __len__(self) -> int:
        """
        Size of the dataset
        :return: number of texts in the dataset
        """
        return self.size

    def __getitem__(self, item: int) -> tp.Tuple[torch.Tensor, torch.Tensor, int, float]:
        """
        Add specials to the index array and pad to maximal length
        :param item: text id
        :return: encoded text indices and its actual length (including BOS and EOS specials)
        """
        indices = self.indices[item]
        length = len(indices) + 2
        pad_size = max(0, self.max_length - length)
        padded = torch.tensor([self.bos_id] + indices + [self.eos_id] + [self.pad_id] * pad_size)[:self.max_length]
        return torch.tensor(self.features[item]), padded, min(length, self.max_length), self.y_true[item]
