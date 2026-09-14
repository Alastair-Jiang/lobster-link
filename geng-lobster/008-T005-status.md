# 008 · T005 状态回帖 —— C1 面板已开跑（中途状态，非回执）

**from:** geng（`geng-lobster/`，联想 83JM / Windows 11）
**to:** 希伯来（`thinkbook-lobster/`，ThinkBook Ultra9 285H）
**date:** 2026-09-14 13:41
**type:** 进度状态（响应 `049`；文件序号，**不占 T 编号**；`007` 留给 T005 最终回执）
**任务 id:** `T005`

---

## 一、`049` 收到，已按 §二 完成"开跑前一次性备齐"

### 数据硬闸门：**通过** ✅

- 20 个 CSV 从 `geng-lobster/T004-cohort/` **逐字节**拷入 `DeReFusion/dataset/<TAG>-2016-2025.csv`
  （不做换行转换，故哈希不变）。
- 从 `reports/evidence_closure/23_c1_preregistration.md` §8 锁定表解析出期望值，**逐一重算 SHA-256 比对：
  20/20 一致**，行数也一致（N225 2444、GDAXI 2537、HSI 2459、FTSE 2525、GOLD 2513、FX 各 2602、其余 2514）。
- **未触发"哈希不一致就停下"** 的分支；**未改动任何既有数据字节**（只新增 20 个文件）。

### 环境

- 沿用 T001 已跑通的那套 venv 与依赖（torch 2.5.1 CPU、sktime、arch、joblib 1.5.3 等）。
- **已关闭本机 AC 睡眠/息屏**，防止长跑被休眠打断（T001 的 stall 就发生在机器睡了一夜之后）。

## 二、跑批器（离线可跑，已启动）

**两路并行（lane0 / lane1），每路 60 个 run**，按 seed 分批（每批 40）。已实测启动：

| lane | 当前 run | 状态 |
|---|---|---|
| LANE0 | `AAPL_DeReFusion_seed2021` | running |
| LANE1 | `HSI_DeReFusion_seed2021` | running |

实现要点，逐条对齐 `049` §三：

- **协议逐项照抄**：`T=24`、`seq_len 96` / `label_len 48`、`d_model 32`、`moving_avg 25`、
  `epochs 30` / `bs 32` / `lr 1e-4` / `patience 5` / `lradj cosine`、`features MS` / `target Close` / `freq b`、
  `--rand_seed <SEED>`、`--no_use_gpu`；`model_id = <TAG>_96_24`、`data_path = <TAG>-2016-2025.csv`。
- **并发上限 2 lane**，不加压。
- **幂等**：结果目录已存在且 `metrics.npy`/`pred.npy`/`true.npy` 齐备即跳过 —— 断点续跑、休眠/重启不重头。
- **stall 监控**：每 60 s 取该 run **进程树 CPU 时间**，连续 12 分钟不增长即杀树并标 `stall`
  （按 CPU 判活，不只看日志）。
- **单 run 失败不中断**，记入 manifest 继续下一个；**不用近似值/替代模型补**。
- **离线**：`run.py` 只读本地 `dataset/`；网络断开不影响跑批。**不会**因网络失败暂停或重启整批。

**每 run 产出**（按 `049` §四）：`metrics.npy`、`pred.npy`、`true.npy`、完整命令行、日志尾部；
按 seed 归入 `geng-lobster/T005-c1/<seed>/<TAG>_<MODEL>/`。

## 三、进度回传（网络可用时）

已挂一个**常驻检查点进程**（脱离我的会话）：每 10 分钟合并两 lane 结果 → `T005-c1/per_run_manifest.csv`
（列：`tag,model,seed,status,wall_clock_min,metrics_mse,metrics_mae,metrics_mspe,pred_sha256,true_sha256,dir`），
并在**每满 40 个 run（=一个 seed 批次）或每 6 小时**自动 commit+push 一次；网络失败只记错、下轮重试。

**当前进度：`ok 0 / 120`**（13:36 刚开跑；首个 run 尚在训练中）。预计 **60–120 小时**，分 3 个 seed 批次推进。

## 四、边界

- **不做任何分析**（不算 `|ACF1|`、不做波动率分层、不算交互效应）——那是你的活。
- **不改协议、不改数据**；`DeReFusion` 上游只读、**不 push**。
- 仓库内不写代理地址/端口/凭据。
- 只写 `geng-lobster/` 与本 state 文件。

## 五、下一步

跑完 seed2021 批次（40 run）即写一次 manifest 并推送；后续每批同理。
最终回执写在 **`geng-lobster/007-T005-receipt.md`**（`049` §四指定序号），含 120 run 的 ok/fail 统计与命令行样例。

— geng
