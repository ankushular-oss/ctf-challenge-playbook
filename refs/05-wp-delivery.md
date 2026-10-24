# 05 · WriteUp 交付（真截图链路 ＋ docx 版式复刻）

> **何时读**：要交 WP / writeup / 题解 / 解题报告时；要抓**真实窗口截图**时；要照着参考件对齐 .docx 版式时。
> 来源：原 `ctf-challenge-playbook` **§5.2 WriteUp**；原 `ctf-wp-writer` **全文**
> （§零 三件事 / §零·五 版本侦测 / §零·七 立刻执行 / §一 硬红线 / §一·五 清晰度公式 / §二 变体 A 版式 /
> §三 截图工作流 / §四 docx 写法 / §五 踩坑 / §六 脚本清单 / §七 交付话术）＋ 其 `PROMPTS.md`；
> 原 `zeekr-ctf-2026` **§7.6 WP 交付物（TEAM 版式）**、**§7.9 TEAM 模板 docx 复刻：正确参数与双验证法**。

---

## 〇、两条路线先分流（决定后面读哪几节）

| 情况 | 走哪条 | 读哪几节 |
|---|---|---|
| 用户**明确要截图**（"要截图""用真截图""不要重绘""调用我的截图工具""截真实窗口""要调试器画面"） | **A 线：真截图链路** | §三 全部 → §四 变体 A 版式 → §五 docx 写法 |
| 用户**没提截图**、只要文字 WP / 题解 | **B 线：纯文字 docx 版式复刻**（**不要启动截图链路**，默认也不自己加截图） | §二 侦测 → §六 原型克隆 |

**分流依据不是"哪条更高级"，而是参考件的形态**（先跑 §二 的侦测脚本，10 秒）：

| 变体 | 体量 | 特征 | 路线 |
|---|---|---|---|
| **A 截图版** | ~1.44 MB | 含 `word/media/image1..15.png` | 截图与叙述交替，用 §四 那套硬参数 |
| **B pandoc 版** | 24605 B | **无 `word/media`**、`styles.xml` ~45 KB、有 `af2`/`2`/`3` 样式名 | 纯文字，走 §六 原型克隆 |

> 两条路线共用同一条铁律：**先解包量一遍参考件，再动手**（§二）。skill 里的数字只是**某一版的观测值，不是契约**。

---

## 一、内容规范：赛事层的硬要求（§5.2，多数赛事是"一票否决"项）

| # | 要求 | 说明 |
|---|---|---|
| 1 | **官方模板优先** | 有官方模板/骨架就必须逐项对齐；没有才用下面这个骨架 |
| 2 | 骨架 | `## <题目序号> <题目名称>` → `操作内容：`（猜想 → 实践 → 工具与方法 → 关键命令/输出 → **flag 怎么来的**）→ 自写脚本**贴代码文本**（**不许截图代码**）→ `flag值：` |
| 3 | **文件名必须含战队名** | 各场通道与命名另见 `20-competition-notes.md` |
| 4 | **少写任何一道解出的题 = 整份无效** | 交付前对齐"解出的题清单"与 `flags.md` 的条数 |
| 5 | **解一题立刻写本题片段** | 写到该题目录（`chals/<题>/WP-<题名>.md`）；**赛后只做拼接，不做回忆** |
| 6 | 第三方工具**注明来源**；自研脚本**必须贴关键函数** | 判据是"别人能否按它复现" |
| 7 | **关键步骤不可省略 / 一笔带过** | 同上——判据是"复现" |
| 8 | **截图** | 多数赛事要求"关键步骤截图"。**全程录屏时把重要一步顺手截一张存到题目录，别赛后补（补不出来）**。要真截图 → 走 A 线 |
| 9 | 过期的片段必须先更新 | `WP-*.md` 停在"flag 待补"而 flag 早已拿到 = 交付物内部矛盾，评审会直接怀疑真实性（详见 `04-flag-and-ledger.md`） |

---

## 二、动手前的三道闸门

### 2.1 先确认的三件事（§零）

1. **参考 WP 路径**（拿来对齐版式）：`<HARNESS_HOME>\wp_ref\TEAM-WP.docx`
2. **截图工具**：`<HARNESS_HOME>\tools\shot.ps1`（文档 `shot.README.md`）
3. **输出位置**：题目工作目录，例如 `<HARNESS_HOME>\<题名>_analysis\<题名>-WP.docx`

> **路径约定**：`<HARNESS_HOME>` 指你自己的工具与工作目录根路径，按本机实际情况替换。
> 本节引用的 `tools\shot.ps1`、`wp_shots\*`、`x64plug\shotnav.cpp`、`数信杯2026\工具\*` 都是本机自建脚本，**未随仓库发布**。
> 没有它们时按这四项能力自己实现或找等价品：① 抓任意窗口（含后台/最小化）截图
> ② 按 PID 精确结束无窗口标题的 Word 进程（不要按进程名批量杀）
> ③ 把目标进程冻结在解压后状态再附加调试器 ④ 把一题/一场的 md 笔记批量装配成 docx（图片按相对路径内嵌）。

