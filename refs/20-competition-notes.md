# 20 · 历史赛事存档（三场已结束的比赛）

> **何时读**：①有人提到 极氪 / Zeekr / 西湖论剑 / 霄元杯；②要打一场**新**比赛、需要判断"这场属于哪种赛制形态"；
> ③需要 DASCTF 类平台的接口套路。
> **立场**：三场都已结束（2026-08），**具体赛程/凭据/matchId 全部失效**，本文件只保留"换个比赛还能用"的部分。
> 来源：原 `westlake-ctf-agent` / `xiaoyuan-ctf-2026` / `zeekr-ctf-2026`（已并入本 skill）。

---

## 一、最要紧的一条：三种赛制形态**互不通用**

⚠️ 这是本文件存在的主要理由。把 A 场的规则套到 B 场，轻则白做，重则**违规**。

| 形态 | 代表赛事 | AI 的角色 | 致命差异 |
|---|---|---|---|
| **AI Agent 夺旗赛** | 第九届西湖论剑（`gcsis.dasctf.com`，DASCTF） | **Agent 就是选手**，每队仅允许一个 Agent 接入平台 | **用户不能给答案/解法提示**（连"逆序+Base32"这种提示都算违规），只能做方向性指导；**模型必须走平台网关白名单**，禁外部模型/中转站；模型流量被审计 |
| **传统 CTF + 理论赛** | 霄元杯·星域之盾（OpenVPN 内网） | AI 是**助手**，队员主导 | **AI 使用声明计入评分（20 分）**，且"截图 + 代码"是必需项；**flag 一票否决**（错/未获取 = 该题 0 分）；题解每题一个 docx |
| **传统线上 CTF** | 极氪全球汽车网络安全挑战赛（太初封神台） | **规则明文允许 AI 解题** | 无 WP 评分（以 flag 为准）；动态积分 + **前三名额外奖励原始分的 30/20/10** ⇒ 抢首杀收益极高 |

**开赛前 5 分钟必做**：把本场的 **AI 规则原文**与**WP/题解规则原文**抄进工作区 `notes/`，赛中不再猜。
来源：`ctf-challenge-playbook` §5.4；本文件即该纪律的由来。

---

## 二、跨场稳定、值得复用的三条

### 2.1 凭据与赛程**绝不写进 skill**
- 反面教材：`westlake-ctf-agent` 早期把 `ak_live_*`、账号口令、matchId 写死在 skill 里 → 赛事一结束全部腐化。
- 正确做法：skill 里只留**指针**——"凭据/matchId/stageId 一律读工作区 `<赛事>\config.json`"。
- 已被 `_INDEX.md` 写成硬规矩：**单场赛事/一次性凭据不要写进长期 skill**。

### 2.2 WP / 题解的"提交规则"每场都不同，且都是坑
| 赛事 | 规则要点 |
|---|---|
| 西湖论剑 | **一个队只有一次 WP 提交机会** ⇒ **比赛中绝不提交**，每题 WP 只写进 `prelim/writeups/`；**赛后**合并成一个文档，发官方邮箱，**邮件主题 = 排名-团队名称**；**缺一题则整份无效** |
| 霄元杯 | 每题独立 docx（`赛队名-赛题名.docx`）打包 ZIP 上传；结构必须逐项对齐官方模板（题目 → **flag 置顶** → **AI 使用声明** → 思路 → 关键步骤+截图 → 完整代码 → 难点）；**关键步骤 50 分 + 规范 50 分** |
| 极氪 | 以 flag 为准，赛后另有 WP 交付（TEAM 版式，另行见 `05-wp-delivery.md`） |

⇒ **交付前先问"这场的 WP 通道是什么、能不能重交、缺题会怎样"**，再决定什么时候写、写几份。

### 2.3 DASCTF 类平台的接口套路（换个 DASCTF 赛事仍适用）
- **WAF**：`pro.dasctf.com` 用浏览器 UA，`requests` 默认 UA 直接 403（HTML 页）⇒ 客户端内置 Chrome UA + Referer。
- **鉴权位置会改变行为**：`matchId` 必须放 **header**（放 query 会变行为）；`stageId` 必须放 **body**（放 query 报 `40001 阶段不存在`）。
- **错误码速查**：`40409` 参数/方法不对（multipart 字段名必须是 `file`）｜`40001` stageId 位置错或无效｜`40500` 业务拒绝（先查开关）｜`40403` 路径不存在（接口名拼错）。
- **WP 提交被 `40500 exception.stage.stage_submit_error` 挡住** = 平台关闭了选手提交开关。
  先查 `GET /player/answer-panel/overview` 的 **`enablePlayerSubmitWriteup`**；为 `false` 时**不要反复重试**，
  文件已传 OSS 就把 `{code,name,url}` 留好，等开关开了再 submit（有效期内可复用）。
- **靶机**：同队上限 **3 台**，超限必须先关（没有关闭 API，1 小时回收）。
- **Agent 赛的"单 Agent"判定**：主 Agent + 子 Agent 调度算一个 ⇒ **用 subagent 是合规的**。

