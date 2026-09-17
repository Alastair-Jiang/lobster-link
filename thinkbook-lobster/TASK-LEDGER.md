# TASK-LEDGER · 任务编号账本（唯一权威）

**编号权：** 希伯来（`thinkbook-lobster/`，ThinkBook）。geng 不自行编号。
**规程：** `thinkbook-lobster/040-to-geng-task-protocol.md`
**更新时间：** 2026-09-14 13:30 (CST)

## 硬规则

1. 任务**整体**交一台机器，不许为了分摊算力而拆解。
2. 默认先压 geng 那台（83JM）；确实跑不动或环境不匹配才由 ThinkBook 补，且分工理由写进任务文件。
3. 派 `T(n+1)` 前必须核 `T(n)` 回执；非"完成"则停发 + 发 `*-EXCEPTION.md`。
4. 全局一个序列，下一个编号在下方明确标出。

## 状态取值

`未发布` / `已发布-待回执` / `完成` / `部分完成` / `未完成` / `阻塞` / `已取消`

## 文件序号约定（2026-09-14 确定）

**文件名序号 ≠ 任务号**，两套体系独立。派活时由我指定一个**未被占用的文件序号**；**账本以"回执路径"为准**，
不以序号推断任务状态。已交付文件不因序号冲突而重排（`004-device-info.md`、`005-T001-evidence.md` 保持原样）。

## 账本

| id | 标题 | 交付方 | 发布日 | 状态 | 回执文件 |
|----|------|--------|--------|------|----------|
| `T001` | DeReFusion 组件消融实验（GSPC + BTCUSD, T=24, 6 run） | geng（83JM） | 2026-09-12 | **已取消（主人指示）；工作已完成，证据已入库** | ✅ `geng-lobster/005-T001-evidence.md`（`71808bc`） |
| `T002` | 出口可达性实测（Yahoo/Stooq，只读诊断） | geng（83JM） | 2026-09-14 | **完成** | ✅ `geng-lobster/004-T002-receipt.md` |
| `T003` | 独立复算 F1 裁决（容量受控广度面板） | geng（83JM） | 2026-09-14 | **完成** | ✅ `geng-lobster/005-T003-receipt.md` |
| `T004` | C1 独立队列取数（Yahoo，单一来源，20 预命名标的） | geng（83JM） | 2026-09-14 | **完成** | ✅ `geng-lobster/006-T004-receipt.md` + `T004-cohort/`（20 CSV + MANIFEST） |
| `T005` | **C1 面板执行**（20 资产 × 2 臂 × 3 seeds = 120 run，**离线可跑**） | geng（83JM） | 2026-09-14 | **完成（120/120 ok、0 fail、0 stall；两臂各 60）** | ✅ `geng-lobster/007-T005-receipt.md` |

### T002 结论（已采纳）

- Yahoo **经系统代理 = 200**（3/3 稳定、正文逐字节一致）；**直连 = 429**；**Stooq 两种方式都只给 JS 挑战页** → **Stooq 弃用**，本队列只用 Yahoo。
- 全场量单请求实测：AAPL 2514 根、`^GSPC` 2514 根、`BTC-USD` 3654 根 → 与既有 `dataset/` 行数吻合 ⇒ 该出口**能复现同一数据源**（C1 的"同源"前提因此成立）。

### T003 结论（已采纳）

- 独立复算：**成功**；与 `reports/evidence_closure/21_f1_result.md` **逐格一致、差异为空**。
- 额外自检（超出我要求，予以记录）：`dMSE = MSE_N − MSE_L` 成立（792 行中 106 行严格相等，其余相对差 ≤3e-8，float32 存储所致）。
- 工程细节：输入 CSV 带 UTF-8 BOM，读取须 `encoding="utf-8-sig"`。

### T004 结论（已采纳，队列已锁定）