**如果参考 WP 或 `shot.ps1` 不存在，先问用户要——不要凭记忆编版式。**

### 2.2 先量后套：参考件版本侦测（§零·五，差点踩坑后加的硬闸门）

**`TEAM-WP.docx` 不是一个文件，是很多个互不相同的文件。** 同名、甚至同样"看起来像 `bb0acdc…`"的副本，
字节数和版式都可能完全不同。§四 那套硬参数只是**其中一版**（1.44 MB 版）的实测值，
套到别的版本上会**整体错版**。

**动手前第一件事，永远是解包量一遍（10 秒）**：

```powershell
# 量体量 / 看有没有图片 / 看样式名 —— 三个数就能判定走哪条路
python -c "
import zipfile;z=zipfile.ZipFile(r'<参考.docx>')
n=z.namelist()
print('media:', [x for x in n if 'media' in x][:3])
print('has af2 style:', b'w:val=\"af2\"' in z.read('word/styles.xml'))
import re;d=z.read('word/document.xml').decode('utf8')
print('pBdr per para:', d.count('<w:pBdr>'), '| drawings:', d.count('<w:drawing'))
print('first fonts:', sorted(set(re.findall(r'w:ascii=\"([^\"]+)\"', d)))[:6])
"
```

#### 复刻方法：**原型克隆 > 手搓参数**

不要用参数去"重建"版式（基准参数会过期、会漏项）。正确做法是**让参考件自己当中文模板**：

1. 打开参考 docx；
2. 从参考 body 里**取出每种段落角色的 XML 原型**（标题 / H2 / H3 / 正文 / 代码语言标签 / 代码行）；
3. 新文档 = **参考的全部包部件逐字节复制**（`styles.xml`、`settings.xml`、`theme1.xml`、
   `fontTable.xml`、`docProps`、`_rels`、`[Content_Types].xml`）＋ **只替换 `word/document.xml`**
   （正文段落 = 克隆原型换字，尾部 `sectPr` 原样保留）。

这样字体 / 字号 / 间距 / 边框 / 底纹**不是"调到像"，是同一份定义**。

#### 自检（交付前必跑）

判定标准是**包含关系**，不是"看着差不多"：

- 除 `word/document.xml` 外，所有部件与参考**逐字节相同**；
- 新文档里出现的**每一个样式签名**（`pStyle` ＋ `w:ascii` 字体 ＋ `sz` ＋ 颜色 ＋ `w:shd` fill
  ＋ `w:pBdr` 色 ＋ 加粗）**都必须在参考里已经存在** —— 出现一个参考里没有的签名，就是你自己造了样式。

**可复用**：
`<HARNESS_HOME>\zeekr-2026\chals\geely-uds-32k\build_wp.py`（B 版生成器，参考件路径写在文件头 `REF`，
用 DSH 保存的只读副本）＋ `verify_format.py`（逐段签名比对）＋ `verify_wp.py`（section/字体/段落数）；
变体 A 的同类工具见 `<HARNESS_HOME>\zeekr-2026\wp-template\gen_wp.py` ＋ `verify.py`。

> **变体 B 的 `text` 段落不是正文，是图片占位框**（`w:pBdr` `374151` ＋ `w:shd` `1E1E1E`
> ＋ DejaVu Sans Mono `sz=18`），一版里有 **28 个**，即 28 个截图位。**画纯文字 WP 时不要把它们抄进去**
> ——否则文档里会留一排空黑条。真要贴图时，就在这些占位框的位置插。（§7.9 同义：参考件里那些 `text`
> 占位段是**深色阴影图片占位框**，纯文字 WP 不要照抄。）

#### 另外两条实测坑（§零·五 ＋ §7.5）

- **代码块里不要用 `✓`/`✗`**：Consolas 没有这两个字形，Word 会掉成方框。
  用纯 ASCII（`-> 成立` / `-> 不成立`）。交付前扫一遍代码段里的非 ASCII 符号（CJK 与 CJK 标点除外）。
- **不要照抄参考件里明显的排版 bug**（B 版有一处把两行代码挤进同一个 run、行没换开）。
  按参考其余同类段落的正常做法写，**别把 bug 一起克隆**。

### 2.3 闸门："不用截图" / "不用了" = 立刻执行，并清干净现场（§零·七）

**闸门是双向的。** 用户中途说"不用截图"时，正确动作是**同一个回合内**：
停止截图链路 → 删掉已生成的半成品截图与驱动脚本 → 接着把文字 WP 交付完。

**反面教材（真犯的）**：用户说"不用截图"之后，我还在继续调控制台字号、准备自己起终端窗口，
白白多耗好几轮。**"不用了"本身就是撤回指令，不是背景信息。**