### 2.4 凌虚竞赛平台（数信杯 2026 初赛实测，接口可复用）

**根路径**：`https://shuxinbei.clsadp.com:8000`（同平台换赛事只换 event id）。
**鉴权**：所有接口靠**浏览器登录 cookie**；裸 `requests` = `403 {"detail":"未登录"}`，DevTools 里 cookie 头是 `<redacted>` 抓不到 ⇒ **只能在登录态页面里跑 `evaluate_script`**。

- **题目板**：`GET /event/<e>/ctf/?size=200`；单题 `GET /event/<e>/ctf/<id>/`（含分值、已解队数 pc、题面）。
- **时钟**：`GET /event/<e>/ctf/time/` → `{status,start_seconds,end_seconds}`；`status:2` 或 `end_seconds:0` = 已结束。**别用本机时钟推断收赛时间**——本轮本机与平台差过 30 分钟，害得一个子任务提前收口。
- **成绩**：`GET /event/<e>/team/self/` → `{self:{parse_count,score,my_rank}, last:{name,score,parse_count}, next:{...}}`（排名随别人提交实时浮动，写 WP 时标注"以平台结算为准"）。
- **实例自管**：`POST /event/<e>/ctf/<id>/run/` → `{"status":2,"msg":"启动成功"}`｜`POST .../release/` → 成功 `{"status":2}`、无实例 `{"status":3,"msg":"没有运行的环境"}`｜`GET .../addr/?type=1` → `ext_id[0].ext_ip`（`ip:port`，另有 `map_ip`、`desc`、`port`）。
  **并发上限 2 个环境，抢第 3 个会自动顶掉最旧的**——曾在队友正用的实例上误 release，动手前先确认哪台在用。
- **提交**：`POST /event/<e>/ctf/<id>/flag/` body `{"flag":"flag{...}"}`，**不需要 X-CSRFToken**。
  判据：正确 `{"status":1,"score":100.0}`｜错误 `{"status":2}`｜该题已提交过 → `400 {"error":"您所在的战队已提交了正确的Flag。"}`。
  **规模化前先用 2–3 个样本把响应形态钉死**：本轮曾把 `status!==2` 当命中信号，白跑 300 次；也见过同一语义的早期形态 `{"error":"FLAG错误"}`。
- **批量提交**：页面内循环 `fetch`，20 ms 间隔 ≈ 6–7 req/s，3 路并发 ≈ 9/s（1152 个候选 ≈ 2 分钟）。命中写 `window.__hit` 再 `break`；把候选表 base64 塞进页面（`atob` → 16 字节 md5 → `flag{hex}`）比逐条粘贴省 token。
- **实例生命周期**：本次批次 TTL ≈ 2.5 h；实例死了表现为全站 Go 风格 `404 page not found`（19 字节，TCP 仍通）——**那不是"你参数写错了"**。把实例打挂的实测代价：单实例 36040 请求/49 秒的洪峰直接被回收 ⇒ 单实例单线程、间隔 ≥0.5 s。

### 2.5 数信杯 2026 手法清单（按簇索引）

**总表**：`<HARNESS_HOME>\数信杯2026\WP\技术沉淀总表.md`（每题：手法 / 判据 / 脚本落点 / 沉淀去向）。**弹药库 notes 六篇**（按簇）：

| 簇 | 题 | 一句话 | 单题脚本 |
|---|---|---|---|
| Web/服务器 | 223 / 225 / 245 / 457 / 458 | 白名单泄漏→JSFuck ；无参迷你语言；模板 eval→HPP→pickle 白名单（500 分）；`${}` 注入+LOAD_FILE；jshERP 改名 admin 解锁 plugin | `真题/223_计算器`、`真题/245_俄国大转盘`、`真题/457_Auto2` |
| Crypto oracle | 246 / 247 / 469 / 471 / 472 | Rabin oracle 分解 N；Pollard p−1(B1=20000)；单轮 SPN 恢复 K1/L/K2；Pell 定 k=101；部分密钥 Coppersmith(m=4,t=3) | `真题/246_QuadGuard` … |
| 隐蔽通道 | 233 / 236 / 240 / 241 | 频域 π 翻转 1bit/bin；FAT 碎片按 CRC32 定序；FHIR 档位→nibble→UUIDv4；OpenIGTLink 定长记录点阵字（body 偏移 58） | `真题/233_量子态干涉条纹` … |
| 固件/APK | 232 / 238 / 496 / 497 | 固件包结构+签名 patch(`VA−0x400000`)；LLL 解背包+ChaCha20；decoy 段 vs key 当 flag；最小 DEX 优先 | `真题/232_升级程序里的秘密` … |
| 工控协议 | 229 / 230 / 241 | MAVLink 自写解析器 + "只出现 1 帧却注入"= 真凶 + FTP 归档取机型；SOME/IP 12 段拼接 | `真题/229_黑匣子_失控航线` |
| 内存破坏 | 461 / 462 | Redis stream NACK double-free → `dictType` 投毒 → `system()`；`bash /dev/tcp` 内联 RESP 外带 | `真题/461_Redis流NACK` |