- 20/20 `ok`、0 `fail`；单一来源 Yahoo chart API。
- **我方独立校验**（`reproduction/analysis/c1_cohort_validate.py`）：表头/日期解析/**升序**/**无重复**/行数==MANIFEST/**哈希 20/20 一致**/覆盖窗口/与既有资产**零重叠**/provenance 已声明 → `all 20 files pass`，退出码 0。
- 已据此**锁定资产池**：DeReFusion 仓 `reports/evidence_closure/23_c1_preregistration.md` §8（含锁定提交与决策点/调整口径/无排除项）。
- 已回复 geng：`thinkbook-lobster/048-to-geng-t004-accepted.md`；**T005 暂不派发**（C1 跑完前不给新任务）。

## 派发文件

| 文件 | 用途 |
|---|---|
| `thinkbook-lobster/048-to-geng-t004-accepted.md` | T004 受理（独立校验 20/20 通过）+ 锁定说明（2026-09-14） |
| `thinkbook-lobster/049-T005-c1-panel.md` | **T005 派发（C1 面板执行，含离线运行要求）** |
| `thinkbook-lobster/050-to-geng-t005-status-accepted.md` | T005 状态受理 + 三条接收要求（2026-09-14） |
| `thinkbook-lobster/051-to-geng-post-panel-roles.md` | T005 面板完成后的角色与边界（含盲复算安排，2026-09-14） |
| `thinkbook-lobster/052-to-geng-decisions-on-012.md` | **`012` 六问裁定 + 预授权（此后不再等批复）**（2026-09-14） |
| `thinkbook-lobster/053-to-geng-batch01-verified-and-commit-hash.md` | 首批 2 run 整批验收通过 + Q5 选 A + 索取冻结版本 commit hash（2026-09-14） |
| `thinkbook-lobster/054-to-geng-decisions-014-015-016.md` | `014` 受理（首批链路闭合）+ `015` 记功 + `016` 裁定：**批准受控 3 lane（线程不改）与 A/B 提前**（2026-09-14） |
| `thinkbook-lobster/055-to-geng-approve-liveness-fix.md` | **批准判活口径修正（以产物推进为准）** + 重跑安排 + 对 `018` 确认（2026-09-16） |
| `thinkbook-lobster/058-to-geng-t005-accepted-handoff-complete.md` | **T005 完成受理**（我方全量验收 120/120 通过）+ 交付物组装完毕 + A/B 放行（2026-09-18） |
| 文件 | 用途 |
|---|---|
| `thinkbook-lobster/041-T001-ablation.md` | T001 派发（保留存档） |
| `thinkbook-lobster/042-to-geng-t001-status.md` | T001 状态询问 |
| `thinkbook-lobster/043-to-geng-t001-evidence-and-alert.md` | T001 证据收取 + 告警逻辑答复（2026-09-13） |
| `thinkbook-lobster/044-T002-egress-test.md` | T002 派发 |
| `thinkbook-lobster/045-T003-f1-recompute.md` | T003 派发 |
| `thinkbook-lobster/046-to-geng-t002-t003-accepted.md` | T002/T003 受理 + 编号规则答复（2026-09-14） |
| `thinkbook-lobster/047-T004-cohort-acquisition.md` | **T004 派发（C1 关键路径）** |

## 派活暂停与恢复记录

### 暂停（2026-09-12 08:45 主人指示）

- 主人指示：**先不给 geng 那台机器分配任务**；`T001` 转出在途，不派 `T002`。

### 恢复（2026-09-14 13:06 主人指示："都办了"）

- 恢复对外派活，并要求同时发布 `T002` 与 `T003`；**规程第 3 条例外**已记录（两者零风险、互不依赖；`T001` 为"取消"非"未完成"）。
- `T002`/`T003` 回执已收到并受理 → 按规程第 3 条核完上一轮，**已发布 `T004`**。

## 下一个可用编号

**T006**（编号不回收；下一轮若派活从 T006 起；当前下一步是分析与盲复算，不派新任务）

### T005 收官（2026-09-18）：120/120，我方验收全过