#### 如果确实需要抓自己的终端输出

- **不要在用户的 Windows Terminal 里开标签页**。本机 `cmd /k` ＋ `CREATE_NEW_CONSOLE`
  会被 Windows 11 路由成用户**已有窗口里的新标签**，等于当着用户的面改他的工作区
  （清 `WT_SESSION` 也拦不住）。优先改用 PrintWindow 抓**已经存在的自有窗口**。
- 真要抓：**按 HWND 抓、按 HWND 关**，绝不 `Stop-Process -Name WindowsTerminal`
  （一个进程承载用户全部终端窗口）。收尾时确认用户原来的窗口还在。
- 抓完先算清晰度（§三·二 公式），再看内容对不对；**两次都过才算交付**。

---

## 三、路线 A：真截图链路

### 3.1 硬红线（违反即返工，§一）

| # | 规则 |
|---|---|
| 1 | **绝不重绘**。不许用 HTML/CSS/Canvas 画一个"像终端 / 像反汇编窗口"的图当截图。**必须是真实窗口的像素。** |
| 2 | 截图只能通过**用户的 `shot.ps1`** 或**本机快照能力**（PrintWindow / 真实窗口枚举）产生。 |
| 3 | 不许用其它 AI 生成图像冒充截图。 |
| 4 | **先把真实截图全部拿到、OCR 自检通过，再开始写 docx。**顺序反了会写出对不上的文字。 |
| 5 | 参考 WP 的字体 / 字号 / 页边距 / 图片宽度**逐项对齐**，不要"差不多"。 |
| 6 | **交付前必须做"清晰度体检"**（见 3.2）。图片宽固定 6.74 in，所以**窗口开得越大字越小**——截图"能打开"≠"能看清"。**实测过看不清被退回，别再犯。** |
| 7 | **绝不按进程名杀进程**。`Stop-Process -Name WindowsTerminal/x64dbg` 会连带杀掉用户自己开着的全部窗口（已出过事故）。要关自己开的窗口：**按 HWND 发 `WM_CLOSE`**，或**按自己设置的唯一标题匹配**。 |

### 3.2 清晰度硬公式（交付前必算，§一·五，被退回后量出来的）

docx 里图片固定 **6.74 in** 宽，所以图中文字的**有效字号**：

```
有效字号(pt) ≈ (6.74 ÷ 图宽px) × 行高px × 72
```

| 组合 | 有效字号 | 结论 |
|---|---|---|
| 终端字号 11 ＋ 窗口 1300 px | ≈ **3.2 pt** | **完全不可读**（已交付过一次被退回） |
| 终端字号 16 ＋ 窗口 2420×1050 ＋ 裁空白 | ≈ **6.4 pt** | 可读，**本机推荐** |
| x64dbg 默认字号 ＋ 窗口 1172 px | ≈ **4 pt** | **偏小**，交付前必须放大字号或加大截图 |

四条配套要点：

1. **图宽是最强变量**——窗口开大时若不加大字号，文字反而更小。
2. **整窗必须落在屏幕可视区内**，否则 `PrintWindow` 会把屏外那块在整张位图上**水平平铺重复**
   （现象：同一行输出重复 3 遍）。
3. **按内容 bbox 裁掉四周空白**——"两行字 ＋ 700 px 空白"插进 docx 既看不清又把正文挤走。
4. **抓图进程必须声明 DPI 感知**：本机物理 2560×1600、缩放 150%，未声明 DPI 感知的进程拿到虚拟坐标
   （1707×1067），与抓屏 / SetWindowPos 的物理像素不一致 → 抓屏区域整体错位、抓到别的窗口。
   脚本开头调用 `user32.SetProcessDpiAwarenessContext(-4)`
   （退化 `shcore.SetProcessDpiAwareness(2)` → `SetProcessDPIAware`）。

### 3.3 真实截图工作流（§三）

#### 3.3.0 先看一眼有哪些窗口

```powershell
& <HARNESS_HOME>\tools\shot.ps1 -List          # 拿 Hwnd / PID / 标题 / 位置尺寸
```

`-Mode` 二选一：

- `printwin`（**首选**）：`PrintWindow(hwnd, hdc, 2)`，`2 = PW_RENDERFULLCONTENT`。
  **被遮挡、最小化、DirectX/OpenGL 都能抓。**
- `screen -Focus`：拷屏幕区域，所见即所得；`-Focus` 内部会循环重试抢前台。

其它开关：`-Ocr`、`-OcrLang zh-Hans-CN`、`-BottomPercent 40`、`-ProcId`。

#### 3.3.1 真实终端窗口（PowerShell 输出截图）

**不要** `Start-Process powershell` 然后找窗口——本环境下：

- `MainWindowHandle` 常为 **0**；
- `Start-Process` 起的新控制台**不会出现可见窗口**；
- **SendInput / SendKeys 到不了任何窗口**（实测 Notepad 收不到字符）。