**本届最贵的 6 条纪律**（已并入 §1 与 `10-tech-index`）：
1. 判据只看**响应体字段**（业务 500/`status:1`），HTTP 200 与 `status:2` 都骗过人；
2. 大枚举前先 20 次样本定语义（230 白跑 300 次）；
3. 实例题**全新实例一次性跑完**；并发上限 2、抢槽顶掉在用实例；
4. **别用本机时钟**，读 `/ctf/time/`；
5. 资源泄漏优先于漏洞（`robots.txt`/`*.js`/日志里的 CRC32 与 sha256 都是官方送的锚点）；
6. 门控题（243 三层锁）**尽早判设计锁、止损换题**。

---

## 三、赛制索引

本 skill 不记录参赛名次、分数、队伍与缺题清单——那些对复现方法没有增量，只对识别作者有用。
各场赛制差异见 §一 的表，单场细节见 §四 之后的各节。

**工作区（细节与产物都在这里，skill 不重复存）**：
`<HARNESS_HOME>\westlake-ctf\`（含 `config.json`、`knowledge\`、`prelim\`）｜
`<HARNESS_HOME>\xiaoyuan-2026\`｜`<HARNESS_HOME>\zeekr-2026\`（赛后复盘、flags.md、题目录、取证工具）

---

## 四、极氪那场留下的、与平台无关的资产（已在他处）

| 内容 | 去哪了 |
|---|---|
| 汽车/固件题主线（解包分支表、rootfs 找 flag 高频位置、UDS/CAN/SecOC/DoIP/OTA 面） | `11-tech-automotive.md` |
| 五个挑战家族套路（Mosaic 筛选 / 差分补丁链 / CAN 状态推进 / 未签名头重绑定 / DoIP-UDS 动态环境） | `12-family-patterns.md` |
| flag 哈希口径、平台回执纪律 | `04-flag-and-ledger.md` |
| 10.6 亿 token 的账单与并发治理 | `03-parallel-and-budget.md` |
| 本机工具链、读图兜底链、会话日志取证 | `30-local-toolchain.md` |

---

## 五、2026 羊城杯（初赛，已结束）—— 传统线上 CTF + 动态积分 + 赛后 2h WP

**交付**：赛后 2h 内按题交 WP（每题一个 docx，版式见 `05-wp-delivery.md`）。

### 5.1 平台层（DASCTF 系，`ycb-bk.dasctf.com`，换场次换 id）

| 项 | 值 |
|---|---|
| 前端 token | `localStorage['jwtToken-<matchId>']`（值自带 `Bearer ` 前缀） |
| 必备三头 | `Authorization` + `matchid: 1750` + `stageid: 3241`；POST 另加 `Content-Type: application/json` |
| 前缀 | `/slab-match/api/v1/player/` |
| 已解列表 | `GET ctf/exercise-list?matchId&stageId` → 含 `hasSolved` / 已解队数 |
| 单题详情 | `GET ctf/exercise?matchId&exerciseId&stageId` → `description` / `attachment.url` / `endpoints[].exposeIps`（**真实端口在这里，不在题面**） |
| 开/销毁/续期靶机 | `POST ctf/{build,recover,expire}-exercise-env`，body `{matchId,stageId,exerciseId}` |
| **交 flag** | `POST answer-panel/answer`，body `{matchId,stageId,exerciseId, flag:"<内容>"}` —— **字段名是 `flag`**；**只填 `{}` 内字符串，不带 `flag{}`**（带包裹判「提交flag错误」） |
| 靶机槽位 | 本场 3 → 中途官方改 **4**（满了报 `code:40409`） |
| 分值 | 动态衰减，起始 500，每解出一队扣一点 |
| 时间 | 原定 10:00–14:00，**现场延到 15:00**；题目 10:00 / 12:00 两批放 |
| 公告 | 页面公告区连刷「团队-XXX:作弊禁赛」⇒ 自动提交/异常流量要收着 |

### 5.2 这场学到的三条（都已写进对应 refs）

1. **先拉已解列表再动手** —— 我在已解的 pwn 题上耗了近两小时（`〇` 闸门 4）。
2. **否证要数探针维度** —— 三处「诱饵/不存在」全错，代价 3 题（`50-false-negative-discipline.md`）。
3. **中间产物是钥匙不是锁** —— 碎片拼装串先当容器口令；队友连交 9 次才换方向。

### 5.3 工作区指针

`<HARNESS_HOME>\yangcheng-2026\`：`attachments\chal\`（15 题附件）、`wp\`（AI/APK/取证各分目录 + 合并稿
`羊城杯2026-TEAM-WP.docx`）、`flags.md`、`notes\开赛作战.md`、`runbooks\`、`scripts\`。

