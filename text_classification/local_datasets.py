# -*- coding: utf-8 -*-
"""
local_datasets.py —— 轻量级的 datasets.load_dataset 替代实现。

背景：
    本项目仅使用 datasets 的 load_dataset('text', data_files=...) 读取本地文本文件，
    而 datasets 强依赖 pyarrow。在开启 Windows「智能应用控制(Smart App Control)」的机器上，
    pyarrow 的 arrow*.dll 会被安全策略拦截（报错：应用程序控制策略已阻止此文件），
    导致 `from datasets import load_dataset` 直接导入失败。

本模块提供与 datasets 兼容的最小接口，完全不依赖 pyarrow：
    load_dataset('text', data_files={'train': p1, 'dev': p2}) -> DatasetDict
    DatasetDict / Dataset 支持: __len__ / __getitem__ / map(batched=True) / select

用法：把各脚本中的 `from datasets import load_dataset`
      改为 `from local_datasets import load_dataset` 即可。
"""
import os

__all__ = ["load_dataset", "Dataset", "DatasetDict"]


class Dataset:
    """极简数据集：以「列名 -> 列表」的形式存储。"""

    def __init__(self, columns):
        self._columns = {k: list(v) for k, v in columns.items()}
        if self._columns:
            self._num_rows = len(next(iter(self._columns.values())))
        else:
            self._num_rows = 0

    # ---- 兼容 datasets 的常用属性 ----
    @property
    def column_names(self):
        return list(self._columns.keys())

    @property
    def features(self):
        return self.column_names

    @property
    def num_rows(self):
        return self._num_rows

    def __len__(self):
        return self._num_rows

    def __getitem__(self, index):
        # ds['text'] -> 整列；ds[0] -> 一行；ds[0:3] -> 子数据集
        if isinstance(index, str):
            return self._columns[index]
        if isinstance(index, slice):
            idxs = range(*index.indices(self._num_rows))
            return Dataset({k: [v[i] for i in idxs] for k, v in self._columns.items()})
        return {k: v[index] for k, v in self._columns.items()}

    def map(self, function, batched=False, **kwargs):
        """与 datasets.Dataset.map 兼容；本项目只用到 batched=True。"""
        if batched:
            out = function(self._columns)
        else:
            out = {}
            for i in range(self._num_rows):
                row = function({k: v[i] for k, v in self._columns.items()})
                for k, v in row.items():
                    out.setdefault(k, []).append(v)
        return Dataset(out)

    def select(self, indices):
        idxs = list(indices)
        return Dataset({k: [v[i] for i in idxs] for k, v in self._columns.items()})

    def filter(self, function, **kwargs):
        keep = [i for i in range(self._num_rows) if function(self[i])]
        return self.select(keep)

    def __repr__(self):
        return "Dataset({\n    features: %s,\n    num_rows: %d\n})" % (
            self.column_names,
            self._num_rows,
        )


class DatasetDict(dict):
    """与 datasets.DatasetDict 兼容：对每个 split 同时 map。"""

    def map(self, function, batched=False, **kwargs):
        return DatasetDict(
            {k: v.map(function, batched=batched, **kwargs) for k, v in self.items()}
        )

    def __repr__(self):
        inner = ",\n    ".join("%s: %r" % (k, v) for k, v in self.items())
        return "DatasetDict({\n    " + inner + "\n})"


def load_dataset(name=None, data_files=None, **kwargs):
    """读取本地文本文件，每个文件一行作为一个样本（与 datasets 'text' 行为一致）。"""
    if data_files is None:
        raise ValueError("local_datasets.load_dataset 仅支持本地 data_files 参数")
    if isinstance(data_files, (str, os.PathLike)):
        data_files = {"train": data_files}

    result = DatasetDict()
    for split, path in data_files.items():
        paths = list(path) if isinstance(path, (list, tuple)) else [path]
        lines = []
        for p in paths:
            with open(p, encoding="utf-8") as f:
                lines.extend([ln.rstrip("\n") for ln in f])
        result[split] = Dataset({"text": lines})
    return result