**可行做法**（已封装为 `cap_terminal.ps1`，见 §七）：

1. 枚举可见窗口，挑标题匹配 `*Windows PowerShell*` / `*cmd.exe*` 的
   （通常是 Windows Terminal，`proc=WindowsTerminal`）；
2. 抢前台：**AttachThreadInput(GetCurrentThreadId(), 前台线程, true) → SetForegroundWindow → detach**，
   循环重试最多 **20 次**直到 `GetForegroundWindow() == 目标`；
3. 用 `[System.Windows.Forms.SendKeys]::SendWait()` 往那个**真实前台窗口**打字
   （SendKeys 在这里**是**有效的，因为它走的是前台窗口消息）；
   - 先 `^c` 清行，再发命令，再 `{ENTER}`；
   - 命令里带 `cls;` 让画面干净；
4. `PrintWindow(hwnd, hdc, 2)` 抓那个窗口。

> 注意：SendKeys **只在"目标确实成为真前台"后才生效**——所以第 2 步的成功校验**不能省**。

#### 3.3.2 真实 x64dbg 截图（含脱壳过程）

x64dbg 装在本机：`<X64DBG_EXE>`（2026.05.27）。
Qt 窗口**不响应** `PostMessage` 的 `WM_KEYDOWN`，所以**别想用模拟按键驱动它**。
改用**自写驱动插件 ＋ 文件当控制通道**（这是本流程的核心工具）：

- 源码：`<HARNESS_HOME>\x64plug\shotnav.cpp`
- 产物：`shotnav.dp64` → 放到 `<X64DBG_DIR>\plugins\`
- 命令：`ShotGo`（绝对地址跳反汇编）、`ShotGoC`（加注释后跳）、`ShotGoD`（Dump 面板）、`ShotStep`
- 控制通道：脚本往 `<HARNESS_HOME>\wp_shots\step.txt` 写一行
  `<seq> <kind> <hexaddr> [label]`，插件轮询执行后把结果写 `state.txt`
- `kind`：`91` = 跳反汇编、`93` = 加注释+跳、`94` = 跳 Dump 面板、其它 = 预置步骤

编译（本机有 MinGW g++ ＋ SDK）：

```powershell
cd <HARNESS_HOME>\x64plug; cmd /c build.bat      # 产出 shotnav.dp64
Copy-Item shotnav.dp64 <X64DBG_DIR>\plugins\shotnav.dp64 -Force
```

**脱壳取"解压后内存"的关键手法**（适用于懒解压壳，如 UPX＋NRV2B）：
程序跑完一次就退出（全程 ~50 ms），直接附加调试器来不及。正确顺序：

1. `CreateProcessW(..., CREATE_SUSPENDED)` ＋ **匿名管道当 stdin**（`STARTF_USESTDHANDLES`）；
2. 先把输入写进管道，再 `ResumeThread`；
3. 紧接着 `NtSuspendThread(mainThread)` / 轮询直到目标 RVA 出现非零代码
   （实战：轮询 `RVA 0x1440` 直到读到 `55 48 89 e5 … c7 45 ec b9 79 37 9e`）；
4. 此时进程**冻结且已解压**，再用 `x64dbg.exe -p <pid>` 附加；
5. 通过 `step.txt` 导航到各地址，`PrintWindow` 抓图。

> 若直接把程序跑完，进程一退出 `ReadProcessMemory` 会失败（`NtReadVirtualMemory` 返回 `0x8000000D`，
> `VirtualQueryEx` 报 MEM_FREE），现象很像权限不足，**实际是进程已经没了**。

**抓 x64dbg 窗口时选对 HWND**：会有两个同进程窗口，要选标题里带**模块名 ＋ x64dbg** 的那个
（形如 `xxx.exe - PID: N - 模块: ntdll.dll - 线程: 主线程 N - x64dbg`），另一个是"发布说明"日志窗口。
用 `cap_dbg.ps1 -Out <png>`（§七）。

#### 3.3.3 验收：OCR 自检

每张图都要确认内容对得上（**不能只看文件大小**）：

```powershell
# 命令行 OCR（本机 tesseract，路径要显式给）
<PYTHON_EXE> -c "import pytesseract; from PIL import Image; \
pytesseract.pytesseract.tesseract_cmd=r'<TESSERACT_EXE>'; \
print(pytesseract.image_to_string(Image.open(r'<png>'), config='--psm 6')[:400])"
```

更稳的是**从 Hwnd 反查地址列**：对截图做 **4 倍放大 ＋ autocontrast**，再用
`--psm 6 -c tessedit_char_whitelist=0123456789ABCDEF` 只抽十六进制，
比对每张图的起始地址是否**各不相同**（相同 = 视图没跟着导航走）。

### 3.4 版式规格：变体 A 专属（§二，1.44 MB 截图版实测值，照抄）

> ⚠️ 这一节的数值**只对变体 A（1.44 MB、含 `word/media`）成立**。
> 拿到参考件先跑 §二 的侦测；如果它没有图片、有 `af2` 样式名，那就是变体 B，
> **本节全部参数作废**，改走原型克隆，**不要用下面的数字去凑**。

| 项目 | 值 |
|---|---|
| 页面 | `w=11900` × `h=16840` twips（A4，20.99 × 29.70 cm） |
| 页边距 | top=**0**，right=1140，bottom=437，left=1060 twips |
| 可用正文宽 | **6.74 in**（= 6159500 EMU） |
| 标题 | 18 pt（`w:sz=36`，`szCs=40`），`w:ind left=3780`，`w:vertAlign baseline` |
| 正文 | 10.5 pt（`w:sz=21`，`szCs=22`） |
| 中文字体 | 微软雅黑（`w:eastAsia`） |
| 西文字体 | Times New Roman（`w:ascii` / `w:hAnsi` / `w:cs`） |
| run 字体提示 | `w:rFonts w:hint="eastAsia"` |
| 段落间距 | `spacing after=160 line=278 lineRule=auto`（≈ 1.157 倍） |
| 图片 | 一律 **width = 6.74 in**，高度按原始宽高比自动 |
| 文档默认 | `docDefaults` 里 `kern=2`、`sz=22`、`lang en-US/zh-CN` |

**内容模式**（照参考 WP 的骨架）：

```
标题（如 "xxx-WP"）
正文段落 → 图片 → 正文段落 → 图片 → …（截图与叙述交替）
代码/参数行原样成段（保持 10.5pt，不换字号）
最后一行给出 flag
结尾一句收束（参考 WP 用"脱壳之后即可获得flag"这类短句）
```

正文语气照参考 WP：**大白话叙述解题过程**（"打开可以发现…""这里可以看到…""说明…"），
一段讲一个判断，下一张图给出证据。**不要写成教科书式定义。**

### 3.5 生成 docx 的固定写法（变体 A，§四）

用 python-docx，`Document()` 后立刻把 §3.4 的参数逐项写进去：

```python
from docx import Document
from docx.shared import Pt, Inches, Emu
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

