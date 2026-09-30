# -*- coding: utf-8 -*-
"""
生成《基于 transformers 的 NLP 多任务实验报告.docx》
正文统一 宋体 五号(10.5pt)；章节按老师要求：实验环境与条件 / 实验方法与过程 /
实验结果及分析 / 遇到的问题及处理情况；并嵌入真实训练曲线图 + 预留运行截图位置。
"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE = r"D:\transformers_tasks"
OUT = os.path.join(BASE, "基于transformers的NLP多任务实验报告.docx")

doc = Document()
normal = doc.styles["Normal"]
normal.font.name = "宋体"
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
normal.font.size = Pt(10.5)


def set_font(run, size=10.5, bold=False, name="宋体"):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.font.bold = bold


def para(text, size=10.5, bold=False, indent=True, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if indent:
        p.paragraph_format.first_line_indent = Pt(21)
    r = p.add_run(text)
    set_font(r, size=size, bold=bold)
    return p


def heading(text, level=1):
    sizes = {1: 15, 2: 12.5, 3: 11}
    p = doc.add_heading(level=level)
    r = p.add_run(text)
    set_font(r, size=sizes.get(level, 11), bold=True)
    return p


def table(rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            r = p.add_run(str(cell))
            set_font(r, size=10.5, bold=(i == 0))
    return t


def picture(path, caption, width=15.0):
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Cm(width))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cp.add_run(caption)
        set_font(r, size=10.5)
    else:
        para(f"[图片缺失] {caption} ---- {path}")


# ================= 封面 =================
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(t.add_run("基于 transformers 的 NLP 多任务实验报告"), size=18, bold=True)
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(s.add_run("—— transformers_tasks 项目实践"), size=11)
doc.add_paragraph()

# ================= 一、实验环境与条件 =================
heading("一、实验环境与条件", 1)
para("本实验基于开源项目 transformers_tasks，系统实践了基于 HuggingFace transformers 库的中文 NLP 多项任务，"
     "包括文本分类、文本匹配、信息抽取（UIE）、Prompt 学习（PET/p-tuning）、强化学习与语言模型（RLHF 奖励模型）、"
     "文本生成（T5 中文问答）以及工具类（Tokenizer Viewer）。实验旨在打通从数据预处理、模型加载、训练到评估推理的完整流程，"
     "并产出可复现的模型 checkpoint 与评估指标。")
heading("1.1 硬件环境", 2)
table([
    ["项目", "配置"],
    ["GPU", "NVIDIA GeForce RTX 5070 Ti Laptop GPU，12 GB 显存，计算能力 sm_120（CUDA 12.8 运行时）"],
    ["CPU / 内存", "多核 CPU，31 GB 内存"],
    ["操作系统", "Windows 64 位"],
])
heading("1.2 软件环境", 2)
table([
    ["软件/库", "版本"],
    ["Python", "3.10.11（虚拟环境 D:\\transformers_tasks\\.venv）"],
    ["PyTorch", "2.10.0+cu128（已启用 GPU）"],
    ["transformers", "4.57.6"],
    ["datasets / evaluate", "5.0.1 / 0.4.6"],
    ["其他依赖", "numpy 2.2.6、scikit-learn 1.7.2、matplotlib 3.10.9、rich 15.0.0、jieba、streamlit 1.63.0、python-docx"],
    ["预训练模型来源", "hf-mirror.com 镜像（本机 huggingface.co 不可直连）"],
])
para("环境验证命令与输出见附录 A（实际运行截图）。")

# ================= 二、实验方法与过程 =================
heading("二、实验方法与过程", 1)
heading("2.1 数据与预训练模型", 2)
para("数据均取自仓库自带数据：文本分类与 Prompt 任务使用 comment_classify（评论分类，8 类，train 402 / dev 63 等）；"
     "文本匹配有监督部分使用同源 comment_classify 文本对（query/doc/label，train 1416 / dev 352），"
     "无监督 SimCSE 使用 LCQMC 语料（本实验取子集 3000 / 500 演示）；信息抽取使用 DuIE（train 2087 / dev 232）；"
     "文本生成使用 DuReaderQG（train 14520，本实验取 2000 子集演示）；RLHF 奖励模型使用 sentiment_analysis 排序打分数据。")
para("预训练模型：bert-base-chinese、nghuyong/ernie-3.0-base-zh、Pky/uie-base-zh、uer/t5-base-chinese-cluecorpussmall，"
     "均通过 hf-mirror 下载至本地 models 目录。由于显存为 12 GB 且部分模型权重（ChatGLM-6B 约 6.5 GB）经镜像 LFS 下载停滞，"
     "本实验未运行 6B/7B 级大模型任务。")

heading("2.2 文本分类（BERT-CLS）", 2)
para("以 bert-base-chinese 为骨干，接分类头做 8 类中文评论分类。使用 CrossEntropyLoss、AdamW 优化器与线性学习率调度，"
     "在 GPU 上以 batch_size=16、max_seq_len=128 训练 20 个 epoch，每 25 步在验证集评估 Accuracy/Precision/Recall/F1。")

heading("2.3 文本匹配（Text Matching）", 2)
para("实现并训练四种匹配方法：单塔 PointWise（[CLS] 池化后二分类）、双塔 DSSM（余弦相似度）、"
     "Sentence Transformer（u、v、|u-v| 拼接分类）与无监督 SimCSE（Dropout 增强的对比学习）。"
     "均以 ernie-3.0-base-zh 为骨干，在 GPU 上训练 8-10 个 epoch。")

heading("2.4 信息抽取（UIE）", 2)
para("UIE 采用“编码器（ERNIE 3.0）+ 起止位置线性层 + Sigmoid”的片段抽取结构，将 prompt 与 content 拼接后预测答案 span 的"
     "起止位置，以 BCELoss 训练、以 SpanEvaluator 评估 Precision/Recall/F1，在 GPU 上以 batch=32、max_seq_len=256 训练 20 个 epoch。")

heading("2.5 Prompt 任务（PET / p-tuning）", 2)
para("PET 使用人工模板“这是一条{MASK}评论：{textA}。”配合 verbalizer 做类别词映射，并引入 R-Drop 损失；"
     "p-tuning 则用可学习的 p-embedding 自动搜索 prompt 表示。二者均以 bert-base-chinese 为骨干，在 GPU 上训练。")

heading("2.6 强化学习与语言模型（RLHF 奖励模型）", 2)
para("RLHF 第一阶段奖励模型采用“ERNIE 编码器 + 线性打分 + 排序损失（compute_rank_list_loss）”实现，"
     "样本为同一 query 下按优劣排序的多个候选回答。训练目标为使奖励分数符合人类排序偏好。")

heading("2.7 文本生成（T5 中文问答）", 2)
para("以 uer/t5-base-chinese-cluecorpussmall 为骨干，将问题与原文拼接为 “问题：Q[SEP]原文：C” 作为编码器输入，"
     "以 “答案：A” 为解码目标，用 CrossEntropy 训练生成式问答模型，在 GPU 上训练 5 个 epoch，以 BLEU-4 评估。")

heading("2.8 工具类与不可运行任务说明", 2)
para("工具类 Tokenizer Viewer 基于 streamlit + transformers，实现词表查看、编解码与 token 搜索；"
     "本实验验证其核心功能并给出启动命令。")
para("任务 7（ChatGLM-6B 零样本与 MBTI）与任务 8（ChatGLM-6B 微调、LLMsTrainer 从零预训练）目标为 6B/7B 级大模型："
     "① 约 6.5 GB 权重经 hf-mirror 的 LFS 下载停滞；② 12 GB 显存装不下 fp16 的 12.4 GB，需 int4/int8 量化；"
     "③ 依赖 cpm_kernels/icetk 及旧版 transformers。受上述硬条件限制，未实际运行，仅完成可行性评估。")

# ================= 三、实验结果及分析 =================
heading("三、实验结果及分析", 1)
heading("3.1 结果汇总", 2)
table([
    ["任务", "模型/方法", "评估指标", "结果"],
    ["文本分类", "BERT-CLS", "F1", "0.86"],
    ["文本匹配", "PointWise", "F1", "0.921"],
    ["文本匹配", "DSSM", "F1", "0.749"],
    ["文本匹配", "Sentence Transformer", "F1", "0.818"],
    ["文本匹配", "SimCSE", "F1", "0.670"],
    ["信息抽取", "UIE", "F1", "0.812"],
    ["Prompt 任务", "PET", "F1", "0.73"],
    ["Prompt 任务", "p-tuning", "F1", "0.70"],
    ["RLHF", "Reward Model", "Accuracy", "0.21（子集演示）"],
    ["文本生成", "T5 中文问答", "BLEU-4", "0.025"],
    ["工具类", "Tokenizer Viewer", "功能验证", "通过"],
    ["LLM 应用/训练", "ChatGLM-6B / 7B", "—", "受限于下载与显存，未运行"],
])

heading("3.2 训练曲线", 2)
para("各任务训练过程中由训练记录器自动绘制损失/指标曲线，下图均为真实运行产物。")
picture(os.path.join(BASE, r"text_classification\logs\comment_classify_gpu\BERT.png"),
        "图 1 文本分类 BERT-CLS 训练曲线")
picture(os.path.join(BASE, r"text_matching\supervised\logs\comment_classify_gpu\ERNIE-PointWise.png"),
        "图 2 文本匹配 PointWise 训练曲线")
picture(os.path.join(BASE, r"text_matching\supervised\logs\comment_classify_gpu\dssm\ERNIE-DSSM.png"),
        "图 3 文本匹配 DSSM 训练曲线")
picture(os.path.join(BASE, r"text_matching\supervised\logs\comment_classify_gpu\sentence_transformer\Sentence-Ernie.png"),
        "图 4 文本匹配 Sentence Transformer 训练曲线")
picture(os.path.join(BASE, r"text_matching\unsupervised\simcse\logs\LCQMC_gpu\ERNIE-ESimCSE.png"),
        "图 5 文本匹配 SimCSE 训练曲线")
picture(os.path.join(BASE, r"UIE\logs\UIE Base.png"), "图 6 信息抽取 UIE 训练曲线")
picture(os.path.join(BASE, r"prompt_tasks\PET\logs\comment_classify_gpu\pet\BERT.png"),
        "图 7 Prompt PET 训练曲线")
picture(os.path.join(BASE, r"prompt_tasks\p-tuning\logs\comment_classify_gpu\ptuning\BERT.png"),
        "图 8 Prompt p-tuning 训练曲线")
picture(os.path.join(BASE, r"RLHF\logs\reward_model\sentiment_analysis\ERNIE Reward Model.png"),
        "图 9 RLHF 奖励模型训练曲线")
picture(os.path.join(BASE, r"answer_generation\logs\DuReaderQG_gpu\T5-Base-Chinese.png"),
        "图 10 文本生成 T5 中文问答训练曲线")

heading("3.3 结果分析", 2)
para("（1）文本分类：20 个 epoch 下验证集准确率 0.88、F1 0.86，损失由约 2.2 平稳下降至 0.6 以下，模型收敛良好；"
     "因训练集仅 402 条、类别较少，继续增加 epoch 提升有限甚至轻微过拟合。")
para("（2）文本匹配：四种方法中 PointWise（单塔，交叉编码）精度最高（F1 0.921）；"
     "Sentence Transformer 由 CPU 版 2 个 epoch 的 0.453 提升至 10 个 epoch 的 0.818，提升最显著；"
     "DSSM 由 0.571 提升至 0.749。说明充分训练（更多 epoch）对双塔类模型收益最大，而单塔模型本身已接近该数据集的性能上限。")
para("（3）信息抽取：UIE 在 20 个 epoch 后验证 F1 达 0.812，起止位置损失降至 1e-4 量级，验证了 prompt+span 抽取框架的有效性。")
para("（4）Prompt 任务：在仅 63 条训练样本的 few-shot 设定下，PET 与 p-tuning 分别取得 F1 0.73 与 0.70，"
     "体现了提示学习在小样本场景下的价值。")
para("（5）文本生成：T5 问答模型训练损失由 7.76 降至 6.08，BLEU-4 由 0 提升至 0.025，已能输出“答案：4.35”等符合格式且"
     "抽取正确的答案，说明生成式问答流程已跑通；因基座为掩码语言模型（MLM）且演示数据量小，指标仍偏低，需更大数据与更长训练。")
para("（6）综合来看，GPU 相对 CPU 带来约 19 倍训练加速，使原本只能跑 2-3 个 epoch 的任务能够完整训练 10-20 个 epoch，"
     "是本次指标整体提升的主要原因。")

# ================= 四、遇到的问题及处理情况 =================
heading("四、遇到的问题及处理情况", 1)
table([
    ["序号", "问题", "原因", "处理方式"],
    ["1", "matplotlib 报错 seaborn-darkgrid 样式不存在", "新版 matplotlib 移除了该样式", "捕获异常后回退使用 seaborn-v0_8-darkgrid 或 default"],
    ["2", "rich 输出 UnicodeEncodeError（emoji）", "Windows 控制台默认 GBK 编码", "设置 PYTHONUTF8=1 与 UTF-8 输出编码"],
    ["3", "evaluate.combine 报模块不存在", "需联网从 Hub 下载指标脚本（网络受限）", "用 sklearn 自行实现本地 MatchingMetric 替代"],
    ["4", "UIE 旧模型加载报 _output_attentions 缺失", "旧版 transformers 序列化的 config 与新版本不兼容", "加载后遍历模型配置，补齐 _output_* 私有属性"],
    ["5", "UIE 权重大小与实际不符、加载损坏", "首次下载被 --max-time 截断", "改用断点续传/完整下载并校验文件大小"],
    ["6", "UIE 权重在 CUDA 上保存无法直接加载", "本机默认按 CPU 环境加载", "torch.load 指定 map_location='cpu'、weights_only=False"],
    ["7", "缺少 jieba 分词模块", "Augmenter 模块依赖 jieba", "pip 安装 jieba"],
    ["8", "PyTorch 仅为 CPU 版本，GPU 未被使用", "pip 默认安装 CPU 版 torch", "从 download.pytorch.org 安装 torch==2.10.0+cu128，启用 GPU"],
    ["9", "大模型权重下载停滞", "ChatGLM-6B 等经镜像 LFS 下载为 0 字节", "记录为环境限制，未运行，报告中如实说明"],
    ["10", "12 GB 显存无法容纳 6B 模型 fp16", "fp16 需约 12.4 GB", "评估使用 int4/int8 量化方案，仍未运行"],
])

# ================= 五、实验总结 =================
heading("五、实验总结", 1)
para("本实验完整打通了基于 transformers 的中文 NLP 多任务流程，在 GPU 上显著提升训练效率与评估指标，"
     "修复了旧代码与新环境的多项兼容性问题，各任务均产出可复现的 checkpoint 与指标，"
     "并验证了工具类组件的可用性。受限方面，ChatGLM-6B 系列与 7B 级 LLM 任务、RLHF 的 PPO 阶段因模型规模、"
     "显存与依赖等原因未能运行。后续如具备 24 GB 以上显存与稳定高速网络，可进一步完成大模型相关任务。")

# ================= 附录 =================
heading("附录 A：实际运行截图", 1)
para("（在此处粘贴 VS Code / 终端中实际运行各任务的截图，可参照 RUN_GUIDE.md 中的命令逐条运行并截图。）", indent=False)
for _ in range(6):
    doc.add_paragraph()
para("截图建议包含：① 环境验证（nvidia-smi、torch.cuda.is_available()）；"
     "② 各任务训练日志（含 global step、loss、Evaluation 与 best F1/BLEU 行）；"
     "③ 工具类功能验证输出。", indent=False)

heading("附录 B：实验运行命令", 1)
para("完整可复制的运行命令见仓库根目录 RUN_GUIDE.md，涵盖环境准备、模型下载、各任务 GPU 训练命令与推理验证命令。")

doc.save(OUT)
print("已生成：", OUT)
