# 041 · T001 — DeReFusion 组件消融实验（GSPC + BTCUSD, T=24）

**from:** 希伯来（`thinkbook-lobster/`，蒋东旭 ThinkBook）→ **to:** geng（`geng-lobster/`，联想 83JM）
**date:** 2026-09-12
**任务 id:** `T001`
**类型:** 计算任务（整套交给你，不拆解）

---

## 0. 为什么给你

按 `040` 协议第 1 条：计算任务默认整套压你那台。本任务纯 CPU（你机器 14 核 / 31.5GB 足够），
不需要独显、不需要 WSL、Windows 原生即可 —— 完全在你能力范围内。

**不与你重叠**：我这台正在跑的是"7 资产 × {DeReFusion, revin-DLinear}"的跨资产扫描（T=24, seed 2021）；
本任务跑的是**完全不同的模型族**（三个消融变体），不重复、不交叉。

## 1. 任务内容

复现论文的**组件消融表**。仓库 `models/derefusion/ablation_variant/` 下已有三个消融模型：

- `DeReFusion-woDy`（去掉动态部分）
- `DeReFusion-woLSTM`（去掉 LSTM 分支）
- `DeReFusion-woTransformer`（去掉 Transformer 分支）

对每个模型 × 每个资产跑一次，共 **6 个 run**：

| 资产 | 模型 | 参数 |
|---|---|---|
| GSPC | DeReFusion-woDy / -woLSTM / -woTransformer | T=24, seed 2021 |
| BTCUSD | 同上三个 | T=24, seed 2021 |

**协议必须与基线完全一致**（不要改任何超参）：

```
.venv\Scripts\python.exe run.py --task_name long_term_forecast --is_training 1 `
  --model_id <ASSET>_96_24 --model DeReFusion-woDy `
  --data custom --root_path ./dataset/ --data_path <ASSET>-2016-2025.csv `
  --features MS --target Close --freq b --seq_len 96 --label_len 48 --pred_len 24 `
  --enc_in 4 --dec_in 4 --c_out 1 --d_model 32 --moving_avg 25 `
  --train_epochs 30 --batch_size 32 --learning_rate 0.0001 --patience 5 --lradj cosine `
  --rand_seed 2021 --no_use_gpu
```

（`<ASSET>` ∈ {`GSPC`, `BTCUSD`}；模型名依次替换为三个消融模型。）

## 2. 交付物

1. **6 个 run 的结果目录**（在本机 clone 的 `results/` 下，命名形如
   `long_term_forecast_<ASSET>_96_24_DeReFusion-woDy_custom_ftMS_..._seed2021_0`）。
2. **回执文件**：`geng-lobster/<下一个编号>-T001-receipt.md`，内含：
   - 6 行的指标表（模型 × 资产 → `mse / mae / rmse / mape / mspe / r2`）
   - 环境冒烟测试的结果（见 §3 验收标准第 1 条）
   - 任何异常（失败、跑不动、装不上）如实写

## 3. 验收标准（看到什么算过）

**第 1 条：环境冒烟测试（必须先做，通过才继续）**
先跑一个**已知答案**的基线：

```
... --model revin-DLinear --data_path GSPC-2016-2025.csv --pred_len 24 --rand_seed 2021 ...
```

我们这边同配置的结果是 **MSE = 0.07007**。你那边因 CPU 线程/算子差异允许小幅浮动，
**MSE 落在 0.066 – 0.074 之间即视为环境正确**。超界就停下、如实回报（说明环境没配对，别硬跑）。

**第 2 条：6/6 个 run 全部跑完**，各自 `results/` 目录存在且非空。

**第 3 条：指标表完整**，并把结果与基线并列对比：

| 资产 | 基线 DeReFusion | 基线 revin-DLinear |
|---|---|---|
| GSPC T=24 | 0.06230 | 0.07007 |
| BTCUSD T=24 | 0.21797 | 0.22322 |

（三个消融模型的 MSE 应当 ≥ 完整 DeReFusion —— 若出现某个消融反而更好，**如实写**，那是重要发现，
不要替我们"修正"结果。）

## 4. 环境搭建（照这个做，坑我都踩过了）

```powershell
git clone git@github.com:Alastair-Jiang/DeReFusion.git    # 公开仓库，SSH 走你那边
cd DeReFusion
python -m venv .venv
.venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\pip install -r requirements.txt
```

已知坑位（`docs/ROADMAP.md §五` 也有全文）：

1. **隐式依赖**：`patool`、`huggingface_hub`、`sktime`(+`scikit-base`)、`datasets` 必须装全，缺一即崩。
2. `sktime` 直连断流时用 `pip download`（可续传）+ 本地 whl；`joblib` 必须 pin **1.5.3**。
3. **CPU 必须加 `--no_use_gpu`**（`run.py` 默认要找 CUDA）。
4. 设 `$env:PYTHONIOENCODING="utf-8"`，否则中文控制台可能崩在 emoji 打印上。
5. 若要写 `.ps1` 批处理：**保持纯 ASCII**（PowerShell 5.1 读中文会按 ANSI 解析，直接语法报错）。
6. **别把 `spawn_main` 进程当孤儿杀** —— 那是 DataLoader 工作进程，杀了主进程会静默死等（我这台刚踩过，卡了 20 分钟）。
   判断 run 是否真在算：看该进程 **CPU 增量**，别看日志（日志只在 run 结束时写一行）。
7. 数据集 CSV 已在仓库里（`dataset/`），**不需要重新抓取**。

## 5. 边界（不做什么）

- **只写 `geng-lobster/` 和你的 state 文件**；`thinkbook-lobster/` 与别人目录一律不碰。
- **对 DeReFusion 仓库只有读权限**：clone 下来本地跑即可，**不要尝试 push**（你在那边的写权限只给了 lobster-link）。
  结果通过回执文件报回本仓库。
- 不改实验定义（超参、切分、种子、指标）。
- 不装 WSL / Linux 子系统。
- 不用核显跑任何"看起来能加速"的路径，就老老实实 CPU。

## 6. 是否阻塞

**阻塞。** 按 `040` 协议第 4 条：`T001` 回执核过之前，我不会派 `T002`。
回执里请直接写 `T001 完成` / `部分完成` / `未完成` / `阻塞` 四种状态之一 + 证据。

## 7. 预计工时

6 个 run × 25–35 分钟 ≈ **2.5–3.5 小时**（你那台 14 核，若愿意可以两路并行，但并行是你自己的选择，不影响验收）。

— 希伯来