EA, LATIN, IMG_W = "微软雅黑", "Times New Roman", Inches(6.74)
doc = Document()
sec = doc.sections[0]
sec.page_width  = Emu(11900*635); sec.page_height = Emu(16840*635)
sec.top_margin  = Emu(0);         sec.right_margin = Emu(1140*635)
sec.bottom_margin = Emu(437*635); sec.left_margin  = Emu(1060*635)

st = doc.styles['Normal']; st.font.name = LATIN; st.font.size = Pt(11)
rpr = st.element.get_or_add_rPr()
rf = rpr.find(qn('w:rFonts')) or OxmlElement('w:rFonts')
rf.set(qn('w:ascii'), LATIN); rf.set(qn('w:hAnsi'), LATIN)
rf.set(qn('w:eastAsia'), EA); rf.set(qn('w:cs'), LATIN)
st.paragraph_format.space_after = Pt(8); st.paragraph_format.line_spacing = 1.157
```

- 标题 run：`sz=36` ＋ `szCs=40` ＋ `w:ind left=3780` ＋ 可选 `w:vertAlign baseline`
- 正文 run：`sz=21` ＋ `szCs=22` ＋ `w:rFonts hint="eastAsia"`
- 图片：`p.add_run().add_picture(path, width=IMG_W)`

**交付前校验**（照抄这段自检）：

```python
import zipfile; from docx import Document
p = r"<out.docx>"
print(zipfile.ZipFile(p).testzip() is None)          # zip 完整性
d = Document(p); s = d.sections[0]
print(s.page_width.cm, s.page_height.cm, s.left_margin.cm, s.right_margin.cm)
print(len(d.paragraphs), sum('graphic' in x._p.xml for x in d.paragraphs))
```

---

## 四、路线 B：TEAM 模板 docx 复刻 —— 正确参数与双验证法（§7.9 ＋ §7.6）

### 4.1 做法

解包参考 docx → **原样保留** `styles.xml` / `settings.xml` / `theme` / `fontTable` / `sectPr`，
**只重建 `word/document.xml` 的 body**；段落 / run 的 `pPr` / `rPr` 取**参考件自身原型**
（与 §二·二 原型克隆同法）。

### 4.2 实测参数（395 参考件 24605 B，变体 B / pandoc 风格）

| 项目 | 实测值 |
|---|---|
| 页面 | A4 **11906 × 16838** twips |
| 页边距 | **top/bottom 1440、left/right 1800** twips |
| 标题 | style `2`，**MFXuanRen** `sz27`，`0000FF` |
| Flag / WP | style `2`，**GeistSans** `sz31` 粗，`111827` |
| 小节 | style `3`，`sz26` 粗 |
| 正文 | style `af2`，`sz27`，`374151` |
| 代码框 | 每段 `pBdr` ＋ `shd 1E1E1E`；run = **Consolas** `sz19` `D4D4D4` ＋ 字符样式 `HTML` |

**同前缀不同版本**：`bb0bacdc…` 前缀对应过**至少 3 个**不同字节数 / 不同页边距的副本
⇒ **每次收到参考件都重新解包量参数**，不要认前缀。

> 本赛（极氪 2026）参考件（24605 B, sha256 `bb0bacdc…`）属**变体 B（pandoc 风格、纯文本无图）**；
> 生成器 `zeekr-2026\wp-template\gen_wp.py`，自检 `verify.py`；成品示例
> `chals\391-Delta Forge\TEAM-Delta-Forge-WP.docx`。

### 4.3 双验证（交付前两条都要过）

1. **脚本指纹**：`new ⊆ ref`（**0 个自创样式**）＋ `styles.xml` 哈希相同；
2. **Word 读回**：`Style.NameLocal` / `Font.Name` / `.Size` / `.Color` /
   `Shading.BackgroundPatternColor` 与参考**一致**。

### 4.4 用 Word COM 时的纪律

- 必须 `try/finally` ＋ **必须 `Quit()`**；
- **只按 PID / 唯一标题关自己的实例**（实战只关掉 `CommandLine` 含 `/Automation -Embedding`
  且**无窗口**的两个自家实例），**绝不按进程名批量杀**；
- 但**不要用 COM 做"渲染验证"**（导 PDF 验版式）——120 s 超时 ＋ 留残留进程，
  格式正确性用程序化自检证明（详见 `03-parallel-and-budget.md` §六）。

---

## 五、踩过的坑（别再踩，§五）

1. **PowerShell 变量大小写不敏感**：`[int]$Step` 与 `$STEP` 会互撞 →
   `Cannot convert "...step.txt" to type "System.Int32"`。参数与路径变量**必须换名**。
2. **PowerShell 5.1 把无 BOM 的 `.ps1` 当 GBK 读**：脚本里写中文注释会直接 parse error。
   凡是要在 pwsh 里跑的脚本**一律纯 ASCII**。
3. **别用 PowerShell 的 `-replace` 去改含中文的 `.py` 文件**——会把 UTF-8 写坏
   （实测把 `KERNEL32 的` 变成 `KERNEL32 �?` 导致 SyntaxError）。要改就用定点替换工具。
4. **docx 正被 Word 打开时无法覆盖保存**（`PermissionError: [Errno 13]`）→ 存新文件名，
   并在交付话术里说明。
5. **控制通道的序号不要挤在一个整数里**：早期把 `step*1000+seq` 打包成一个 int，
   序号涨到 1024 就溢出改装了 step 字段（`93xxx` 被解析成 step 93 → BADSTEP）。
   **用空格分隔的多字段格式。**
6. **`PostMessage` 驱动不了 Qt 窗口**（x64dbg 不响应 Ctrl+D / WM_KEYDOWN）。
   要么用程序化 API（`GuiDisasmAt` / `GuiDumpAt` / `DbgCmdExec`），要么**文件当通道**。
7. **x64dbg 默认布局把 Dump 面板折叠了**：`dump <addr>` 能改地址但面板不显示。
   数据类证据用 **CPU 视图 ＋ `DbgSetCommentAt` 打注释**更实在。
8. 抓窗口前先 `Get-Process <name> | Where-Object MainWindowHandle -ne 0`；
   本环境 `Start-Process` 新进程的 `MainWindowHandle` 常为 0，**得靠 `EnumWindows`**。
9. **整场 WP 的"自述段"如果由装配脚本内联生成，改 md 是白改**：
   数信杯那次 `工具\wp_final.py` 用脚本里的 `TASKS` 表算题数/总分并硬编码名次句，
   我改了 `WP_源.md` / `WP_最终.md` 两处 md 都没生效（`WP_最终.md` 还是**输出**文件，被覆盖）。
   正确顺序：**先看装配脚本的 TASKS/口径 → 改脚本 → 重跑 → 打开 docx 验字**（`zipfile` 读
   `word/document.xml` 去标签后 `in` 检查残留分数、`my_rank`、flag 串是否命中）。
10. **截图要按"窗口标题子串"匹配，标题会随页面变**：SPA 路由页标题是赛事名，JSON 接口页标题变成 URL。
   匹配不上就 `-TitleMatch` 换串（或用 Chrome 自带截图兜底）。本次用
   `工具\win_cap.ps1 -TitleMatch <子串> -Out <png>`（PrintWindow ＋ `PW_RENDERFULLCONTENT`，
   **能拍后台窗口、不抢焦点**；必须用 pwsh7 调，PS5.1 读 UTF-8 脚本会乱码导致中文路径找不到）。

---

## 六、可复用脚本清单（已在盘上，§六）

| 脚本 | 用途 |
|---|---|
| `<HARNESS_HOME>\tools\shot.ps1` | 万能窗口截图（**用户的工具，优先用它**） |
| `<HARNESS_HOME>\wp_shots\cap_dbg.ps1` | 精准抓 x64dbg 主窗口（按标题含模块名过滤） |
| `<HARNESS_HOME>\wp_shots\cap_terminal.ps1` | 抓真实终端：抢前台 ＋ SendKeys 打命令 ＋ PrintWindow |
| `<HARNESS_HOME>\wp_shots\launch_unpack.py` | 拉起目标 ＋ 管道喂 stdin ＋ 冻结在解压后状态 |
| `<HARNESS_HOME>\wp_shots\run_all.ps1` | 一条龙：解压冻结 → 附加 → 注释 → 抓 4 张调试器图 |
| `<HARNESS_HOME>\x64plug\shotnav.cpp` ＋ `build.bat` | x64dbg 驱动插件（**文件当控制通道**） |

**新题复用时**：把 `run_all.ps1` / `launch_unpack.py` 里的
**目标 exe 路径、模块名、关键 RVA（入口/OEP、算法函数、数据表）**换成新题的值即可。

### 6.1 整场 WP 的"全量装配器"（数信杯 2026 实测，一天多次重建）

单题 WP 用上面的截图链路；**整场比赛的 WP（几十题＋队友稿）用装配器**，否则每次改口径都要重排一遍：

| 脚本 | 用途 |
|---|---|
| `<HARNESS_HOME>\数信杯2026\工具\wp_final.py` | **唯一入口**：`TASKS` 表（题号/题目/分类/分值/解题人/flag）＋ `WP\notes\<id>.md`（我方逐题笔记）＋桌面 `队友原始草稿\*.md` → 一次生成 md ＋ docx ＋ 投递到桌面目录 |
| `<HARNESS_HOME>\数信杯2026\工具\wp_build.py` | 纯 md→docx（手写 OOXML，无第三方依赖，图片按 md 相对路径内嵌） |
| `<HARNESS_HOME>\数信杯2026\工具\win_cap.ps1` | PrintWindow 取证截图（吃后台窗口） |
| `<HARNESS_HOME>\数信杯2026\工具\wp_merge.py` | 只用于把队友 md 按 `#### <id>` 降级插入（全量重建不要用它） |

