# -*- coding: utf-8 -*-
"""
本地实现 evaluate 库的 combine(["accuracy","f1","precision","recall"]) 接口，
避免从 HuggingFace Hub 下载 metric 模块（本环境下 hub 受限）。
接口与 evaluate 兼容：add_batch(predictions=..., references=...), compute()。
"""
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def _to_list(x):
    if hasattr(x, "cpu"):          # torch tensor
        x = x.detach().cpu().numpy()
    if hasattr(x, "tolist"):       # numpy array
        x = x.tolist()
    return list(x)


class MatchingMetric:
    def __init__(self):
        self.preds = []
        self.refs = []

    def reset(self):
        self.preds = []
        self.refs = []

    def add_batch(self, predictions=None, references=None):
        self.preds.extend(_to_list(predictions))
        self.refs.extend(_to_list(references))

    def compute(self):
        p = np.asarray(self.preds)
        r = np.asarray(self.refs)
        return {
            "accuracy": float(accuracy_score(r, p)),
            "precision": float(precision_score(r, p, average="binary", zero_division=0)),
            "recall": float(recall_score(r, p, average="binary", zero_division=0)),
            "f1": float(f1_score(r, p, average="binary", zero_division=0)),
        }
