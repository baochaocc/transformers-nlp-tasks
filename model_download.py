# -*- coding: utf-8 -*-
"""
从 hf-mirror 下载任务所需的中文预训练模型到本地 D:\transformers_tasks\models\<model>。
用法: python model_download.py <model_name> [models_dir]
"""
import os, sys, argparse

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
os.environ.setdefault("HF_HOME", r"D:\transformers_tasks\hf_cache")

from huggingface_hub import snapshot_download
from huggingface_hub import HfApi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", help="huggingface model id, e.g. bert-base-chinese")
    ap.add_argument("--local_dir", default=r"D:\transformers_tasks\models")
    args = ap.parse_args()

    name = args.model.replace("/", "--")
    local_dir = os.path.join(args.local_dir, name)

    print(f"[download] {args.model} -> {local_dir}")
    path = snapshot_download(
        repo_id=args.model,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot", "*.onnx"],
        max_workers=4,
    )
    print(f"[done] downloaded to {path}")
    # 列出已下载的关键文件
    for f in sorted(os.listdir(local_dir)):
        full = os.path.join(local_dir, f)
        if os.path.isfile(full):
            print(f"    {f}  {os.path.getsize(full)} bytes")


if __name__ == "__main__":
    main()