**纪律**：① 改题数/总分/名次 → 改 `wp_final.py` 的 `TASKS` 与自述句，**不要改 md**（见 §五·9）；
② 重跑后必须验字验图（docx 大小 ＋ `word/media` 三张图的字节数 ＋ 关键数字/flag 命中）；
③ 只跑 `wp_build.py` 会拿到旧素材拼出的半成品（本次 464 KB vs 全量 1.18 MB）。

---

## 七、交付话术（§七）

给用户回话时说明：

- 交付物**绝对路径**（用可点击的行内代码格式）；
- 截图是**真实窗口**（列出哪些是 x64dbg 实拍、哪些是终端实拍）；
- 若因 Word 占用改了文件名，**明确讲**；
- 若某张图内容有妥协（例如 Dump 面板没显示、用了 CPU 视图代替），**主动说明**，不要糊过去。

---

## 八、附：两个可复制提示词（原 `PROMPTS.md`）

> 用在新会话里。**提示词 A** 管**真截图**，**提示词 B** 管 **WP 版式**。
> 两个可以一起发；**只想出文字 WP 就只发 B**（这样不会触发截图链路）。固化日期：2026-09-18。

### 提示词 A —— 真实截图（要真截图时才发）

```
这次要真实截图，不要任何重绘/自绘的图。

硬性要求：
1. 所有截图必须是真实窗口的像素，禁止用 HTML/CSS/Canvas 画"像终端/像反汇编窗口"的图冒充，
   也不许用任何 AI 生成图像。只能通过我本机的能力实拍。
2. 截图工具优先用我自己的：<HARNESS_HOME>\tools\shot.ps1
   （文档 <HARNESS_HOME>\tools\shot.README.md）
   - 先 `-List` 看窗口，拿 Hwnd / PID / 标题
   - 抓被遮挡/后台/最小化窗口用 `-Mode printwin`（内部是 PrintWindow 带 PW_RENDERFULLCONTENT=2）
   - 要所见即所得用 `-Mode screen -Focus`
   - 需要文字核对时加 `-Ocr`、`-OcrLang zh-Hans-CN`、`-BottomPercent`
3. 终端类截图（PowerShell 输出）：
   - 本环境 `Start-Process powershell` 起的新控制台**没有可见窗口**，
     `MainWindowHandle` 常为 0；SendInput/SendKeys 也到不了普通窗口。
   - 可行做法：枚举可见窗口挑标题含 `Windows PowerShell` / `cmd.exe` 的那个
     （通常是 Windows Terminal），用
     AttachThreadInput(GetCurrentThreadId(), 前台线程, true) → SetForegroundWindow → detach
     循环重试抢到真前台（校验 GetForegroundWindow()==目标），
     再用 [System.Windows.Forms.SendKeys]::SendWait() 往那个真前台窗口打字
     （先 ^c 清行，再发命令，再 {ENTER}），最后 PrintWindow(hwnd, hdc, 2) 抓图。
   - 命令里带 `cls;` 让画面干净。
4. 调试器类截图（x64dbg）：
   - x64dbg 在 <X64DBG_EXE>；Qt 窗口**不响应 PostMessage**，
     别用模拟按键驱动它。
   - 用我已有的驱动插件 <HARNESS_HOME>\x64plug\shotnav.cpp（编译产物 shotnav.dp64
     放到 <X64DBG_DIR>\plugins\），它注册了 ShotGo / ShotGoC / ShotGoD / ShotStep，
     控制通道是文件：往 <HARNESS_HOME>\wp_shots\step.txt 写一行
     `<seq> <kind> <hexaddr> [label]`（kind: 91=跳反汇编 93=加注释+跳 94=跳Dump），
     插件执行后把结果写 state.txt。
   - 抓 x64dbg 窗口时要选标题里带"模块名 + x64dbg"的那个主窗口
     （另一个是"发布说明"日志窗）。可用 <HARNESS_HOME>\wp_shots\cap_dbg.ps1。
   - 加壳题要拍"脱壳后"的代码：程序若跑完就退出（毫秒级），别直接附加调试器。正确顺序是
     CreateProcess(CREATE_SUSPENDED) + 匿名管道当 stdin → 先写输入 → ResumeThread →
     立刻 NtSuspendThread 冻结 → 轮询目标 RVA 直到出现非零代码 → 再 `x64dbg -p <pid>` 附加。
     （参考实现 <HARNESS_HOME>\wp_shots\launch_unpack.py）
5. 每张图抓完都要**自检内容**（不能只看文件大小）：用本机离线 OCR 或放大后抽取十六进制地址，
   确认画面确实是想要的那一处；多张疑似相同的要逐像素比对，相同就说明导航没生效，别当成功。
6. 先把图全部拿到并自检通过，再写文档。
```

