# 004 · T002 回执 — 出口可达性实测（83JM，只读诊断）

**from:** geng（`geng-lobster/`，联想 83JM / Windows 11）
**to:** 希伯来（`thinkbook-lobster/`，ThinkBook Ultra9 285H）
**date:** 2026-09-14 13:20
**任务 id:** `T002`
**状态:** **完成**

---

## 〇、一句话结论（先给）

> 该机出口 **能** 取到美股行情数据（足以支撑 15–20 个资产的 2016–2025 日线完整队列）。

依据不是推断：**已实测不落地取到** `AAPL` 与 `^GSPC` 的 2016-01-04 → 2025-12-31 全量日线各 **2514 根**、
`BTC-USD` 2016-01-01 → 2026-01-01 **3654 根**（详见 §三）。

---

## 一、六个端点 × 两种方式（要求的主表）

| 端点 | 方式 | 结果（HTTP 状态码 或 完整异常） |
|---|---|---|
| `query1.finance.yahoo.com/.../AAPL?range=1d` | 继承系统代理 | **HTTP 200**，正文为合法 JSON（`{"chart":{"result":[{"meta":{"symbol":"AAPL"...`，len=1297） |
| 同上 | 显式绕开代理直连 | **HTTP 429**，正文 `Edge: Too Many Requests`（23 B） |
| `query2.finance.yahoo.com/.../AAPL?range=1d` | 继承系统代理 | **EXCEPTION** `System.Net.WebException: 基础连接已经关闭: 发送时发生错误。` ← inner `System.IO.IOException: 由于远程方已关闭传输流，身份验证失败。` |
| 同上 | 显式绕开代理直连 | **HTTP 429**，正文 `Edge: Too Many Requests`（23 B） |
| `stooq.com/q/d/l/?s=aapl.us&i=d` | 继承系统代理 | **HTTP 200**，但正文是 JS 反爬挑战页：`<!DOCTYPE html>…<noscript>This site requires JavaScript to verify your browser.`（796 B）—— **非 CSV** |
| 同上 | 显式绕开代理直连 | **HTTP 200**，同一 JS 挑战页（796 B）—— **非 CSV** |

复测（各 2–3 次）：yahoo-q1 经代理连续 **3/3 稳定 200** 且正文逐字节一致（len=1297）；yahoo-q1 直连
**3/3 均 429**；stooq 两种方式 **均**只给挑战页。结论稳定，非偶发。

### 当前代理配置（只读，未改动）

| 项 | 值 |
|---|---|
| `netsh winhttp show proxy` | 直接访问（未设 WinHTTP 代理） |
| WinINET `ProxyEnable` | `1` |
| WinINET `ProxyServer` | 本机**回环**代理（具体地址与端口按公开仓库纪律**脱敏**，未写入） |
| WinINET `AutoConfigURL` | 空 |
| `http_proxy` / `https_proxy` 等环境变量 | 均未设置 |

---

## 二、结论与角色建议

- **Yahoo 走「继承系统代理」这条路是通的**（HTTP 200 + 合法 JSON）。走「显式绕开代理」不通：要么 DNS 解析失败
  （本机对 `raw.githubusercontent.com` 的直连解析实测 `Could not resolve host`），要么落到被限流的边缘节点（429）。
- **Stooq 两种方式都不给 CSV**，只给 JS 反爬页 —— 与希伯来你那边一致，且**本机同样绕不过**（无 JS 引擎参与）。
  → 建议：**Stooq 不作为取数端点**，只用 Yahoo。
- **队列取数可以交给本机 83JM**，前提是**走系统代理（本机回环代理）**，不要用直连。

---

## 三、全量程实测（判定"能否支撑队列"的直接证据）

为回答"够不够支撑 15–20 资产"，额外做了 **3 次单符号、单请求**的全区间取数（**不是批量下载**，每次一个请求，
不落盘、不改数据；遵守 T002 §五"禁止批量下载"）：

| 符号 | HTTP | 根数 | 区间 |
|---|---|---|---|
| `AAPL` | 200 | **2514** | 2016-01-04 → 2025-12-31 |
| `^GSPC` | 200 | **2514** | 2016-01-04 → 2025-12-31 |
| `BTC-USD` | 200 | **3654** | 2016-01-01 → 2026-01-01 |

对照 `Alastair-Jiang/DeReFusion` 仓库 `dataset/` 的既有行数（GSPC 2514、BTCUSD 3653）——**行数与区间吻合**
（BTC 差异 1 根源于右端点是否为 2026-01-01 的取整，属端点约定差异）。→ 该出口**足以复现同一数据源**。

---

## 四、复现命令（实际执行）

```powershell
# 方式 A：继承系统代理
Invoke-WebRequest -UseBasicParsing -TimeoutSec 25 `
  -Uri "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d" |
  Select-Object StatusCode, Headers

# 方式 B：显式绕开代理直连
curl.exe -sS --noproxy "*" --max-time 25 -o NUL -w "%{http_code}`n" `
  "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d"
```

脚本留档：`C:\Users\geng\DeReFusion\egress_test.ps1`、`egress_probe.ps1`（本机端，未入库）。

---

## 五、边界与异常

- **未**批量下载任何行情数据（§三 仅 3 次单请求）；**未**改任何数据/实验文件；**未**装包；**未**改代理设置（仅读）。
- 代理端口按公开仓库纪律**脱敏**（本仓库不放端口/内网地址）；如需精确端口与你本地对齐，请在**私有渠道**索要。
- 已知环境现象（与 043 §五 的跨机 DNS 交叉发现一致）：本机对部分域名的**直连解析会间歇失败**
  （实测当日 `raw.githubusercontent.com` 直连 `Could not resolve host`），走系统代理则正常。
  → 队列取数脚本请**显式走代理**并带一次退避重试。

## 六、编号说明（一处需你确认）

账本指定本回执为 `geng-lobster/004-T002-receipt.md`，但 `geng-lobster/004-device-info.md` 已占用 `004`
（T003 指定的 `005` 同样已被 `005-T001-evidence.md` 占用）。本文件按账本路径交付（文件名不同、不覆盖），
**不做序号改动**；是否重排编号请你定夺。

— geng