- **最终状态**：目标 120；`ok=120`、`fail=0`、`stall=0`；**DeReFusion 60 / revin-DLinear 60**；seed 各 40。
- **我方独立验收**：逐 run 协议一致 **120/120**；`.npy` 哈希 vs manifest **120/120**；metrics 六值 **120/120**；网格覆盖 **120/120（缺失 0、多余 0）**；五项附加审计 **no integrity problems found**。
- **交接产出**：逐文件 SHA-256 清单 **610 个文件**（`reproduction/results/t005_intake/final120.inventory.csv`）+ 交接回执（`executor_reported_commit=d17822f`、`runs_seen/passing=120/120`）。
- **执行方声明（`007`）**：数据闸门 20/20；命令行 120/120 且**线程全程 14**；副本=manifest **240/240**；**本机原件=manifest 240/240（0 缺失）**、无 WARN；`ingested_orphan=1` 共 4 行。
- **误杀事件收尾（`020`/`055`）**：stall 行 89、不同单元 **39**、修正后 **39/39 全部跑成**（stall 行臂分布 DeReFusion 6 : revin 83）；判活修正生效 **2026-09-16 17:12**，此后 **kill 台账为空（零 kill）**。
- **另记**：`057` 一次休眠事故（~2h38m 零算力，已修）；总 run 墙钟 5014.4 min ≈ 83.6 h；战役窗口约 78 h（含三类非计算损耗）。
- **下一步**：交付集交**盲第三方复算**（规格 `24a`，由主人/Codex 安排）；A/B 已放行（机器空闲，结果不入 C1 证据链）；`T006` 不派。

- **进度 87/120**（未完成）：`ok=54`、`stall=33`。**33 个 stall 全部在基线臂 `revin-DLinear`**（该臂仅 10 ok）；实验臂 `DeReFusion` **44/44 全 ok、零 stall**。
- **原因（`020`）**：判活用的是「进程树 CPU 增量」（`Get-TreeCpu`），对**小模型路径失真** → 12 分钟判死后杀树；被杀单元留有 checkpoint（当时正在训练）→ **误杀**。继续跑则**基线臂永远跑不完**，C1 对照组会残缺 ~40%。
- **我方裁定（`055`）**：**批准把判活改为“以产物推进为准”（checkpoint/results 写入）**，限定：只改“何时杀树”、**不得取消 stall 检测**（新判据 = 产物无推进 **且** CPU 无增长，持续 N 分钟）、逐次记录 kill 事件、**幂等重跑 33 个 stall 行 + 跑完剩余 33 个**、已产出的 54 行与 `.npy` 一字不改。
- **3 lane 已按 `054` §3.1 熔断回退 2 lane**（两次 stall 触发条件）；geng 自述该窗口实际并发为 **4 路**（2-lane 时代孤儿 + 新发起）→ 测的是超订，**3 lane 的问题交给 A/B**（仍在 120 完成后）。
- **我方验收**：已交付 **54/54 全通过**（协议逐项 + `.npy` 哈希 + metrics 六值）；另 5 项附加审计无问题；已产出**逐文件 SHA-256 清单（278 个文件）**+ 交接回执（`executor_reported_commit=d17822f`）。那 33 个 FAIL = stall 行无产物（跑中被杀）。
- **文件**：`BATCH-2021-DONE.md`（20 ok/20 stall）、`BATCH-2022-DONE.md`（24 ok/16 stall）；`007` 最终回执尚未出。
- **待补**：判活修正生效后的重跑与补跑（约 66 个 run，~1.5–2 天）；`007` 需写清逐 run 最终状态 + 重跑前后对照 + 修正生效时点 + 两臂完成数。

### T005 执行状态（geng `008-T005-status.md`，已受理）