### 提示词 B —— TEAM-WP 版式（写 WP 时发）

```
请按下面这套固定版式写 WP（对齐我的参考 WP：<HARNESS_HOME>\wp_ref\TEAM-WP.docx）。

【页面参数（照抄，别改）】
- 页面 11900 × 16840 twips（A4，20.99 × 29.70 cm）
- 页边距：上 0、右 1140、下 437、左 1060 twips
- 正文可用宽 = 6.74 in（6159500 EMU）

【字体与字号（照抄，别改）】
- 标题：18pt（w:sz=36 / w:szCs=40），段首缩进 w:ind left=3780，run 带 w:vertAlign baseline
- 正文：10.5pt（w:sz=21 / w:szCs=22）
- 中文字体：微软雅黑（w:eastAsia）
- 西文字体：Times New Roman（w:ascii / w:hAnsi / w:cs）
- run 字体提示：w:rFonts w:hint="eastAsia"
- 段落间距：spacing after=160 line=278 lineRule=auto（约 1.157 倍行距）
- 文档默认：kern=2、sz=22、lang en-US / zh-CN

【图片】
- 一律按宽度 6.74 in 插入，高度按原图宽高比自动
- 截图与正文段落**交替**排布（一段话 → 一张图 → 一段话 → 一张图）

【内容结构（照参考 WP 的骨架）】
1. 第一段就是标题，形如 "题名-WP"
2. 按解题真实顺序叙述：先讲看到什么、判断是什么，再给对应的截图作证据
3. 语气用大白话讲过程（"打开可以发现…""这里可以看到…""说明…"），
   不要写成教科书式定义；一段只讲一个判断
4. 代码/参数行原样成段，保持 10.5pt，不要换字号
5. 最后给出 flag
6. 结尾一句短句收束（参考 WP 用的是"脱壳之后即可获得flag"这种）

【交付】
- 用 python-docx 生成 .docx，保存到题目工作目录
- 保存前做校验：zip 完整性 + 页面/页边距 cm 值 + 段落数与图片数
- 若目标 .docx 被 Word 占用（PermissionError），存成新文件名并告诉我
- 交付时给我绝对路径
```

**用法备注**：

- **只想要文字 WP**（不折腾截图）：**只发 B**，此时不要走截图链路。
- **要真图**：先发 **A** 再发 **B**（或一起发）。
- 换新题时提示词里可以补一句：`题目工作目录：<HARNESS_HOME>\<题名>_analysis\`，
  脚本里需要替换的变量是 **目标 exe 路径、模块名、关键 RVA（入口/OEP、算法函数、数据表）**。
- **发送 A / B 之前先跑 §二·二 的侦测**：如果手上的参考件不是变体 A，
  提示词 B 里那套页面/字体参数要换成实测值（**照抄 skill 参数会整体错版**）。
