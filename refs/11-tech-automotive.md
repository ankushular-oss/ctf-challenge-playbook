# 11 · 汽车 / 车联网 / 固件题主线

> **何时读**：题目是固件/车机/ECU/T-Box 镜像，或题面出现 UDS / CAN / SecOC / DoIP / SOME-IP / OTA / Secure Boot / RKE / ADAS 等汽车词汇时。**固件题 90% 走同一条主干**，本节就是那条主干 + 解包失败的分支清单。
> 来源：`zeekr-ctf-2026` §三（技术手法层：汽车固件题主线）全部小节（3.1–3.5）。

**交叉引用**：家族套路模板（Mosaic 筛选 / 差分补丁链 / CAN 状态推进 / 未签名头重绑定 / DoIP-UDS 动态环境）→ `12-family-patterns.md`｜固件链工具实测路径 → `30-local-toolchain.md`。

---

## 3.1 解题主干（90% 的固件题走这条）

```
附件 → 识别( file/binwalk/熵 ) → 解包( 递归 ) → 认文件系统( squashfs/ubifs/jffs2/ext4/cpio )
     → 在 rootfs 里找"题目问的那件东西" → 需要时用提取到的密钥/凭据去解下一层或连动态环境
```

**一条命令起步**（脚本已写好，别再手敲 binwalk 参数）：

```powershell
# 提取（自动 binwalk -e -M 递归 + squashfs/ubi/jffs2/7z/sparse 兜底）
wsl -d Ubuntu-22.04 -u root -e bash /mnt/d/<HARNESS_DIR>/zeekr-2026/tools/fw-extract.sh "D:\path\to\firmware.bin"
# 搜索（flag/口令/私钥/sqlite/URL/汽车关键词/大文件清单）
wsl -d Ubuntu-22.04 -u root -e bash /mnt/d/<HARNESS_DIR>/zeekr-2026/tools/fw-hunt.sh "/mnt/d/.../<firmware>_extracted"
```

---

## 3.2 解包失败时的分支清单（**按顺序试，别死磕一条**）

| 症状 | 处理 |
|---|---|
| binwalk 认出 squashfs 但解不开 | 换压缩机：`unsquashfs -lz4` / `-lzo` / `-lzma` / `-xz` / `-gzip`；仍失败则找 vendor 魔数/填充 |
| 头部异或/加密 | 常见**单字节 XOR** 或 **16 字节 AES-CBC**，密钥多在 U-Boot/bootloader 里；先看熵与重复块 |
| UBI/UBIFS | `ubireader_extract_images` + `ubireader_extract_files`（WSL 已装） |
| JFFS2 | `jefferson`（WSL 已装） |
| ext4 / cramfs / cpio / tar / iso | `7z x`（Windows 与 WSL 都有）；cramfs 用 `cramfsck -x` |
| Android 车机 | `simg2img` 转 sparse → `7z x` 或 `debugfs`；APK 用 JADX（MCP 可用） |
| U-Boot uImage / FIT | 去掉 **64 字节头**；FIT 用 `dtc -I dtb -O dts` 看结构 |
| ECU 固件（Intel HEX / SREC） | `srec_cat in.hex -intel -binary -o out.bin`；再按 MCU 架构反汇编 |
| NAND 裸备份 | 先判断 **OOB/页大小**，去掉 spare 区再解包 |

---

## 3.3 从 rootfs 里"找 flag"的高频位置

| 类别 | 位置与打法 |
|---|---|
| **账号口令** | `/etc/passwd`、`/etc/shadow`（哈希 → `hashcat`/`john`/在线已知明文对照）、`/etc/*.htpasswd`、web 后台默认口令、`/etc/config/*` |
| **硬编码密钥/证书** | `*.pem` / `*.key` / `*.p12` / `*.jks`、`-----BEGIN * PRIVATE KEY-----`、`.so`/二进制里的 32/64 位十六进制常量、AES/DES 表 |
| **数据库** | `*.db` / `*.sqlite`（先 `.tables` 再 `select`；口令/轨迹/日志常在里面） |
| **脚本与配置** | `/etc/init.d/*`、`*.sh`、nginx/lighttpd 配置、`/usr/sbin/*` 启动参数 |
| **Web 根目录** | `/www`、`/web`、`/htdocs`、`/usr/share/web` —— 后台路径 + 凭据常在旁边 |
| **flag 本体** | `/flag`、`/flag.txt`、`/etc/flag`、环境变量、`/root/`、版本字符串旁 |
| **反直觉但常见** | flag 不直接躺在文件里，而要**用提取到的密钥解密某段密文**，或**用提取到的凭据登录动态环境**再拿 flag —— 这时"提取到的字符串"是下一步的输入，**别急着当答案提交** |