- **数据硬闸门 20/20 通过**：其本机 `DeReFusion/dataset/` 副本逐一重算 SHA-256 与锁定表（`23` §8）比对一致，行数一致，未改既有数据。
- **已开跑**：13:36 两路（LANE0 `AAPL_DeReFusion_seed2021`、LANE1 `HSI_DeReFusion_seed2021`）；协议逐项照抄；2 lane 上限；幂等跳过；按**进程树 CPU 时间**判活 stall；单 run 失败不中断；**离线不依赖网络**。
- **回传**：常驻检查点每 10 分钟合 manifest，每满 40 run 或每 6h 自动 push；产物布局 `T005-c1/<seed>/<TAG>_<MODEL>/`。
- 已关本机 AC 睡眠/息屏（防长跑被打断）。
- 我方已回 `050`：受理 + 三条要求（`.npy` 逐字节保留；最终回执含 dataset 哈希校验结果与逐 run 命令行；断点幂等续跑不得重头）。
- 我方接收端已就绪：`reproduction/analysis/c1_artifacts_intake.py`（验 `.npy` 哈希 + 命令行逐项对协议 + metrics 六值可解析，通过才落到管线规范名目录）。
- **面板完成后 geng 的角色**（`051`）：(a) 传输完整性确认——给出其**本机原件** `pred/true` 的 SHA-256（全量或每资产每模型≥1 种子），闭合“仓库文件 = 本机原件”这一段；(b) **可选**的交互效应交叉复核（**不算盲复算**，因其为执行方）。
- **headline 统计量的盲复算**由**第三方**承担（规格 `24a`，owner=操作者安排）；执行方与分析方均被排除。
- **`012` 六问已裁定**（`052`，2026-09-14）：Q1 并发**维持 2 lane**（否决放宽）；Q2 线程数**延下战役**；Q3 DataLoader **延下战役**；Q4 电源无异议、**Defender 排除建议不做**（主人拍板）；Q5 **场外调优 A/B 批准**（附四条条件）；Q6 技能无需我定。
- **`009` 断网/无人回复预案：接受**；并补了预授权（自行补推、失败 3 次记 fail 继续、可自主重启 lane）。geng 已被告知：**此后不需等批复**。
- **首批真实数据（2026-09-14 14:56 到达）**：`T005-c1/2021/{AAPL,HSI}_DeReFusion/`（metrics+pred+true+command+log_tail）+ `per_run_manifest.csv` + lane CSVs。**整批校验通过 2/2**（协议逐项 / `.npy` 哈希 / 指标六值 / 日志一致），退出码 0；两行 `ingested_orphan=1`（先完成、后被摄入），`wall_clock_min` 为估算口径（已接受）。
- **批次交接机制已上线**：某 seed 的 40 run 全部落库时自动写 `T005-c1/BATCH-<seed>-DONE.md` 并强制 push（先探网；断网本地保留、每 10 分钟重试）。
- **待 geng 补件**：执行所用 DeReFusion 冻结版本 **commit hash**（验收器 `--inventory` 强制要求），以及"manifest 哈希取自本机原件且在传输前计算"的声明。

### 首批链路已闭合（2026-09-14 15:2x）

- geng `014` 交了**执行版本 `d17822f`**（已在仓库核对存在）+ **哈希来源声明**（改为先对本机原件算哈希、再校验推送副本）+ **6/6 字节级等价证明**（本机原件 = 推送件）。
- 我方据此补齐：**逐文件 SHA-256 清单**（13 个文件）+ **交接回执**（含 `executor_reported_commit=d17822f`），位于 `reproduction/results/t005_intake/`。验收 2/2 通过。
- geng `015`：稳定性演练**自查出第一轮"5/5 PASS"为假阳性**，真实结果 **B 实为 FAIL**（看门狗用全局 run.py 计数做重启门槛→双 lane 常驻 4 进程→恢复被永久拦住）；已修并复验**杀 lane0 → 29.1s 拉起**。（该类缺陷会造成整批静默停摆，已记功。）
- geng `016`：主人指出"CPU 利用率太低"（实测 14 核总体 53.3%，cpu12/cpu13 仅 0.9%/0.3%）。**我方裁定（`054`）**：① **批准受控 3 lane**（仅当前 seed 批次，**每进程线程保持 14 不变**以保数值一致；插桩逐 run 墙钟+stall；出现 stall 或墙钟恶化 >10% **立即回退**）；② **批准 Q5 调优 A/B 提前**（对比 2×14 / 2×7 / 3×5 / 3×4，报 runs-hour、stall、每核分布；熔断条件不变；A/B 数字不进 C1 证据链）；③ L2/L3 维持延后。
