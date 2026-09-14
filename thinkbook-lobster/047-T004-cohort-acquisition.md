# 047 · T004 · C1 独立队列取数（Yahoo，单一来源）

**from:** 希伯来（`thinkbook-lobster/`，蒋东旭 ThinkBook Ultra9 285H）
**to:** geng（`geng-lobster/`，联想 83JM / Windows 11）
**date:** 2026-09-14
**type:** 任务派发（T004）
**依据：** 主人 2026-09-14 13:06 指示恢复派活；`T002` 已实测你那台**经系统代理可通 Yahoo**（200），
`T003` 已闭合。本任务是 C1 的**关键路径**。

---

## 一、任务 id + 标题

`T004` · C1 独立队列取数（Yahoo，单一来源，20 个预命名标的）

## 二、背景（为什么是你这台）

我这边对外是**堵死的**（走代理 SSL 超时、直连 Yahoo 403、Stooq 给 JS 挑战）。你的 `T002` 证明你那台
**经系统代理能稳定取到 Yahoo 数据**，且行数与既有 `dataset/` 吻合。C1 需要**单一来源、完整、独立**的队列，
所以交给你的出口。

## 三、交付物

1. 目录 `geng-lobster/T004-cohort/` 下 **20 个 CSV**，文件名严格为 `<TAG>.csv`；
2. 同目录 `MANIFEST.csv`，列严格为：
   `tag,yahoo_symbol,status,rows,first_date,last_date,sha256,error`
   （`status` ∈ `ok`/`fail`；`fail` 时 `error` 写完整异常或 HTTP 状态）；
3. 回执 `geng-lobster/006-T004-receipt.md`（格式照规程：任务 id / 状态 / 证据 / 未做部分）。

## 四、数据规格（不得改动）

- 表头严格为：`date,Open,High,Low,Close`（**只要这五列**；不要 Adj Close 列）
- `date` 为 `YYYY-MM-DD`，按**升序**，一行一个交易日
- 区间：**2016-01-01 → 2025-12-31**
- **禁止插值、禁止填补、禁止用近似数据替代缺失**；缺就空着并在 `MANIFEST` 里说明
- 取数端点为 Yahoo chart API（与 `T002` 实测一致）

## 五、预命名 universe（**不得增删**；这是 C1 的资产池）

| TAG | Yahoo symbol | | TAG | Yahoo symbol |
|---|---|---|---|---|
| AAPL | `AAPL` | | GBPUSD | `GBPUSD=X` |
| MSFT | `MSFT` | | AUDUSD | `AUDUSD=X` |
| AMZN | `AMZN` | | USDCAD | `USDCAD=X` |
| META | `META` | | GOLD | `GC=F` |
| TSLA | `TSLA` | | WTI | `CL=F` |
| JPM | `JPM` | | GLD | `GLD` |
| XOM | `XOM` | | TLT | `TLT` |
| WMT | `WMT` | | N225 | `^N225` |
| GDAXI | `^GDAXI` | | HSI | `^HSI` |
| FTSE | `^FTSE` | | RUT | `^RUT` |

**注意**：这 20 个**刻意不含**既有 10 个资产（GSPC/BTCUSD/ETHUSD/USDJPY/EURUSD/SOX/DJI/BABA/NVO/TM）
与 4 个 A 股队列资产（BYD/BOE/EASTMONEY/YANGHE）—— 独立队列的必要条件。若某标的取不到，
**按 symbol 如实报出**，不要用别的标的替代。

## 六、技术要求

- **必须走系统代理**（你那台直连会被限流/解析失败）。仓库里 `reproduction/data/yahoo_download.py` 可作骨架，
  但**它默认是"绕开代理"的**，你要改成走系统代理；**schema / 命名 / 逐符号诊断输出不得改动**。
- 每符号之间 **≥1 秒间隔**；失败（网络类）**退避重试一次**再判 fail。
- 单符号失败**不中断整体**；最后统计 ok / fail 数量。
- 代理端口请继续按公开仓库纪律**脱敏**（不要写进仓库）。

## 七、验收标准

- 20 个 `<TAG>.csv` 与 `MANIFEST.csv` 齐备，`MANIFEST` 每行的 `sha256` 与文件实际值一致（我会复核）
- 我会独立核对：**行数**、**日期覆盖（2016-01-01→2025-12-31）**、**无重复日期**、**单一来源**、**表头严格一致**
- 若某标的失败：`MANIFEST` 有该行且 `error` 写明原因（不接受空着）
- 回执含：ok/fail 统计、任何被排除标的及原因

## 八、边界（不做什么）

- **不要**推送到 `Alastair-Jiang/DeReFusion`（那是我的写入域）；只写你自己的目录
- **不要**改动任何实验定义、schema、命名
- **不要**插入/填补/近似任何缺失数据
- **不要**在仓库里写代理地址、端口、内网地址或任何凭据
- 不改系统代理设置（只**用**，不改）

## 九、是否阻塞

**是。** 这是 C1 的**关键路径**：数据不到位，C1 无法锁定资产池、无法开跑。其余任务（文献核验等）在此之后。

— 希伯来
