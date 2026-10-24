# 30 · 本机实测工具链

> **何时读**：要动手解固件/二进制/流量题、需要挑一个能跑的工具、或工具"明明装了却调不通"时。**这里写的是本机实测过的路径与坑，别凭猜调用工具**（调外部程序前先跑 `--help`）。
> 来源：`zeekr-ctf-2026` §四（本机工具链）＋ §7.3（读图兜底链）＋ §7.12（会话日志取证工具指针）。

---

## 一、Windows 侧

| 工具 | 路径 / 版本 | 备注 |
|---|---|---|
| IDA Pro 9.2 | `<IDA_DIR>` | 含 `idat.exe`，**可批处理**（先 `--help` 确认参数） |
| 7-Zip | 已装 | ext4/cramfs/cpio/tar/iso 通吃 |
| tshark | `<TSHARK_EXE>` | 流量题首选 |
| Python 3.13 | 已装 | capstone / unicorn / keystone / angr / z3 / pycryptodome / pwntools / PyMuPDF |
| 其它 | Node、Java、sqlite3、gcc/mingw | Java 环境用于 JADX / ysoserial 类工作 |

**可直接调用的 MCP**：IDA MCP、JADX MCP、sharkmcp、chrome-devtools、playwright（另有 FOFA 测绘 MCP，属授权实战用途，见 skill `src-hunt`）。

> **调 MCP 的通用两条**（2026-09-20 实测）：①**别并行调同一个 MCP**——很多中转有 ~3 秒限流，
> 并行必挂一个且**静默丢结果**（返回 `http_status: 429` 时等 3 秒串行重试即可，不是 Key 坏）；
> ②**注意工具的默认过滤参数**——它会静默缩小结果集（实测 FOFA 的默认 `status_code=200`
> 让同一查询从 460 条变成 8 条，差 57 倍）。**看到数量小得反常，先怀疑自己的参数，别当成事实。**

## 二、WSL Ubuntu-22.04（root）—— 固件主战场

已装工具：

```
binwalk、unsquashfs、7z、ubi_reader、jefferson、dtc、srec_cat、can-utils、mtd-utils、
cpio、交叉 objdump（arm/aarch64/mips）、sqlite3、cramfsck、simg2img
```

| 动作 | 命令 |
|---|---|
| 一键装/修（**幂等**） | `wsl -d Ubuntu-22.04 -u root -e bash /mnt/d/<HARNESS_DIR>/zeekr-2026/tools/setup_wsl_firmware.sh` |
| 补 Python 库 | `wsl -d Ubuntu-22.04 -u root -e bash -lc "pip3 install python-can cantools pycryptodome z3-solver"` |

## 三、两个已实测的坑（**必看，都静默出错**）

| 坑 | 现象 | 对策 |
|---|---|---|
| **WSL 的 `/tmp` 会被清空** | 两次 `wsl` 调用之间 `/tmp` 里的中间产物消失 | **产物一律放 `/mnt/d/...`**（跨调用持久） |
| **管道里 `grep -a` 要一路带** | 第一个 `grep` 用了 `-a`，后面的没带 → 含 NUL 的二进制行让下游 grep 只回 `binary file matches`，**静默吞掉真实命中** | **后面每个 grep 都带 `-a`**（曾因此搜不到配置文件里的口令） |

## 四、操作纪律

- **调外部程序前先跑 `--help`**（尤其 IDA / 自定义工具）；**不确定的参数不要猜**。
- **单个大输出先落盘再摘要**，别灌进上下文。
- 本机 `<TOOLS_DIR>\Lib` 下有 `dataclasses.py` / `inspect.py` **影子模块**，会打断 `cryptography` 的
  import 链（`pub.verify()` 报 `TypeError: missing 1 required positional argument: 'signature_algorithm'`），
  且**脚本别命名为 `inspect.py`** —— 复现细节见 `12-family-patterns.md` 家族 4·陷阱。

## 五、读图兜底链（模型不吃图时，本机实测可用）

按顺序退化，**关键规格图必须交叉验证**：

| 顺序 | 手段 | 位置 / 用法 |
|---|---|---|
| ① | 本机 **Qwen-VL** | key 在 `empire\data\dsh-home\.credentials.yaml`，脚本 `zeekr-2026\tools\vlm.py` |
| ② | Windows **WinRT OCR** | `zeekr-2026\tools\lineocr.py` |
| ③ | WSL **tesseract-ocr** ＋ **逐字形位图人工判读** | 规格图里 `B/8`、`3/8`、`01F/1FF` 这类**必须逐字形确认**，单靠 OCR 会错 |

> 三手段交叉验证的实战判据：把"读图对不对"变成**可判定的数学事实**——
> 128×5 个格子墨量只有两桶（如 40/177，无歧义格），且 5 张碎片全部满足
> `XOR(全部数据点) == 实心 PARITY 点` ⇒ 读错任何一位这个等式几乎不可能 5/5 成立。
> 通用脚本归档：`zeekr-2026\tools\imgkit\`（含 README 与"深底浅字先判底色"等实测坑）。

## 六、赛后取证：会话日志是唯一可信的"事实基线"

> 复盘"到底发生了什么"**先跑这个，别靠回忆**。

- 数据源：`<HARNESS_HOME>\sessions\<workspace>\<sid>\session.v3.jsonl.zstd`（逐事件 JSONL）。
- 工具：**`<HARNESS_HOME>\zeekr-2026\tools\session-forensics\`**（Python + `zstandard`，无需额外依赖）：

  | 脚本 | 作用 |
  |---|---|
  | `timeline.py` | 每个会话的真实起止**时间线** |
  | `tokens.py` | 逐会话/逐步 **token 账单** |
  | `digest2.py` | 单会话深摘 |
  | `submissions.py` | 搜**平台判正/判错回执**原文 |

- 它能替代"靠回忆"的三件事：①真实起止时间 ②每步 token 用量 ③**平台回执原文**（提交 flag 到底对不对）。
- 纪律：**复解任何一题之前**，先在工作区会话日志里 grep `提交的Flag正确` / `提交的Flag错误` / `solved=true`，
  用回执把状态钉死再决定要不要重推。（flag 总账口径 → `04-flag-and-ledger.md`）
