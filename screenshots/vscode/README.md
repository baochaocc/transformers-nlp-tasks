# 你的实际运行截图放这里

把在 VS Code 里截的图保存到本文件夹（`screenshots/vscode/`）。

## 命名建议（按数字前缀会自动排序）

```
01_环境验证.png           # nvidia-smi + torch.cuda.is_available()
02_文本分类.png           # train.py 运行日志（含 global step / Evaluation / best F1）
03_文本匹配-PointWise.png
04_文本匹配-DSSM.png
05_文本匹配-SentenceTransformer.png
06_文本匹配-SimCSE.png
07_UIE信息抽取.png
08_Prompt-PET.png
09_Prompt-ptuning.png
10_RLHF奖励模型.png
11_T5文本问答.png
12_TokenizerViewer.png
```

> 文件名用中文或英文都可以，前缀 `01_`、`02_` 只是为了让插入报告时顺序正确。
> 格式建议用 `.png`；VS Code 截图默认就是 PNG。

## 放好之后

告诉 AI 助手"截图放好了"，会自动：
1. 把这些图按顺序插入到实验报告的「附录 A：实际运行截图」；
2. 重新生成 `基于transformers的NLP多任务实验报告.docx`；
3. 执行 `git add / commit / push` 更新到 GitHub。

## 也放进报告里会更完整

如果想让报告正文更充实，也可以在正文各章节对应位置插入对应截图，
直接在 Word 里打开报告、在正文粘贴即可，保存后重新 push。
