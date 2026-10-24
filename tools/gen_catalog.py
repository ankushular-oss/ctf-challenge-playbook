# -*- coding: utf-8 -*-
"""Generate refs/CATALOG.txt: one line per refs file with 何时读 + grep 关键词 + 实测大小."""
import io, os, glob, datetime

REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'refs')
OUT = os.path.join(REF, 'CATALOG.txt')

META = {
    '01-tempo-and-checklist.md': (
        '开赛前 + 每场分诊时',
        '赛制 战术 动态积分 抢首杀 首杀 时间盒 15分钟 分诊 回扫 检查单 停止条件 赛前 赛后 WP窗口 提示词 轮换',
    ),
    '02-evidence-discipline.md': (
        '卡住时 + 赛前默读一遍',
        '证据 静默失败 自诊断 marker 记账 tries.log 错误模式 枚举 候选 假设 时间盒 我被什么咬 踩坑'),
    '03-parallel-and-budget.md': (
        '开赛前定并发 + 每次想"再开一个会话"时',
        '并行 子agent 任务卡 fresh spawn 上下文 token 预算 账单 并发上限 收口 延迟 TRANSPORT 黑板 配额 动态靶机'),
    '04-flag-and-ledger.md': (
        '拿到第一个 flag 前 + 每次要提交/核对台账时',
        'flag 口径 哈希 sha256 大写 hex 台账 总账 回执 flags.md 提交 候选 平台判正 AI声明 一票否决'),
    '05-wp-delivery.md': (
        '要交 WP / 题解 / 解题报告时',
        'WP WriteUp 题解 docx 版式 参考件 复刻 截图 清晰度 shot.ps1 PrintWindow x64dbg OCR 自检 模板'),
    '10-tech-index.md': (
        '分诊后准备动手 + 卡住找候选方向时（先新鲜分析）',
        'Reverse Pwn Web Crypto Misc 取证 应急 手法 工具 shellcode 堆 UAF tcache gadget WAF 注入 SSTI 反序列化'),
    '11-tech-automotive.md': (
        '题面出现固件/ECU/T-Box/车机/诊断/CAN 时',
        '汽车 车联网 固件 binwalk 解包 squashfs ubifs jffs2 rootfs UDS CAN SecOC DoIP SOME-IP OTA IVI T-Box ECU 诊断 DID'),
    '12-family-patterns.md': (
        '认出题目"家族指纹"时',
        '家族 Mosaic 筛选 页 诱饵 CRC 差分 补丁链 链式摘要 CAN 状态推进 重绑定 签名 oracle padding DoIP 解码'),
    '20-competition-notes.md': (
        '提到极氪/西湖论剑/霄元杯，或要打新比赛判断赛制形态时',
        '极氪 Zeekr 西湖论剑 DASCTF 霄元杯 星域之盾 平台 红线 赛制 形态 AI声明 邮箱 WP提交 手法清单 接口 错误码'),
    '30-local-toolchain.md': (
        '需要用本机工具时（别猜路径）',
        '工具链 WSL binwalk unsquashfs IDA JADX tshark MCP VLM OCR WinRT tesseract session-forensics 取证 /tmp grep -a'),
    '99-reusable-highlights.md': (
        '想直接抄现成招时',
        '亮点 可复用 后门 复刻靶机 marker DNS TXT 弱DH 参数敏感性 队友资料 复核 seccomp'),
}


def main():
    files = sorted(glob.glob(os.path.join(REF, '*.md')))
    rows = []
    for p in files:
        n = os.path.basename(p)
        txt = io.open(p, encoding='utf-8', errors='replace').read()
        rows.append((n, os.path.getsize(p), txt.count('\n') + 1, META.get(n, ('-', '-'))))

    total = sum(r[1] for r in rows)
    L = []
    L.append('CTF skill 目录（refs/CATALOG.txt）')
    L.append('=' * 100)
    L.append('')
    L.append('用途：**不要为了"了解全貌"把 refs 全读一遍**。先在这里 grep，再只读命中的那一个文件。')
    L.append('')
    L.append('  用法（PowerShell）：')
    L.append('    Select-String -Path "<本skill>\\refs\\CATALOG.txt" -Pattern "UDS"   # 找内容在哪')
    L.append('    Select-String -Path "<本skill>\\refs\\CATALOG.txt" -Pattern "何时读"  # 只看时机')
    L.append('  用法（niubash/Git Bash）：')
    L.append('    grep -i "UDS" "<本skill>/refs/CATALOG.txt"')
    L.append('')
    L.append(f'入口 SKILL.md 约 6 KB；refs 合计 {total:,} 字节 / {len(rows)} 个文件——**按需读，别整读**。')
    L.append('本文件由脚本生成（关键词表在生成脚本里），新增 refs 文件后请同步补一行。')
    L.append('生成时间：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    L.append('')
    L.append('-' * 100)
    L.append('')
    L.append(f'{"文件":<32}{"大小":>9}  何时读 / grep 关键词')
    L.append('-' * 100)
    for n, size, lines, (when, kw) in rows:
        L.append(f'{n:<32}{size:>7,}B  [{lines} 行]')
        L.append(f'{"":<32}{"":>9}  何时读：{when}')
        L.append(f'{"":<32}{"":>9}  关键词：{kw}')
        L.append('')
    L.append('-' * 100)
    L.append('')
    L.append('其它入口（不在本目录）')
    L.append('  ..\\SKILL.md                 统一入口：触发词 + 三条硬闸门 + 路由表')
    L.append('  ..\\..\\muteki-blackboard\\    多 agent 共享事实板（独立 skill，未合并）')
    L.append('')
    L.append('历史备份')
    L.append('  <HARNESS_HOME>\\backups\\skills-ctf-<date>\\   合并前 5 个 skill 的整目录')
    io.open(OUT, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(L))
    print('wrote', OUT, os.path.getsize(OUT), 'bytes;', len(rows), 'files;', total, 'bytes total')


main()

