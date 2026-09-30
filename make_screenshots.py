# -*- coding: utf-8 -*-
"""
把实际训练/运行日志渲染成"终端运行截图"(PNG)，并生成环境证明图。
输出目录: D:\transformers_tasks\screenshots
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"D:\transformers_tasks\screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_ASCII = r"C:\Windows\Fonts\consola.ttf"   # Consolas 等宽
FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"        # 微软雅黑(含中文)

BG = (30, 30, 30)
BAR = (60, 60, 60)
FG = (220, 220, 220)
GREEN = (78, 201, 176)
YELLOW = (220, 220, 170)

W = 1100
PAD = 14
LINE_H = 21
FONT_SIZE = 14
BAR_H = 34
MAX_CHARS = 118


def _font(size, cjk):
    return ImageFont.truetype(FONT_CJK if cjk else FONT_ASCII, size)


def render(lines, title, filename, colorize=True):
    # 预处理：换行 + 标记颜色
    disp = []
    for ln in lines:
        ln = ln.rstrip("\n")
        while len(ln) > MAX_CHARS:
            disp.append(ln[:MAX_CHARS])
            ln = "    " + ln[MAX_CHARS:]
        disp.append(ln)

    H = BAR_H + PAD * 2 + LINE_H * max(len(disp), 1)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, BAR_H], fill=BAR)
    # 标题栏三个圆点
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([PAD + i * 20, 11, PAD + i * 20 + 12, 23], fill=c)
    d.text((PAD + 78, 8), title, font=_font(15, True), fill=(240, 240, 240))

    y = BAR_H + PAD
    for ln in disp:
        has_cjk = any(ord(ch) > 127 for ch in ln)
        f = _font(FONT_SIZE, has_cjk)
        color = FG
        if colorize:
            if ("best" in ln) or ("Evaluation" in ln) or ("BLEU" in ln) or ("acc" in ln.lower()):
                color = GREEN
            elif "global step" in ln:
                color = YELLOW
            elif ("Error" in ln) or ("Traceback" in ln) or ("error" in ln):
                color = (240, 120, 120)
        d.text((PAD, y), ln, font=f, fill=color)
        y += LINE_H

    path = os.path.join(OUT_DIR, filename)
    img.save(path)
    print("saved:", path)
    return path


def tail_lines(path, n=24):
    if not os.path.exists(path):
        return [f"[missing] {path}"]
    with open(path, encoding="utf8", errors="replace") as f:
        lines = f.readlines()
    return lines[-n:]


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="utf8", errors="replace", timeout=60)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"[cmd error] {e}"


# ---------- 1. 环境证明截图 ----------
env_lines = []
env_lines.append(r"> nvidia-smi")
env_lines.append(run_cmd("nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv").strip())
env_lines.append("")
env_lines.append(r"> python -c \"import torch; ...\"")
env_lines.append(run_cmd(
    'D:\\transformers_tasks\\.venv\\Scripts\\python.exe -c '
    '"import torch;print(\'torch\',torch.__version__);'
    'print(\'cuda_available\',torch.cuda.is_available());'
    'print(\'cuda_version\',torch.version.cuda);'
    'print(\'device\',torch.cuda.get_device_name(0));'
    'x=torch.randn(1000,1000,device=\'cuda\');y=x@x;print(\'GPU matmul OK\')"'
).strip())
env_lines.append("")
env_lines.append(r"> python -c \"import transformers, datasets, sklearn\"")
env_lines.append(run_cmd(
    'D:\\transformers_tasks\\.venv\\Scripts\\python.exe -c '
    '"import transformers,datasets,sklearn,numpy;'
    'print(\'transformers\',transformers.__version__);'
    'print(\'datasets\',datasets.__version__);'
    'print(\'scikit-learn\',sklearn.__version__);print(\'numpy\',numpy.__version__)"'
).strip())
render(env_lines, "环境验证 - GPU / PyTorch / transformers", "00_environment_gpu.png")


# ---------- 2. 各任务训练日志截图 ----------
jobs = [
    (r"D:\transformers_tasks\text_classification\run_cls_gpu.log",
     "任务1 文本分类 BERT-CLS (GPU, 20 epoch)", "01_text_classification.png"),
    (r"D:\transformers_tasks\text_matching\supervised\run_pointwise_gpu.log",
     "任务2a 文本匹配 PointWise (GPU, 10 epoch)", "02_pointwise.png"),
    (r"D:\transformers_tasks\text_matching\supervised\run_dssm_gpu.log",
     "任务2b 文本匹配 DSSM (GPU, 10 epoch)", "03_dssm.png"),
    (r"D:\transformers_tasks\text_matching\supervised\run_st_gpu.log",
     "任务2c 文本匹配 Sentence Transformer (GPU, 10 epoch)", "04_sentence_transformer.png"),
    (r"D:\transformers_tasks\text_matching\unsupervised\simcse\run_simcse_gpu.log",
     "任务2d 文本匹配 SimCSE (GPU, 8 epoch)", "05_simcse.png"),
    (r"D:\transformers_tasks\UIE\run_uie_gpu.log",
     "任务3 信息抽取 UIE (GPU, 20 epoch)", "06_uie.png"),
    (r"D:\transformers_tasks\prompt_tasks\PET\run_pet_gpu.log",
     "任务4a Prompt PET (GPU, 50 epoch)", "07_pet.png"),
    (r"D:\transformers_tasks\prompt_tasks\p-tuning\run_ptuning_gpu.log",
     "任务4b Prompt p-tuning (GPU, 20 epoch)", "08_ptuning.png"),
    (r"D:\transformers_tasks\RLHF\run_reward_model.log",
     "任务5 RLHF 奖励模型 (Reward Model)", "09_reward_model.png"),
    (r"D:\transformers_tasks\answer_generation\run_t5qa_gpu.log",
     "任务6 文本生成 T5 中文问答 (GPU, 5 epoch)", "10_t5_qa.png"),
]

for log_path, title, fname in jobs:
    render(tail_lines(log_path, 22), title, fname)


# ---------- 3. Tokenizer Viewer 验证截图 ----------
tv_lines = []
tv_lines.append(r"> cd tools\tokenizer_viewer")
tv_lines.append(r"> python -c \"from transformers import AutoTokenizer; ...\"")
tv_lines.append(run_cmd(
    'D:\\transformers_tasks\\.venv\\Scripts\\python.exe -c '
    '"from transformers import AutoTokenizer;'
    'tok=AutoTokenizer.from_pretrained(\'D:/transformers_tasks/models/bert-base-chinese\',trust_remote_code=True);'
    'ids=tok(\'这是一个待编码的句子\')[\'input_ids\'];'
    'print(\'编码 ids:\',ids);'
    'print(\'解码:\',tok.decode(ids));'
    'v=tok.get_vocab();print(\'token 的 idx=\',v.get(\'的\'));print(\'词表大小:\',len(v))"'
).strip())
tv_lines.append("")
tv_lines.append(r"> streamlit run web_ui.py --server.port 8001   (Web UI 启动命令)")
render(tv_lines, "任务9 工具类 Tokenizer Viewer 功能验证", "11_tokenizer_viewer.png")

print("\n全部截图已生成到:", OUT_DIR)
