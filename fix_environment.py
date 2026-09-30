# -*- coding: utf-8 -*-
"""
fix_environment.py —— 修复「Windows 智能应用控制(Smart App Control)拦截 pyarrow」导致的运行失败。

背景
----
    本机开启了 Windows 智能应用控制(SAC)，它会拦截**未签名**的 DLL，而 pyarrow 的
    arrow*.dll 未签名，因此任何版本的 pyarrow 都无法加载，报错：
        ImportError: DLL load failed while importing lib: 应用程序控制策略已阻止此文件。

    后果：
      - `from datasets import load_dataset` 失败（datasets 强依赖 pyarrow）
      - `import sklearn` 失败（sklearn 在 fixes.py 中可选导入 pyarrow，
         但只捕获 ModuleNotFoundError，捕获不到 DLL 加载失败的 ImportError）

本项目采用「绕开 pyarrow」的方案（无需改动系统安全设置）：
    1) datasets  ->  用仓库内的 local_datasets.py 替代（各脚本已改为
                     `from local_datasets import load_dataset`），完全不依赖 pyarrow；
    2) sklearn   ->  本脚本把 sklearn/utils/fixes.py 中
                     `except ModuleNotFoundError:` 改为 `except ImportError:`
                     （该处只是读取 pyarrow 版本号，捕获不到也不影响功能）。

用法（在项目虚拟环境中运行一次即可）：
    D:\\transformers_tasks\\.venv\\Scripts\\python.exe fix_environment.py

如果你更希望“一劳永逸”，也可以在
    Windows 安全中心 -> 应用和浏览器控制 -> 智能应用控制 -> 关闭
（注意：微软说明该开关关闭后不可再开启，除非重装/重置 Windows）。
"""
import os
import sys

SITE = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "..", "Lib", "site-packages")
SITE = os.path.normpath(SITE)
FIXES = os.path.join(SITE, "sklearn", "utils", "fixes.py")

OLD = "except ModuleNotFoundError:  # pragma: no cover\n    pass"
NEW = "except ImportError:  # pragma: no cover  # also catch DLL-load ImportError\n    pass"


def main():
    if not os.path.exists(FIXES):
        print("[skip] 未找到 sklearn：", FIXES)
        return

    with open(FIXES, encoding="utf-8") as f:
        content = f.read()

    if NEW in content:
        print("[ok] sklearn 已是修复后的状态，无需修改。")
    elif OLD in content:
        content = content.replace(OLD, NEW, 1)
        with open(FIXES, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print("[patched] 已修复 sklearn：", FIXES)
    else:
        print("[warn] 未找到预期的代码片段，sklearn 版本可能不同，请手动检查：", FIXES)

    # 验证
    import subprocess
    r = subprocess.run([sys.executable, "-c", "import sklearn; print('sklearn OK', sklearn.__version__)"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    main()
