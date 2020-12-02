from sklearn import model_selection
import numpy as np
import pandas as pd
import os
import tokenizers
import string
import torch
import re
import transformers
import torch.nn as nn

from built.registry import Registry

from torch.nn import functional as F
from tqdm import tqdm
from sklearn import metrics
import matplotlib.pyplot as plt

from transformers import AdamW
from transformers import get_linear_schedule_with_warmup

from tweet.src.dataset.tweet_dataset_base import TweetDatasetBase

@Registry.register(category='dataset')
class TweetDataset(TweetDatasetBase):
    def __init__(self, model_path, csv_path, train=False, max_len=96):
        super().__init__(model_path, csv_path, train, max_len)

    def encode_ids(self, encoding, row=None):
        ids = [0] + encoding.ids + [2]
        return ids

    def encode_offsets(self, encoding):
        offsets = [(0, 0)] + encoding.offsets + [(0, 0)]
        return offsets
