# 实验运行命令指南（VS Code 终端逐条运行，便于截图）

> 说明：以下命令均已在本机实测通过。在 VS Code 中打开终端（`Ctrl+` `` ` ``），
> 逐条复制运行，运行过程即为「实际运行截图」的素材。

---

## 〇、环境验证（**截图 1：实验环境**）

```powershell
# 0.1 查看 GPU 信息
nvidia-smi

# 0.2 验证 PyTorch 与 CUDA 可用
D:\transformers_tasks\.venv\Scripts\python.exe -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('cuda_version', torch.version.cuda); print('device', torch.cuda.get_device_name(0)); print('capability', torch.cuda.get_device_capability(0))"

# 0.3 关键依赖版本
D:\transformers_tasks\.venv\Scripts\python.exe -c "import transformers, datasets, sklearn, numpy; print('transformers', transformers.__version__); print('datasets', datasets.__version__); print('scikit-learn', sklearn.__version__); print('numpy', numpy.__version__)"
```

---

## 一、文本分类 BERT-CLS（**截图：任务1**）

```powershell
cd D:\transformers_tasks\text_classification
D:\transformers_tasks\.venv\Scripts\python.exe train.py --model "D:/transformers_tasks/models/bert-base-chinese" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --save_dir "checkpoints/comment_classify_gpu" --img_log_dir "logs/comment_classify_gpu" --img_log_name "BERT" --num_labels 8 --batch_size 16 --max_seq_len 128 --valid_steps 25 --logging_steps 5 --num_train_epochs 20 --device "cuda:0"
```

推理验证：

```powershell
D:\transformers_tasks\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); from inference import inference; from transformers import AutoTokenizer, AutoModelForSequenceClassification; m='checkpoints/comment_classify_gpu/model_best'; tok=AutoTokenizer.from_pretrained(m); model=AutoModelForSequenceClassification.from_pretrained(m).to('cuda').eval(); print(inference(model, tok, ['不好看，不值这个价钱','房间超级小，根本不值这个价格'], 'cuda:0'))"
```

---

## 二、文本匹配（**截图：任务2a~2d**）

### 2a. PointWise（单塔）

```powershell
cd D:\transformers_tasks\text_matching\supervised
D:\transformers_tasks\.venv\Scripts\python.exe train_pointwise.py --model "D:/transformers_tasks/models/nghuyong--ernie-3.0-base-zh" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --save_dir "checkpoints/comment_classify_gpu" --img_log_dir "logs/comment_classify_gpu" --img_log_name "ERNIE-PointWise" --batch_size 16 --max_seq_len 128 --valid_steps 177 --logging_steps 10 --num_train_epochs 10 --device "cuda:0"
```

### 2b. DSSM（双塔）

```powershell
cd D:\transformers_tasks\text_matching\supervised
D:\transformers_tasks\.venv\Scripts\python.exe train_dssm.py --model "D:/transformers_tasks/models/nghuyong--ernie-3.0-base-zh" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --save_dir "checkpoints/comment_classify_gpu/dssm" --img_log_dir "logs/comment_classify_gpu/dssm" --img_log_name "ERNIE-DSSM" --batch_size 16 --max_seq_len 128 --valid_steps 177 --logging_steps 10 --num_train_epochs 10 --device "cuda:0"
```

### 2c. Sentence Transformer（双塔）

```powershell
cd D:\transformers_tasks\text_matching\supervised
D:\transformers_tasks\.venv\Scripts\python.exe train_sentence_transformer.py --model "D:/transformers_tasks/models/nghuyong--ernie-3.0-base-zh" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --save_dir "checkpoints/comment_classify_gpu/sentence_transformer" --img_log_dir "logs/comment_classify_gpu/sentence_transformer" --img_log_name "Sentence-Ernie" --batch_size 16 --max_seq_len 128 --valid_steps 177 --logging_steps 20 --num_train_epochs 10 --device "cuda:0"
```

### 2d. SimCSE（无监督）

```powershell
cd D:\transformers_tasks\text_matching\unsupervised\simcse
D:\transformers_tasks\.venv\Scripts\python.exe train.py --model "D:/transformers_tasks/models/nghuyong--ernie-3.0-base-zh" --train_path "data/LCQMC/train_sub.txt" --dev_path "data/LCQMC/dev_sub.tsv" --save_dir "checkpoints/LCQMC_gpu" --img_log_dir "logs/LCQMC_gpu" --img_log_name "ERNIE-ESimCSE" --learning_rate 1e-5 --dropout 0.3 --batch_size 64 --max_seq_len 64 --valid_steps 188 --logging_steps 20 --num_train_epochs 8 --device "cuda:0"
```

---

## 三、信息抽取 UIE（**截图：任务3**）

```powershell
cd D:\transformers_tasks\UIE
D:\transformers_tasks\.venv\Scripts\python.exe train.py --pretrained_model "uie-base-zh" --save_dir "checkpoints/DuIE_gpu" --train_path "data/DuIE/train.txt" --dev_path "data/DuIE/dev.txt" --img_log_dir "logs/" --img_log_name "UIE Base" --batch_size 32 --max_seq_len 256 --learning_rate 5e-5 --num_train_epochs 20 --logging_steps 10 --valid_steps 100 --device "cuda:0"
```

---

## 四、Prompt 任务 PET / p-tuning（**截图：任务4a~4b**）

### 4a. PET

```powershell
cd D:\transformers_tasks\prompt_tasks\PET
D:\transformers_tasks\.venv\Scripts\python.exe pet.py --model "D:/transformers_tasks/models/bert-base-chinese" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --save_dir "checkpoints/comment_classify_gpu/pet" --img_log_dir "logs/comment_classify_gpu/pet" --img_log_name "BERT" --verbalizer "data/comment_classify/verbalizer.txt" --prompt_file "data/comment_classify/prompt.txt" --batch_size 8 --max_seq_len 256 --valid_steps 40 --logging_steps 5 --num_train_epochs 50 --max_label_len 2 --rdrop_coef 5e-2 --device "cuda:0"
```

### 4b. p-tuning

```powershell
cd D:\transformers_tasks\prompt_tasks\p-tuning
D:\transformers_tasks\.venv\Scripts\python.exe p_tuning.py --model "D:/transformers_tasks/models/bert-base-chinese" --train_path "data/comment_classify/train.txt" --dev_path "data/comment_classify/dev.txt" --verbalizer "data/comment_classify/verbalizer.txt" --save_dir "checkpoints/comment_classify_gpu/ptuning" --img_log_dir "logs/comment_classify_gpu/ptuning" --img_log_name "BERT" --batch_size 8 --max_seq_len 128 --valid_steps 40 --logging_steps 5 --num_train_epochs 20 --max_label_len 2 --p_embedding_num 15 --device "cuda:0"
```

---

## 五、强化学习与语言模型 RLHF —— 奖励模型（**截图：任务5**）

> 注：数据为多候选排序样本，代码逐句前向，建议用子集演示（全量在 GPU 上仍需数小时）。

```powershell
cd D:\transformers_tasks\RLHF
D:\transformers_tasks\.venv\Scripts\python.exe train_reward_model.py --model "D:/transformers_tasks/models/nghuyong--ernie-3.0-base-zh" --train_path "data/reward_datasets/sentiment_analysis/train_sub.tsv" --dev_path "data/reward_datasets/sentiment_analysis/dev_sub.tsv" --save_dir "checkpoints/reward_model_gpu/sentiment_analysis" --img_log_dir "logs/reward_model_gpu/sentiment_analysis" --img_log_name "ERNIE Reward Model" --batch_size 32 --max_seq_len 128 --learning_rate 1e-5 --valid_steps 20 --logging_steps 5 --num_train_epochs 1 --device "cuda:0"
```

---

## 六、文本生成 T5 中文问答（**截图：任务6**）

```powershell
cd D:\transformers_tasks\answer_generation
D:\transformers_tasks\.venv\Scripts\python.exe train.py --pretrained_model "D:/transformers_tasks/models/uer--t5-base-chinese-cluecorpussmall" --save_dir "checkpoints/DuReaderQG_gpu" --train_path "data/DuReaderQG/train_gpu.json" --dev_path "data/DuReaderQG/dev_gpu.json" --img_log_dir "logs/DuReaderQG_gpu" --img_log_name "T5-Base-Chinese" --batch_size 8 --max_source_seq_len 128 --max_target_seq_len 32 --learning_rate 1e-4 --num_train_epochs 5 --logging_steps 10 --valid_steps 250 --device "cuda:0"
```

生成效果验证：

```powershell
cd D:\transformers_tasks\answer_generation
D:\transformers_tasks\.venv\Scripts\python.exe -c "from transformers import AutoTokenizer, T5ForConditionalGeneration; p='./checkpoints/DuReaderQG_gpu/model_best'; tok=AutoTokenizer.from_pretrained(p); tok.eos_token=tok.sep_token; tok.bos_token=tok.cls_token; m=T5ForConditionalGeneration.from_pretrained(p).to('cuda').eval(); q='2017年银行贷款基准利率'; c='年基准利率4.35%。'; inp=tok('问题：'+q+tok.sep_token+'原文：'+c, truncation=True, max_length=256, return_tensors='pt').to('cuda'); out=m.generate(input_ids=inp['input_ids'], max_length=32, num_beams=2); print('生成:', tok.decode(out[0], skip_special_tokens=True))"
```

---

## 七、工具类 Tokenizer Viewer（**截图：任务9**）

```powershell
cd D:\transformers_tasks\tools\tokenizer_viewer
# 核心功能验证（词表/编码/解码）
D:\transformers_tasks\.venv\Scripts\python.exe -c "from transformers import AutoTokenizer; tok=AutoTokenizer.from_pretrained('D:/transformers_tasks/models/bert-base-chinese', trust_remote_code=True); ids=tok('这是一个待编码的句子')['input_ids']; print('编码:', ids); print('解码:', tok.decode(ids)); print('词表大小:', len(tok.get_vocab()))"

# 启动 Web 界面（浏览器打开 http://localhost:8001）
D:\transformers_tasks\.venv\Scripts\python.exe -m streamlit run web_ui.py --server.port 8001
```

---

## 八、训练曲线图（报告可直接引用）

各任务训练完成后，会自动在 `logs/<任务名>/` 下生成训练曲线 PNG（如
`text_classification/logs/comment_classify_gpu/BERT.png`），
可直接插入报告作为「损失/F1 随训练步数变化」的图。

---

## 九、附：模型下载命令（新环境首次运行需要）

```powershell
cd D:\transformers_tasks
D:\transformers_tasks\.venv\Scripts\python.exe model_download.py "bert-base-chinese"
D:\transformers_tasks\.venv\Scripts\python.exe model_download.py "nghuyong/ernie-3.0-base-zh"
D:\transformers_tasks\.venv\Scripts\python.exe model_download.py "uer/t5-base-chinese-cluecorpussmall"
# UIE 模型（单独下载到 UIE 目录）
curl.exe -sL -o "UIE\uie-base-zh\pytorch_model.bin" "https://hf-mirror.com/Pky/uie-base-zh/resolve/main/pytorch_model.bin"
```