---

## 3.4 汽车/车联网特有面（题面出现这些词就往这里想）

| 面 | 考点与实测参数 |
|---|---|
| **UDS（ISO 14229）诊断** | `0x10` 会话控制、`0x27` SecurityAccess（**seed/key 算法**常是核心考点）、`0x22`/`0x2E` 读写 DID、`0x31` 例程、`0x34-0x37` 传输。**两种会话/安全等级**决定能做什么。现场手册 → `12-family-patterns.md` 家族 5 |
| **CAN 总线** | CAN ID 语义、报文计数/校验（**checksum 常是前 7 字节异或或查表**）、重放/伪造报文触发某动作；日志用 `candump` 文本或 pcap（`tshark -d candump` 解析）。状态推进类模板 → `12-family-patterns.md` 家族 3 |
| **SecOC** | **CMAC-AES128 + 新鲜度值（Freshness Value）**；考点常是"找出密钥 / 绕过校验" |
| **DoIP（ISO 13400，TCP/UDP 13400）/ SOME-IP（SD 30490）** | 车云/车内以太网服务；**动态环境题高频**。完整帧格式、路由激活/诊断寻址的实测参数与两条方法论 → `12-family-patterns.md` 家族 5；现场工具 `tools\doip_uds.py`（`discover` 自动引导）+ 离线练习靶机 `tools\mock_doip.py` |
| **T-Box / 车云交互** | MQTT / HTTPS 上报，**凭据与证书在固件里** |
| **车机（IVI / Android）** | APK 逆向（JADX-MCP）、签名校验绕过、WebView 桥、su/调试口 |
| **OTA** | 签名校验流程、回滚策略、升级包格式（常是"改包 + 伪造签名/绕过校验"） |
| **Secure Boot / U-Boot** | `bootargs`、`bootcmd`、verified boot、解锁命令（如 `fastboot oem unlock` 类） |
| **钥匙 / 无钥匙进入** | RKE 滚动码（**KeeLoq**）、BLE/WiFi 车控、PIN 码 |
| **ADAS / 传感器** | 感知参数、车速/阈值类判断（公开赛里出现过"最低车速阈值"这类逆向题） |

### OTA 类实例：极简二进制协议 + Padding Oracle（极氪 397《OTA Shadow Oracle》）

协议 = `u32BE len` 分帧 + opcode，全部行为如下：

| 元素 | 实测值 |
|---|---|
| op1 | 下发 **48 B 令牌**：`IV ‖ AES-CBC(key, "role=user  sid=<8hex>")` |
| op2 | **PKCS#7 padding oracle**：`00 01` = 合法 / `00 00` = 非法 |
| op3 | 凭令牌鉴权 |

打法（**8192 次预言机查询，零爆破**）：预言机查询还原 `D(C1)/D(C2)` → 解出明文 →
**CBC 可延展性只改 IV** 伪造 `role=admin` → flag。
完整手法（含用命中率/截断实验钉死预言机语义）见 `99-reusable-highlights.md` 第 12 条。

---

## 3.5 「附件 + 动态环境」题怎么打

1. 先把附件**完整解包** —— **动态环境的账号/密钥/协议格式基本都在附件里**。
2. 连上环境先**只做被动观察**：banner、欢迎语、需要的字段格式、能否读不能写。
3. 按题目要求的**那一个动作**去做（一次），拿结果；**不要遍历、不要爆破、不要扫描**。
4. 环境有倒计时/并发上限：**用完就关**，别占着；一次不成就回附件里找线索再动手。

> ⚠️ 合规前置：面向任何远端目标动手前**先读该赛事的红线与授权范围**。
> 反面教材：极氪 397 开题只有一行 `nc`，未加载平台规则就先黑盒枚举，读到"动态环境不要遍历/爆破/扫描"时已发出约 **7000 万次**请求。
> **"我能跑通" ≠ "我可以跑"**；批量请求前先给自己一个请求预算。
