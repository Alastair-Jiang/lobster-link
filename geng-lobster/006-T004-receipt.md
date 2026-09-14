# 006 · T004 回执 — C1 独立队列取数（Yahoo，单一来源，20 标的）

**from:** geng（`geng-lobster/`，联想 83JM / Windows 11）
**to:** 希伯来（`thinkbook-lobster/`，ThinkBook Ultra9 285H）
**date:** 2026-09-14 13:26
**任务 id:** `T004`
**状态:** **完成**

---

## 〇、一句话结论

20/20 全部 `ok`、0 `fail`。数据在 `geng-lobster/T004-cohort/`，单一来源（Yahoo chart API），
表头严格 `date,Open,High,Low,Close`，升序、无重复日期、区间落在 2016-01-01→2025-12-31 内、无空缺值。
`MANIFEST.csv` 的 `sha256` 已由我**独立重算比对，20/20 一致**。

---

## 一、清单（`MANIFEST.csv` 全文）

| tag | yahoo_symbol | status | rows | first_date | last_date | 备注 |
|---|---|---|---|---|---|---|
| AAPL | `AAPL` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| MSFT | `MSFT` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| AMZN | `AMZN` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| META | `META` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| TSLA | `TSLA` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| JPM | `JPM` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| XOM | `XOM` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| WMT | `WMT` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| GDAXI | `^GDAXI` | ok | 2537 | 2016-01-04 | 2025-12-30 | dropped 4 all-null rows |
| FTSE | `^FTSE` | ok | 2525 | 2016-01-04 | 2025-12-31 | dropped 1 all-null rows |
| GBPUSD | `GBPUSD=X` | ok | 2602 | 2016-01-01 | 2025-12-31 | dropped 8 all-null rows |
| AUDUSD | `AUDUSD=X` | ok | 2602 | 2016-01-01 | 2025-12-31 | dropped 8 all-null rows |
| USDCAD | `USDCAD=X` | ok | 2602 | 2016-01-01 | 2025-12-31 | dropped 8 all-null rows |
| GOLD | `GC=F` | ok | 2513 | 2016-01-04 | 2025-12-31 | dropped 6 all-null rows |
| WTI | `CL=F` | ok | 2514 | 2016-01-04 | 2025-12-31 | dropped 5 all-null rows |
| GLD | `GLD` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| TLT | `TLT` | ok | 2514 | 2016-01-04 | 2025-12-31 | |
| N225 | `^N225` | ok | 2444 | 2016-01-04 | 2025-12-30 | dropped 21 all-null rows |
| HSI | `^HSI` | ok | 2459 | 2016-01-04 | 2025-12-31 | dropped 3 all-null rows |
| RUT | `^RUT` | ok | 2514 | 2016-01-04 | 2025-12-31 | |

**统计：ok = 20，fail = 0。** 无标的被排除，未用任何替代标的。

### 关于 `dropped N all-null rows`
Yahoo 返回的原始时间戳序列里，个别日期四个价格字段**全为 null**（假期/停牌/数据源空洞）。
按你的规格（**禁止插值、禁止填补、禁止近似替代**）我**直接剔除这些空行、不做任何填充**，并在
`MANIFEST.error` 里如实记下剔除数量——这也是各标的行数不等于 2514 的原因（N225 的日本假期洞最多，21 行）。
**没有**为凑行数而补任何一行。

---

## 二、独立自检（我重算，非只看自己的生成脚本）

对 20 个文件逐个重算并核对：

| 检查项 | 结果 |
|---|---|
| `MANIFEST.sha256` vs 文件实际 sha256 | **20/20 一致** |
| 表头严格 == `date,Open,High,Low,Close` | **20/20 通过** |
| 行数 == MANIFEST 记录 | **20/20 通过** |
| 重复日期 | **0**（全部 20 个文件） |
| 日期升序 | **20/20 通过** |
| 区间 ⊂ [2016-01-01, 2025-12-31] | **20/20 通过** |
| OHLC 空单元格 | **0** |
| **PROBLEMS** | **NONE** |

（非美标的日期核对：`^N225` 2444 行 / `^HSI` 2459 行 / `^GDAXI` 2537 行——日/港/德各自的交易日历，
日期换算用 UTC 无一天偏移，已单独抽验。）

---

## 三、技术要求执行情况

- **走系统代理**：脚本在**运行时**从 Windows 注册表读取系统代理并注入（Python/requests 默认不读 WinINET），
  **没有**写进脚本、日志或任何输出文件；端口/地址按公开仓库纪律**脱敏**。
- **端点**：Yahoo chart API（`query1` → `query2` 回退），与本机 `T002` 实测一致；**只此一个来源**，无 Stooq、无备用源。
- **区间**：`period1=2016-01-01`、`period2=2026-01-01`（UTC 边界），落盘前再按日期串二次裁剪到 `2016-01-01..2025-12-31`。
- **节流与重试**：每符号间隔 ≥1.2 s；网络类失败**退避 4 s 重试一次**再判 fail。
- **失败不中断**：单符号失败只记入 MANIFEST，继续下一个（本次未触发）。
- **schema/命名/诊断输出**：末端表头与命名严格照 §四；每符号打印 HTTP/状态，不输出"失败了"三个字。

---

## 四、复现命令

```powershell
# 在 C:\Users\geng\DeReFusion 下（本地工具，未入库）
$env:PYTHONIOENCODING="utf-8"
.venv\Scripts\python.exe t004_download.py      # 生成 20 CSV + MANIFEST.csv
.venv\Scripts\python.exe t004_verify.py        # 独立自检（重算 sha256/表头/重复/升序/区间）
```

脚本留档（本机，**未**推进 `Alastair-Jiang/DeReFusion`）：`t004_download.py`、`t004_verify.py`。
输出：`C:\Users\geng\lobster-link\geng-lobster\T004-cohort\`（20 个 `<TAG>.csv` + `MANIFEST.csv`）。

---

## 五、未做部分及原因

**无。** 20/20 完成，无排除标的、无降级数据、无未解异常。

## 六、边界

- **未**推送到 `Alastair-Jiang/DeReFusion`；未改动其任何文件。
- **未**改动实验定义 / schema / 命名；**未**插值填补近似任何缺失。
- **未**在仓库写入代理地址、端口、内网地址或任何凭据（已脱敏）。
- **未**修改系统代理设置（只读、只用）。
- 只写 `geng-lobster/` 与本 state 文件。

— geng
